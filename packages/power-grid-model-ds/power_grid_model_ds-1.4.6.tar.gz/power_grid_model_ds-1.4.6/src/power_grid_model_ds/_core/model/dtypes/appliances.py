# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Appliance data types"""

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.dtypes.id import Id


class Appliance(Id):
    """Appliance data type"""

    node: NDArray[np.int32]  # id of the coupled node
    status: NDArray[np.int8]  # connection status to the node


class Source(Appliance):
    """Source data type"""

    u_ref: NDArray[np.float64]  # reference voltage


class SymLoad(Appliance):
    """SymLoad data type"""

    type: NDArray[np.int8]  # load type
    p_specified: NDArray[np.float64]  # specified active power
    q_specified: NDArray[np.float64]  # specified reactive power


class SymGen(Appliance):
    """SymGen data type"""

    type: NDArray[np.int_]  # load type
    p_specified: NDArray[np.float64]  # specified active power
    q_specified: NDArray[np.float64]  # specified reactive power
