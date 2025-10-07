# Copyright © 2025 Oracle and/or its affiliates.
#
# This software is under the Universal Permissive License
# (UPL) 1.0 (LICENSE-UPL or https://oss.oracle.com/licenses/upl) or Apache License
# 2.0 (LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0), at your option.

from .spanprocessor import OtelBatchSpanProcessor, OtelSimpleSpanProcessor

__all__ = [
    "OtelSimpleSpanProcessor",
    "OtelBatchSpanProcessor",
]
