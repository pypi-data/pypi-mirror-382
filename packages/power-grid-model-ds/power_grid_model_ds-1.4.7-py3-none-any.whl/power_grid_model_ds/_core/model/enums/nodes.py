# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Enums for Nodes"""

from enum import IntEnum


class NodeType(IntEnum):
    """Node Types
    Nodes located within a substation, are marked as Substation nodes.
    """

    UNSPECIFIED = 0
    SUBSTATION_NODE = 1
