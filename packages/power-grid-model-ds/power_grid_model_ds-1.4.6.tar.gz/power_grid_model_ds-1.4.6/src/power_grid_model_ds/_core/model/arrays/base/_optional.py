# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Optional dependencies for the arrays module."""

try:
    # pylint: disable=unused-import
    import pandas
except ImportError:
    pandas = None
