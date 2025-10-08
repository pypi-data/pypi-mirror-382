# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""Wrapper for the Interior Point OPTimizer (IPOPT)."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Final

from cyipopt import minimize_ipopt
from gemseo.algos.design_space_utils import get_value_and_bounds
from gemseo.algos.opt.base_optimization_library import BaseOptimizationLibrary
from gemseo.algos.opt.base_optimization_library import OptimizationAlgorithmDescription
from gemseo.algos.opt.base_optimizer_settings import BaseOptimizerSettings
from numpy import isfinite
from numpy import real

from gemseo_ipopt.settings import IPOPT_Settings

if TYPE_CHECKING:
    from gemseo.algos.optimization_problem import OptimizationProblem


@dataclass
class IPOptAlgorithmDescription(OptimizationAlgorithmDescription):
    """The description of the Interior Point Optimizer."""

    library_name: str = "IPOPT"

    Settings: type[IPOPT_Settings] = IPOPT_Settings
    """The option validation model for the Interior Point Optimizer."""


class IPOpt(BaseOptimizationLibrary):
    """The Interior Point optimizer."""

    ALGORITHM_INFOS: ClassVar[dict[str, IPOptAlgorithmDescription]] = {
        "IPOPT": IPOptAlgorithmDescription(
            algorithm_name="IPOPT",
            handle_equality_constraints=True,
            handle_inequality_constraints=True,
            internal_algorithm_name="Ipopt",
            description="Interior Point Optimizer",
            positive_constraints=True,
            Settings=IPOPT_Settings,
        )
    }

    __USER_PROVIDED_OPTIONS: Final[str] = "user_provided_options"

    def _run(self, problem: OptimizationProblem, **settings: Any) -> tuple[str, Any]:
        x_0, l_b, u_b = get_value_and_bounds(problem.design_space, self._normalize_ds)

        l_b = [val if isfinite(val) else None for val in l_b]
        u_b = [val if isfinite(val) else None for val in u_b]
        bounds = list(zip(l_b, u_b, strict=False))

        constraints = [
            {
                "type": constraint.f_type,
                "fun": constraint.evaluate,
                "jac": constraint.jac,
            }
            for constraint in self._get_right_sign_constraints(problem)
        ]

        user_provided_options = settings[self.__USER_PROVIDED_OPTIONS]

        options_ = self._filter_settings(settings, BaseOptimizerSettings)

        for key, value in list(options_.items()):
            if self.ALGORITHM_INFOS["IPOPT"].Settings.__fields__[key].default == value:
                options_.pop(key)

        if user_provided_options:
            options_.pop(self.__USER_PROVIDED_OPTIONS)
            options_.update(user_provided_options)

        options_.update(self.ALGORITHM_INFOS["IPOPT"].Settings._forced_settings)

        opt_result = minimize_ipopt(
            fun=lambda x: real(problem.objective.evaluate(x)),
            x0=x_0,
            method=None,
            jac=problem.objective.jac,
            bounds=bounds,
            constraints=constraints,
            options=options_,
            tol=sys.float_info.epsilon,
        )

        return opt_result.message, opt_result.status
