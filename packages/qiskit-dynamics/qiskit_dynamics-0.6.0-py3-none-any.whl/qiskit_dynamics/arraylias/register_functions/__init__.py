# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""
Register custom functions using alias
"""

from .asarray import register_asarray
from .matmul import register_matmul
from .rmatmul import register_rmatmul
from .multiply import register_multiply
from .linear_combo import register_linear_combo
from .conjugate import register_conjugate
from .transpose import register_transpose
