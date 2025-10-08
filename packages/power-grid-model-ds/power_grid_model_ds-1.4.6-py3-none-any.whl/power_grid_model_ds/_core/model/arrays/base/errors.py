# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""A collection of errors"""


class ArrayDefinitionError(Exception):
    """Raised when an array is defined incorrectly"""


class RecordDoesNotExist(IndexError):
    """Raised when a record is accessed that does not exist"""


class MultipleRecordsReturned(IndexError):
    """Raised when unexpectedly, multiple records are found."""
