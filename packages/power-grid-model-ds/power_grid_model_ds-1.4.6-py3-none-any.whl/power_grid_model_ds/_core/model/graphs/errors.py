# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


class GraphError(Exception):
    """Raised when there is an error in the graph"""


class MissingNodeError(GraphError):
    """Raised when a node is missing"""


class MissingBranchError(GraphError):
    """Raised when a branch is missing"""


class NoPathBetweenNodes(GraphError):
    """Raised when there is no path between two nodes"""
