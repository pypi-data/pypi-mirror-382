# Copyright © 2025 Oracle and/or its affiliates.
#
# This software is under the Universal Permissive License
# (UPL) 1.0 (LICENSE-UPL or https://oss.oracle.com/licenses/upl) or Apache License
# 2.0 (LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0), at your option.

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from wayflowcore._metadata import MetadataType
from wayflowcore.executors._flowexecutor import FlowConversationExecutor
from wayflowcore.property import AnyProperty, Property, _format_default_value
from wayflowcore.steps import FlowExecutionStep
from wayflowcore.steps.step import Step, StepExecutionStatus, StepResult

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from wayflowcore import Flow, Tool
    from wayflowcore.executors._flowconversation import FlowConversation


class CatchExceptionStep(Step):
    """Executes a ``Flow`` inside a step and catches specific potential exceptions.
    If no exception is caught, it will transition to the branches of its subflow.
    If an exception is caught, it will transition to some specific exception branch has configured in this step.
    """

    EXCEPTION_NAME_OUTPUT_NAME = "exception_name"
    """str: Variable containing the name of the caught exception."""

    EXCEPTION_PAYLOAD_OUTPUT_NAME = "exception_payload_name"
    """str: Variable containing the exception payload. Does not contain any higher-level stacktrace information than the wayflowcore stacktraces."""

    DEFAULT_EXCEPTION_BRANCH = "default_exception_branch"
    """str: Name of the branch where the step will transition if ``catch_all_exceptions`` is ``True`` and an exception was caught."""

    def __init__(
        self,
        flow: "Flow",
        except_on: Optional[Dict[str, str]] = None,
        catch_all_exceptions: bool = False,
        input_descriptors: Optional[List[Property]] = None,
        output_descriptors: Optional[List[Property]] = None,
        input_mapping: Optional[Dict[str, str]] = None,
        output_mapping: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        __metadata_info__: Optional[MetadataType] = None,
    ):
        """
        Note
        ----

        A step has input and output descriptors, describing what values the step requires to run and what values it produces.

        **Input descriptors**

        The input descriptors of this step are the same as the input descriptors of the ``flow`` that this step will run.
        See :ref:`Flow <Flow>` to learn more about how flow inputs are resolved.

        **Output descriptors**

        The outputs descriptors of this step are the same as the outputs descriptors of the ``flow`` that this step will run.
        See :ref:`Flow <Flow>` to learn more about how flow outputs are resolved.

        This step also has two additional output descriptors:

        * ``CatchExceptionStep.EXCEPTION_NAME_OUTPUT_NAME``: ``StringProperty()``, the name of the caught exception if any.
        * ``CatchExceptionStep.EXCEPTION_PAYLOAD_OUTPUT_NAME``: ``StringProperty()``, the payload of the caught exception if any.

        **Branches**

        This step can have several next steps depending on how its execution goes. It has the same
        next branches as the ``flow`` it runs, plus some additional branches:

        * all the values of the ``except_on`` mapping argument, which is taken if a particular exception is caught
        * the ``CatchExceptionStep.DEFAULT_EXCEPTION_BRANCH`` in case ``catch_all_exceptions`` is ``True`` and another exception is caught.


        Parameters
        ----------
        flow:
            ``Flow`` to execute and catch errors from
        except_on:
            Dictionary mapping error class names to the branch name they should transition to.
        catch_all_exceptions:
            Whether to catch any error or just the ones present in the ``except_on`` parameter.
            If ``True``, the step will transition to ``CatchExceptionStep.DEFAULT_EXCEPTION_BRANCH``
        input_descriptors:
            Input descriptors of the step. ``None`` means the step will resolve the input descriptors automatically using its static configuration in a best effort manner.

        output_descriptors:
            Output descriptors of the step. ``None`` means the step will resolve them automatically using its static
            configuration in a best effort manner.

        name:
            Name of the step.

        input_mapping:
            Mapping between the name of the inputs this step expects and the name to get it from in the conversation input/output dictionary.

        output_mapping:
            Mapping between the name of the outputs this step expects and the name to get it from in the conversation input/output dictionary.

        """
        super().__init__(
            llm=flow._get_llms()[0] if flow._get_llms() else None,
            step_static_configuration=dict(
                flow=flow, except_on=except_on, catch_all_exceptions=catch_all_exceptions
            ),
            input_mapping=input_mapping,
            output_mapping=output_mapping,
            input_descriptors=input_descriptors,
            output_descriptors=output_descriptors,
            name=name,
            __metadata_info__=__metadata_info__,
        )

        self.flow = flow
        self.except_on = except_on or {}
        self.catch_all_exceptions = catch_all_exceptions
        self.flow_step = FlowExecutionStep(flow=flow)

    def sub_flow(self) -> "Flow":
        return self.flow

    @classmethod
    def _get_step_specific_static_configuration_descriptors(
        cls,
    ) -> Dict[str, type]:
        from wayflowcore.flow import Flow

        return {
            "flow": Flow,
            "except_on": Optional[Dict[str, str]],  # type: ignore
            "catch_all_exceptions": bool,
        }

    @classmethod
    def _compute_step_specific_input_descriptors_from_static_config(
        cls,
        flow: "Flow",
        except_on: Optional[Dict[str, str]],
        catch_all_exceptions: bool,
    ) -> List[Property]:
        return FlowExecutionStep._compute_input_descriptors_from_static_config(
            flow=flow,
            input_mapping={},
            output_mapping={},
        )

    @classmethod
    def _compute_step_specific_output_descriptors_from_static_config(
        cls,
        flow: "Flow",
        except_on: Optional[Dict[str, str]],
        catch_all_exceptions: bool,
    ) -> List[Property]:
        flow_output_descriptors = (
            FlowExecutionStep._compute_step_specific_output_descriptors_from_static_config(
                flow=flow,
            )
        )
        return [property_.copy() for property_ in flow_output_descriptors] + [
            AnyProperty(
                name=cls.EXCEPTION_NAME_OUTPUT_NAME,
                description="Name of the exception that was caught",
                default_value="",
            ),
            AnyProperty(
                name=cls.EXCEPTION_PAYLOAD_OUTPUT_NAME,
                description="Payload of the exception that was caught",
                default_value="",
            ),
        ]

    @classmethod
    def _compute_internal_branches_from_static_config(
        cls,
        flow: "Flow",
        except_on: Optional[Dict[str, str]],
        catch_all_exceptions: bool,
    ) -> List[str]:
        branches = FlowExecutionStep._compute_internal_branches_from_static_config(
            flow=flow,
        )
        if catch_all_exceptions:
            branches.append(cls.DEFAULT_EXCEPTION_BRANCH)
        if except_on is not None:
            branches.extend(except_on.values())
        return branches

    @property
    def might_yield(self) -> bool:
        """
        Indicates if the step might yield back to the user.
        It depends on the sub-flow we are executing
        """
        return self.flow.might_yield

    async def _invoke_step_async(
        self, inputs: Dict[str, Any], conversation: "FlowConversation"
    ) -> StepResult:

        try:
            step_result = await self.flow_step.invoke_async(
                inputs=inputs,
                conversation=conversation,
            )

            if step_result.step_type == StepExecutionStatus.PASSTHROUGH:
                step_result.outputs.update(
                    {self.EXCEPTION_NAME_OUTPUT_NAME: "", self.EXCEPTION_PAYLOAD_OUTPUT_NAME: ""}
                )
            return step_result

        except Exception as e:

            logger.debug("CatchExceptionStep caught error: %s", str(e))

            caught_exception_name = e.__class__.__name__

            branch_name = None
            for exception_name, exception_next_branch in self.except_on.items():
                if exception_name == caught_exception_name:
                    branch_name = exception_next_branch

            if branch_name is None and self.catch_all_exceptions:
                branch_name = self.DEFAULT_EXCEPTION_BRANCH

            if branch_name is None:
                raise e

            logger.debug("CatchExceptionStep will continue with branch: %s", branch_name)

            # cleanup failed conversation
            FlowConversationExecutor().cleanup_sub_conversation(conversation.state, self.flow_step)

            outputs = {
                self.EXCEPTION_NAME_OUTPUT_NAME: caught_exception_name,
                self.EXCEPTION_PAYLOAD_OUTPUT_NAME: self._format_payload(e),
                **{
                    # if we put the subflow outputs as output of this step, we need to make sure that even if
                    # an exception is raised (and the subflow maybe didn't produce all values) we still
                    # return all outputs (a default value for the ones that were not produced
                    value_name: _format_default_value(value_description)
                    for value_name, value_description in self.flow.output_descriptors_dict.items()
                },
            }

            return StepResult(
                outputs=outputs,
                branch_name=branch_name,
            )

    @staticmethod
    def _format_payload(e: Exception) -> str:
        """For now, just extracts the error message"""
        return str(e)

    def _referenced_tools_dict_inner(
        self, recursive: bool, visited_set: Set[str]
    ) -> Dict[str, "Tool"]:
        all_tools = {}

        if recursive:
            all_tools.update(
                self.flow._referenced_tools_dict(recursive=True, visited_set=visited_set)
            )

        return all_tools
