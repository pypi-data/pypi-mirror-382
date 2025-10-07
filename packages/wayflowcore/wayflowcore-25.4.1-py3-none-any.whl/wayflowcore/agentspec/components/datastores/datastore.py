# Copyright © 2025 Oracle and/or its affiliates.
#
# This software is under the Universal Permissive License
# (UPL) 1.0 (LICENSE-UPL or https://oss.oracle.com/licenses/upl) or Apache License
# 2.0 (LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0), at your option.

from pyagentspec import Component


class PluginDatastore(Component, abstract=True):
    """Store and perform basic manipulations on collections of entities of various types.

    Provides an interface for listing, creating, deleting and updating collections.
    It also provides a way of describing the entities in this datastore.
    """
