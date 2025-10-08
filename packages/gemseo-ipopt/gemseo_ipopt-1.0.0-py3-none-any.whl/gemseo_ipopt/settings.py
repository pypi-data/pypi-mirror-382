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

# Copyright (C) 2005, 2009 International Business Machines and others.
# All Rights Reserved.
# This code is published under the Eclipse Public License.
#
# Authors:  Michael Hagemann               Univ of Basel 2005-10-28
#               original version (based on MA27TSolverInterface.cpp)

"""Settings for the Interior Point OPTimizer (IPOPT)."""

# These settings were recovered by parsing the IPOPT options
# documentation found in (https://coin-or.github.io/Ipopt/LICENSE.html)
from __future__ import annotations

from typing import Any
from typing import ClassVar

from gemseo.algos.opt.base_optimizer_settings import BaseOptimizerSettings
from pydantic import Field
from pydantic import NonNegativeFloat
from pydantic import NonNegativeInt
from pydantic import PositiveFloat
from strenum import StrEnum


class YesOrNoOptionValues(StrEnum):
    """The yes or no string options values."""

    YES = "yes"
    NO = "no"


class PrintOptionsModeValues(StrEnum):
    """The print_options_mode option values."""

    TEXT = "text"
    LATEX = "latex"
    DOXYGEN = "doxygen"


class InfPrOutputValues(StrEnum):
    """The inf_pr_output option values."""

    INTERNAL = "internal"
    ORIGINAL = "original"


class FixedVariableTreatmentValues(StrEnum):
    """The fixed_variable_treatment option values."""

    MAKE_PARAMETER = "make_parameter"
    MAKE_PARAMETER_NODUAL = "make_parameter_nodual"
    MAKE_CONSTRAINT = "make_constraint"
    RELAX_BOUNDS = "relax_bounds"


class NlpScalingMethodValues(StrEnum):
    """The nlp_scaling_method option values."""

    GRADIENT_BASED = "gradient-based"
    NONE = "none"
    USER_SCALING = "user-scaling"
    EQUILIBRATION_BASED = "equilibration-based"


class BoundMultInitMethodValues(StrEnum):
    """The bound_mult_init_method option values."""

    CONSTANT = "constant"
    MU_BASED = "mu-based"


class AdaptiveMuGlobalizationValues(StrEnum):
    """The adaptive_mu_globalization option values."""

    KKT_ERROR = "kkt-error"
    OBJ_CONSTR_FILTER = "obj-constr-filter"
    NEVER_MONOTONE_MODE = "never-monotone-mode"


class ConstraintViolationNormType(StrEnum):
    """The values for constraint_violation_norm_type option."""

    ONE_NORM = "1-norm"
    MAX_NORM = " max-norm"
    TWO_NORM = "2-norm"


class NormTypeOptionValues(StrEnum):
    """The option values for norm_type options with 2-norm-squared."""

    ONE_NORM = "1-norm"
    MAX_NORM = " max-norm"
    TWO_NORM = "2-norm"
    TWO_NORM_SQUARED = "2-norm-squared"


class MuStrategyValues(StrEnum):
    """The mu_strategy option values."""

    MONOTONE = "monotone"
    ADAPTIVE = "adaptive"


class MuOracleValues(StrEnum):
    """The mu_oracle option values."""

    PROBING = "probing"
    LOGO = "loqo"
    QUALITY_FUNCTION = "quality-function"


class FixedMuOracleValues(StrEnum):
    """The fixed_mu_oracle option values."""

    PROBING = "probing"
    LOGO = "loqo"
    QUALITY_FUNCTION = "quality-function"
    AVERAGE_COMPL = "average_compl"


class QualityFunctionCentralityValues(StrEnum):
    """The quality_function_centrality option values."""

    NONE = "none"
    LOG = "log"
    RECIPROCAL = "reciprocal"
    CUBED_RECIPROCAL = "cube-reciprocal"


class QualityFunctionBalancingTermValues(StrEnum):
    """The quality_function_balancing_term option values."""

    NONE = "none"
    CUBIC = "cubic"


class LineSearchMethodValues(StrEnum):
    """The line_search_method option values."""

    FILTER = "filter"
    CG_PENALTY = "cg-penalty"
    PENALTY = "penalty"


class AlphaForYValues(StrEnum):
    """The alpha_for_y option values."""

    PRIMAL = "primal"
    BOUND_MULT = "bound-mult"
    MIN = "min"
    MAX = "max"
    FULL = "full"
    MIN_DUAL_INFEAS = "min-dual-infeas"
    SAFER_MIN_DUAL_INFEAS = "safer-min-dual-infeas"
    PRIMAL_AND_FULL = "primal-and-full"
    DUAL_AND_FULL = "dual-and-full"
    ACCEPTOR = "acceptor"


class CorrectorTypeValues(StrEnum):
    """The corrector_type option values."""

    NONE = "none"
    AFFINE = "affine"
    PRIMAL_DUAL = "primal-dual"


class LimitedMemoryAugSolverValues(StrEnum):
    """The limited_memory_aug_solver option values."""

    SHERMAN_MORRISON = "sherman-morrison"
    EXTENDED = "extended"


class LimitedMemoryUpdateTypeValues(StrEnum):
    """The limited_memory_update_type option values."""

    BFGS = "bfgs"
    SR1 = "sr1"


class LimitedMemoryInitializationValues(StrEnum):
    """The limited_memory_initialization option values."""

    SCALAR1 = "scalar1"
    SCALAR2 = "scalar2"
    SCALAR3 = "scalar3"
    SCALAR4 = "scalar4"
    CONSTANT = "constant"


class DerivativeTestValues(StrEnum):
    """The derivative_test option values."""

    NONE = "none"
    FIRST_ORDER = "first-order"
    SECOND_ORDER = "second-order"
    ONLY_SECOND_ORDER = "only-second-order"


class JacobianApproximationValues(StrEnum):
    """The jacobian_approximation option values."""

    EXACT = "exact"
    FINITE_DIFFERENCE_VALUES = "finite-difference-values"


class GradientApproximationValues(StrEnum):
    """The gradient_approximation option values."""

    EXACT = "exact"
    FINITE_DIFFERENCE_VALUES = "finite-difference-values"


class HessianApproximationValues(StrEnum):
    """The hessian_approximation option values."""

    EXACT = "exact"
    LIMITED_MEMORY = "limited-memory"


class HessianApproximationSpaceValues(StrEnum):
    """The hessian_approximation_space option values."""

    NONLINEAR_VARIABLES = "nonlinear-variables"
    ALL_VARIABLES = "all-variables"


class IPOPT_Settings(BaseOptimizerSettings):  # noqa: N801
    """Settings for IPOPT."""

    _TARGET_CLASS_NAME = "IPOPT"

    _forced_settings: ClassVar[dict[str, Any]] = {
        "max_iter": 10000,
        "tol": 1e-20,
        "acceptable_iter": 100,
        "diverging_iterates_tol": 1e100,
        "compl_inf_tol": 1e-20,
        "max_wall_time": 1e20,
        "max_cpu_time": 1e20,
    }

    tol: PositiveFloat = Field(
        default=1e-08,
        description="""Desired convergence tolerance (relative). Determines the
        convergence tolerance for the algorithm. The algorithm terminates
        successfully, if the (scaled) NLP error becomes smaller than this
        value, and if the (absolute) criteria according to "dual_inf_tol",
        "constr_viol_tol", and "compl_inf_tol" are met. This is epsilon_tol
        in Eqn. (6) in implementation paper. See also "acceptable_tol" as a
        second termination criterion. Note, some other algorithmic features
        also use this quantity to determine thresholds etc. The valid range
        for this real option is 0 < tol and its default value is 10-08.""",
    )

    s_max: PositiveFloat = Field(
        default=100.0,
        description="""(advanced) Scaling threshold for the NLP error. See paragraph
        after Eqn. (6) in the implementation paper. The valid range for this
        real option is 0 < s_max and its default value is 100.""",
    )

    max_iter: NonNegativeInt = Field(
        default=3000,
        description="""Maximum number of iterations. The algorithm terminates with a
        message if the number of iterations exceeded this number. The valid
        range for this integer option is 0 ≤ max_iter and its default value
        is 3000.""",
    )

    max_wall_time: PositiveFloat = Field(
        default=1e20,
        description="""Maximum number of walltime clock seconds. A limit on walltime
        clock seconds that Ipopt can use to solve one problem. If during the
        convergence check this limit is exceeded, Ipopt will terminate with
        a corresponding message. The valid range for this real option is 0 <
        max_wall_time and its default value is 10+20.""",
    )

    max_cpu_time: PositiveFloat = Field(
        default=1e20,
        description="""Maximum number of CPU seconds. A limit on CPU seconds that Ipopt
        can use to solve one problem. If during the convergence check this
        limit is exceeded, Ipopt will terminate with a corresponding
        message. The valid range for this real option is 0 < max_cpu_time
        and its default value is 10+20.""",
    )

    dual_inf_tol: PositiveFloat = Field(
        default=1.0,
        description="""Desired threshold for the dual infeasibility. Absolute tolerance
        on the dual infeasibility. Successful termination requires that the
        max-norm of the (unscaled) dual infeasibility is less than this
        threshold. The valid range for this real option is 0 < dual_inf_tol
        and its default value is 1.""",
    )

    constr_viol_tol: PositiveFloat = Field(
        default=0.0001,
        description="""Desired threshold for the constraint and variable bound
        violation. Absolute tolerance on the constraint and variable bound
        violation. Successful termination requires that the max-norm of the
        (unscaled) constraint violation is less than this threshold. If
        option bound_relax_factor is not zero 0, then Ipopt relaxes given
        variable bounds. The value of constr_viol_tol is used to restrict
        the absolute amount of this bound relaxation. The valid range for
        this real option is 0 < constr_viol_tol and its default value is
        0.0001.""",
    )

    compl_inf_tol: PositiveFloat = Field(
        default=0.0001,
        description="""Desired threshold for the complementarity conditions. Absolute
        tolerance on the complementarity. Successful termination requires
        that the max-norm of the (unscaled) complementarity is less than
        this threshold. The valid range for this real option is 0 <
        compl_inf_tol and its default value is 0.0001.""",
    )

    acceptable_tol: PositiveFloat = Field(
        default=1e-06,
        description=""""Acceptable" convergence tolerance (relative). Determines which
        (scaled) overall optimality error is considered to be "acceptable".
        There are two levels of termination criteria. If the usual "desired"
        tolerances (see tol, dual_inf_tol etc) are satisfied at an
        iteration, the algorithm immediately terminates with a success
        message. On the other hand, if the algorithm encounters
        "acceptable_iter" many iterations in a row that are considered
        "acceptable", it will terminate before the desired convergence
        tolerance is met. This is useful in cases where the algorithm might
        not be able to achieve the "desired" level of accuracy. The valid
        range for this real option is 0 < acceptable_tol and its default
        value is 10-06.""",
    )

    acceptable_iter: NonNegativeInt = Field(
        default=15,
        description="""Number of "acceptable" iterates before triggering termination. If
        the algorithm encounters this many successive "acceptable" iterates
        (see "acceptable_tol"), it terminates, assuming that the problem has
        been solved to best possible accuracy given round-off. If it is set
        to zero, this heuristic is disabled. The valid range for this
        integer option is 0 ≤ acceptable_iter and its default value is
        15.""",
    )

    acceptable_dual_inf_tol: PositiveFloat = Field(
        default=10000000000.0,
        description=""""Acceptance" threshold for the dual infeasibility. Absolute
        tolerance on the dual infeasibility. "Acceptable" termination
        requires that the (max-norm of the unscaled) dual infeasibility is
        less than this threshold; see also acceptable_tol. The valid range
        for this real option is 0 < acceptable_dual_inf_tol and its default
        value is 10+10.""",
    )

    acceptable_constr_viol_tol: PositiveFloat = Field(
        default=0.01,
        description=""""Acceptance" threshold for the constraint violation. Absolute
        tolerance on the constraint violation. "Acceptable" termination
        requires that the max-norm of the (unscaled) constraint violation is
        less than this threshold; see also acceptable_tol. The valid range
        for this real option is 0 < acceptable_constr_viol_tol and its
        default value is 0.01.""",
    )

    acceptable_compl_inf_tol: PositiveFloat = Field(
        default=0.01,
        description=""""Acceptance" threshold for the complementarity conditions.
        Absolute tolerance on the complementarity. "Acceptable" termination
        requires that the max-norm of the (unscaled) complementarity is less
        than this threshold; see also acceptable_tol. The valid range for
        this real option is 0 < acceptable_compl_inf_tol and its default
        value is 0.01.""",
    )

    acceptable_obj_change_tol: NonNegativeFloat = Field(
        default=1e20,
        description=""""Acceptance" stopping criterion based on objective function
        change. If the relative change of the objective function (scaled by
        Max(1,|f(x)|)) is less than this value, this part of the acceptable
        tolerance termination is satisfied; see also acceptable_tol. This is
        useful for the quasi-Newton option, which has trouble to bring down
        the dual infeasibility. The valid range for this real option is 0 ≤
        acceptable_obj_change_tol and its default value is 10+20.""",
    )

    diverging_iterates_tol: PositiveFloat = Field(
        default=1e20,
        description="""Threshold for maximal value of primal iterates. If any component
        of the primal iterates exceeded this value (in absolute terms), the
        optimization is aborted with the exit message that the iterates seem
        to be diverging. The valid range for this real option is 0 <
        diverging_iterates_tol and its default value is 10+20.""",
    )

    mu_target: NonNegativeFloat = Field(
        default=0.0,
        description="""Desired value of complementarity. Usually, the barrier parameter
        is driven to zero and the termination test for complementarity is
        measured with respect to zero complementarity. However, in some
        cases it might be desired to have Ipopt solve barrier problem for
        strictly positive value of the barrier parameter. In this case, the
        value of "mu_target" specifies the final value of the barrier
        parameter, and the termination tests are then defined with respect
        to the barrier problem for this value of the barrier parameter. The
        valid range for this real option is 0 ≤ mu_target and its default
        value is 0.""",
    )

    print_level: NonNegativeInt = Field(
        default=5,
        description="""Output verbosity level. Sets the default verbosity level for
        console output. The larger this value the more detailed is the
        output. The valid range for this integer option is 0 ≤ print_level ≤
        12 and its default value is 5.""",
        le=12,
    )

    output_file: str = Field(
        default="",
        description="""File name of desired output file (leave unset for no file
        output). NOTE: This option only works when read from the ipopt.opt
        options file! An output file with this name will be written (leave
        unset for no file output). The verbosity level is by default set to
        "print_level", but can be overridden with "file_print_level". The
        file name is changed to use only small letters. The default value
        for this string option is "". Possible values: *: Any acceptable
        standard file name.""",
    )

    file_print_level: NonNegativeInt = Field(
        default=5,
        description="""Verbosity level for output file. NOTE: This option only works
        when read from the ipopt.opt options file! Determines the verbosity
        level for the file specified by "output_file". By default it is the
        same as "print_level". The valid range for this integer option is 0
        ≤ file_print_level ≤ 12 and its default value is 5.""",
        le=12,
    )

    file_append: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Whether to append to output file, if set, instead of truncating.
        NOTE: This option only works when read from the ipopt.opt options
        file! The default value for this string option is "no". Possible
        values: yes, no.""",
    )

    print_user_options: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Print all options set by the user. If selected, the algorithm
        will print the list of all options set by the user including their
        values and whether they have been used. In some cases this
        information might be incorrect, due to the internal program flow.
        The default value for this string option is "no". Possible values:
        yes, no.""",
    )

    print_options_documentation: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Switch to print all algorithmic options with some documentation
        before solving the optimization problem. The default value for this
        string option is "no". Possible values: yes, no.""",
    )

    print_timing_statistics: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Switch to print timing statistics. If selected, the program will
        print the time spend for selected tasks. This implies
        timing_statistics=yes. The default value for this string option is
        "no". Possible values: yes, no.""",
    )

    print_options_mode: PrintOptionsModeValues = Field(
        default=PrintOptionsModeValues.TEXT,
        description="""format in which to print options documentation The default value
        for this string option is "text". Possible values:   text: Ordinary
        text, latex: LaTeX formatted, doxygen: Doxygen (markdown)
        formatted.""",
    )

    print_advanced_options: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""(advanced) whether to print also advanced options The default
        value for this string option is "no". Possible values: yes, no.""",
    )

    print_info_string: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Enables printing of additional info string at end of iteration
        output. This string contains some insider information about the
        current iteration. For details, look for "Diagnostic Tags" in the
        Ipopt documentation. The default value for this string option is
        "no". Possible values: yes, no.""",
    )

    inf_pr_output: InfPrOutputValues = Field(
        default=InfPrOutputValues.ORIGINAL,
        description="""Determines what value is printed in the "inf_pr" output column.
        Ipopt works with a reformulation of the original problem, where
        slacks are introduced and the problem might have been scaled. The
        choice "internal" prints out the constraint violation of this
        formulation. With "original" the true constraint violation in the
        original NLP is printed. The default value for this string option is
        "original". Possible values:  internal: max-norm of violation of
        internal equality constraints, original: maximal constraint
        violation in original NLP.""",
    )

    print_frequency_iter: int = Field(
        default=1,
        description="""Determines at which iteration frequency the summarizing iteration
        output line should be printed. Summarizing iteration output is
        printed every print_frequency_iter iterations, if at least
        print_frequency_time seconds have passed since last output. The
        valid range for this integer option is 1 ≤ print_frequency_iter and
        its default value is 1.""",
        ge=1,
    )

    print_frequency_time: NonNegativeFloat = Field(
        default=0.0,
        description="""Determines at which time frequency the summarizing iteration
        output line should be printed. Summarizing iteration output is
        printed if at least print_frequency_time seconds have passed since
        last output and the iteration number is a multiple of
        print_frequency_iter. The valid range for this real option is 0 ≤
        print_frequency_time and its default value is 0.""",
    )

    nlp_lower_bound_inf: float = Field(
        default=-1e19,
        description="""any bound less or equal this value will be considered -inf (i.e.
        not lower bounded). The valid range for this real option is
        unrestricted and its default value is -10+19.""",
    )

    nlp_upper_bound_inf: float = Field(
        default=1e19,
        description="""any bound greater or this value will be considered +inf (i.e. not
        upper bounded). The valid range for this real option is unrestricted
        and its default value is 10+19.""",
    )

    fixed_variable_treatment: FixedVariableTreatmentValues = Field(
        default=FixedVariableTreatmentValues.MAKE_PARAMETER,
        description="""Determines how fixed variables should be handled. The main
        difference between those options is that the starting point in the
        "make_constraint" case still has the fixed variables at their given
        values, whereas in the case "make_parameter(_nodual)" the functions
        are always evaluated with the fixed values for those variables.
        Also, for "relax_bounds", the fixing bound constraints are relaxed
        (according to" bound_relax_factor"). For all but
        "make_parameter_nodual", bound multipliers are computed for the
        fixed variables. The default value for this string option is
        "make_parameter". Possible values: make_parameter: Remove fixed
        variable from optimization variables, make_parameter_nodual: Remove
        fixed variable from optimization variables and do not compute bound
        multipliers for fixed variables, make_constraint: Add equality
        constraints fixing variables, relax_bounds: Relax fixing bound
        constraints.""",
    )

    dependency_detection_with_rhs: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""(advanced) Indicates if the right hand sides of the constraints
        should be considered in addition to gradients during dependency
        detection The default value for this string option is "no". Possible
        values: yes, no.""",
    )

    num_linear_variables: NonNegativeInt = Field(
        default=0,
        description="""(advanced) Number of linear variables When the Hessian is
        approximated, it is assumed that the first num_linear_variables
        variables are linear. The Hessian is then not approximated in this
        space. If the get_number_of_nonlinear_variables method in the TNLP
        is implemented, this option is ignored. The valid range for this
        integer option is 0 ≤ num_linear_variables and its default value is
        0.""",
    )

    jacobian_approximation: JacobianApproximationValues = Field(
        default=JacobianApproximationValues.EXACT,
        description="""(advanced) Specifies technique to compute constraint Jacobian The
        default value for this string option is "exact". Possible values:
        exact: user-provided derivatives, finite-difference-values: user-
        provided structure, values by finite differences.""",
    )

    gradient_approximation: GradientApproximationValues = Field(
        default=GradientApproximationValues.EXACT,
        description="""(advanced) Specifies technique to compute objective Gradient The
        default value for this string option is "exact". Possible values:
        exact: user-provided gradient, finite-difference-values: values by
        finite differences.""",
    )

    findiff_perturbation: PositiveFloat = Field(
        default=1e-07,
        description="""(advanced) Size of the finite difference perturbation for
        derivative approximation. This determines the relative perturbation
        of the variable entries. The valid range for this real option is 0 <
        findiff_perturbation and its default value is 10-07.""",
    )

    kappa_d: NonNegativeFloat = Field(
        default=1e-05,
        description="""(advanced) Weight for linear damping term (to handle one-sided
        bounds). See Section 3.7 in implementation paper. The valid range
        for this real option is 0 ≤ kappa_d and its default value is
        10-05.""",
    )

    bound_relax_factor: NonNegativeFloat = Field(
        default=1e-08,
        description="""Factor for initial relaxation of the bounds. Before start of the
        optimization, the bounds given by the user are relaxed. This option
        sets the factor for this relaxation. Additional, the constraint
        violation tolerance constr_viol_tol is used to bound the relaxation
        by an absolute value. If it is set to zero, then then bounds
        relaxation is disabled. See Eqn.(35) in implementation paper. Note
        that the constraint violation reported by Ipopt at the end of the
        solution process does not include violations of the original (non-
        relaxed) variable bounds. See also option honor_original_bounds. The
        valid range for this real option is 0 ≤ bound_relax_factor and its
        default value is 10-08.""",
    )

    honor_original_bounds: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether final points should be projected into original
        bounds. Ipopt might relax the bounds during the optimization (see,
        e.g., option "bound_relax_factor"). This option determines whether
        the final point should be projected back into the user-provide
        original bounds after the optimization. Note that violations of
        constraints and complementarity reported by Ipopt at the end of the
        solution process are for the non-projected point. The default value
        for this string option is "no". Possible values: yes, no.""",
    )

    check_derivatives_for_naninf: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether it is desired to check for Nan/Inf in
        derivative matrices Activating this option will cause an error if an
        invalid number is detected in the constraint Jacobians or the
        Lagrangian Hessian. If this is not activated, the test is skipped,
        and the algorithm might proceed with invalid numbers and fail. If
        test is activated and an invalid number is detected, the matrix is
        written to output with print_level corresponding to J_MOREDETAILED
        (7); so beware of large output! The default value for this string
        option is "no". Possible values: yes, no.""",
    )

    grad_f_constant: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether to assume that the objective function is linear
        Activating this option will cause Ipopt to ask for the Gradient of
        the objective function only once from the NLP and reuse this
        information later. The default value for this string option is "no".
        Possible values: yes, no.""",
    )

    jac_c_constant: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether to assume that all equality constraints are
        linear Activating this option will cause Ipopt to ask for the
        Jacobian of the equality constraints only once from the NLP and
        reuse this information later. The default value for this string
        option is "no". Possible values: yes, no.""",
    )

    jac_d_constant: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether to assume that all inequality constraints are
        linear Activating this option will cause Ipopt to ask for the
        Jacobian of the inequality constraints only once from the NLP and
        reuse this information later. The default value for this string
        option is "no". Possible values: yes, no.""",
    )

    hessian_constant: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether to assume the problem is a QP (quadratic
        objective, linear constraints) Activating this option will cause
        Ipopt to ask for the Hessian of the Lagrangian function only once
        from the NLP and reuse this information later. The default value for
        this string option is "no". Possible values: yes, no.""",
    )

    nlp_scaling_method: NlpScalingMethodValues = Field(
        default=NlpScalingMethodValues.GRADIENT_BASED,
        description="""Select the technique used for scaling the NLP. Selects the
        technique used for scaling the problem internally before it is
        solved. For user-scaling, the parameters come from the NLP. If you
        are using AMPL, they can be specified through suffixes
        ("scaling_factor") The default value for this string option is
        "gradient-based". Possible values: none: no problem scaling will be
        performed, user-scaling: scaling parameters will come from the user,
        gradient-based: scale the problem so the maximum gradient at the
        starting point is nlp_scaling_max_gradient, equilibration-based:
        scale the problem so that first derivatives are of order 1 at random
        points (uses Harwell routine MC19).""",
    )

    obj_scaling_factor: float = Field(
        default=1.0,
        description="""Scaling factor for the objective function. This option sets a
        scaling factor for the objective function. The scaling is seen
        internally by Ipopt but the unscaled objective is reported in the
        console output. If additional scaling parameters are computed (e.g.
        user-scaling or gradient-based), both factors are multiplied. If
        this value is chosen to be negative, Ipopt will maximize the
        objective function instead of minimizing it. The valid range for
        this real option is unrestricted and its default value is 1.""",
    )

    nlp_scaling_max_gradient: PositiveFloat = Field(
        default=100.0,
        description="""Maximum gradient after NLP scaling. This is the gradient scaling
        cut-off. If the maximum gradient is above this value, then gradient
        based scaling will be performed. Scaling parameters are calculated
        to scale the maximum gradient back to this value. (This is g_max in
        Section 3.8 of the implementation paper.) Note: This option is only
        used if "nlp_scaling_method" is chosen as "gradient-based". The
        valid range for this real option is 0 < nlp_scaling_max_gradient and
        its default value is 100.""",
    )

    nlp_scaling_obj_target_gradient: NonNegativeFloat = Field(
        default=0.0,
        description="""(advanced) Target value for objective function gradient size. If
        a positive number is chosen, the scaling factor for the objective
        function is computed so that the gradient has the max norm of the
        given size at the starting point. This overrides
        nlp_scaling_max_gradient for the objective function. The valid range
        for this real option is 0 ≤ nlp_scaling_obj_target_gradient and its
        default value is 0.""",
    )

    nlp_scaling_constr_target_gradient: NonNegativeFloat = Field(
        default=0.0,
        description="""(advanced) Target value for constraint function gradient size. If
        a positive number is chosen, the scaling factors for the constraint
        functions are computed so that the gradient has the max norm of the
        given size at the starting point. This overrides
        nlp_scaling_max_gradient for the constraint functions. The valid
        range for this real option is 0 ≤ nlp_scaling_constr_target_gradient
        and its default value is 0.""",
    )

    nlp_scaling_min_value: NonNegativeFloat = Field(
        default=1e-08,
        description="""Minimum value of gradient-based scaling values. This is the lower
        bound for the scaling factors computed by gradient-based scaling
        method. If some derivatives of some functions are huge, the scaling
        factors will otherwise become very small, and the (unscaled) final
        constraint violation, for example, might then be significant. Note:
        This option is only used if "nlp_scaling_method" is chosen as
        "gradient-based". The valid range for this real option is 0 ≤
        nlp_scaling_min_value and its default value is 10-08.""",
    )

    bound_push: PositiveFloat = Field(
        default=0.01,
        description="""Desired minimum absolute distance from the initial point to
        bound. Determines how much the initial point might have to be
        modified in order to be sufficiently inside the bounds (together
        with "bound_frac"). (This is kappa_1 in Section 3.6 of
        implementation paper.) The valid range for this real option is 0 <
        bound_push and its default value is 0.01.""",
    )

    bound_frac: PositiveFloat = Field(
        default=0.01,
        description="""Desired minimum relative distance from the initial point to
        bound. Determines how much the initial point might have to be
        modified in order to be sufficiently inside the bounds (together
        with "bound_push"). (This is kappa_2 in Section 3.6 of
        implementation paper.) The valid range for this real option is 0 <
        bound_frac ≤ 0.5 and its default value is 0.01.""",
        le=0.5,
    )

    slack_bound_push: PositiveFloat = Field(
        default=0.01,
        description="""Desired minimum absolute distance from the initial slack to
        bound. Determines how much the initial slack variables might have to
        be modified in order to be sufficiently inside the inequality bounds
        (together with "slack_bound_frac"). (This is kappa_1 in Section 3.6
        of implementation paper.) The valid range for this real option is 0
        < slack_bound_push and its default value is 0.01.""",
    )

    slack_bound_frac: PositiveFloat = Field(
        default=0.01,
        description="""Desired minimum relative distance from the initial slack to
        bound. Determines how much the initial slack variables might have to
        be modified in order to be sufficiently inside the inequality bounds
        (together with "slack_bound_push"). (This is kappa_2 in Section 3.6
        of implementation paper.) The valid range for this real option is 0
        < slack_bound_frac ≤ 0.5 and its default value is 0.01.""",
        le=0.5,
    )

    constr_mult_init_max: NonNegativeFloat = Field(
        default=1000.0,
        description="""Maximum allowed least-square guess of constraint multipliers.
        Determines how large the initial least-square guesses of the
        constraint multipliers are allowed to be (in max-norm). If the guess
        is larger than this value, it is discarded and all constraint
        multipliers are set to zero. This options is also used when
        initializing the restoration phase. By default,
        "resto.constr_mult_init_max" (the one used in
        RestoIterateInitializer) is set to zero. The valid range for this
        real option is 0 ≤ constr_mult_init_max and its default value is
        1000.""",
    )

    bound_mult_init_val: PositiveFloat = Field(
        default=1.0,
        description="""Initial value for the bound multipliers. All dual variables
        corresponding to bound constraints are initialized to this value.
        The valid range for this real option is 0 < bound_mult_init_val and
        its default value is 1.""",
    )

    bound_mult_init_method: BoundMultInitMethodValues = Field(
        default=BoundMultInitMethodValues.CONSTANT,
        description="""Initialization method for bound multipliers This option defines
        how the iterates for the bound multipliers are initialized. If
        "constant" is chosen, then all bound multipliers are initialized to
        the value of "bound_mult_init_val". If "mu-based" is chosen, then
        each value is initialized to the the value of "mu_init" divided by
        the corresponding slack variable. This latter option might be useful
        if the starting point is close to the optimal solution. The default
        value for this string option is "constant". Possible values:
        constant: set all bound multipliers to the value of
        bound_mult_init_val, mu-based: initialize to mu_init/x_slack.""",
    )

    least_square_init_primal: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Least square initialization of the primal variables If set to
        yes, Ipopt ignores the user provided point and solves a least square
        problem for the primal variables (x and s) to fit the linearized
        equality and inequality constraints.This might be useful if the user
        doesn't know anything about the starting point, or for solving an LP
        or QP. The default value for this string option is "no". Possible
        values:  no: take user-provided point, yes: overwrite user-provided
        point with least-square estimates.""",
    )

    least_square_init_duals: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Least square initialization of all dual variables If set to yes,
        Ipopt tries to compute least-square multipliers (considering ALL
        dual variables). If successful, the bound multipliers are possibly
        corrected to be at least bound_mult_init_val. This might be useful
        if the user doesn't know anything about the starting point, or for
        solving an LP or QP. This overwrites option
        "bound_mult_init_method". The default value for this string option
        is "no". Possible values:  no: use bound_mult_init_val and least-
        square equality constraint multipliers, yes: overwrite user-provided
        point with least-square estimates.""",
    )

    warm_start_init_point: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Warm-start for initial point Indicates whether this optimization
        should use a warm start initialization, where values of primal and
        dual variables are given (e.g., from a previous optimization of a
        related problem.) The default value for this string option is "no".
        Possible values:  no: do not use the warm start initialization, yes:
        use the warm start initialization.""",
    )

    warm_start_same_structure: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""(advanced) Indicates whether a problem with a structure identical
        to the previous one is to be solved. If enabled, then the algorithm
        assumes that an NLP is now to be solved whose structure is identical
        to one that already was considered (with the same NLP object). The
        default value for this string option is "no". Possible values: yes,
        no.""",
    )

    warm_start_bound_push: PositiveFloat = Field(
        default=0.001,
        description="""same as bound_push for the regular initializer The valid range
        for this real option is 0 < warm_start_bound_push and its default
        value is 0.001.""",
    )

    warm_start_bound_frac: PositiveFloat = Field(
        default=0.001,
        description="""same as bound_frac for the regular initializer The valid range
        for this real option is 0 < warm_start_bound_frac ≤ 0.5 and its
        default value is 0.001.""",
        le=0.5,
    )

    warm_start_slack_bound_push: PositiveFloat = Field(
        default=0.001,
        description="""same as slack_bound_push for the regular initializer The valid
        range for this real option is 0 < warm_start_slack_bound_push and
        its default value is 0.001.""",
    )

    warm_start_slack_bound_frac: PositiveFloat = Field(
        default=0.001,
        description="""same as slack_bound_frac for the regular initializer The valid
        range for this real option is 0 < warm_start_slack_bound_frac ≤ 0.5
        and its default value is 0.001.""",
        le=0.5,
    )

    warm_start_mult_bound_push: PositiveFloat = Field(
        default=0.001,
        description="""same as mult_bound_push for the regular initializer The valid
        range for this real option is 0 < warm_start_mult_bound_push and its
        default value is 0.001.""",
    )

    warm_start_mult_init_max: float = Field(
        default=1000000.0,
        description="""Maximum initial value for the equality multipliers. The valid
        range for this real option is unrestricted and its default value is
        10+06.""",
    )

    warm_start_entire_iterate: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""(advanced) Tells algorithm whether to use the GetWarmStartIterate
        method in the NLP. The default value for this string option is "no".
        Possible values:  no: call GetStartingPoint in the NLP, yes: call
        GetWarmStartIterate in the NLP.""",
    )

    warm_start_target_mu: float = Field(
        default=0.0,
        description="""(advanced) Experimental! The valid range for this real option is
        unrestricted and its default value is 0.""",
    )

    replace_bounds: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""(advanced) Whether all variable bounds should be replaced by
        inequality constraints This option must be set for the inexact
        algorithm. The default value for this string option is "no".
        Possible values: yes, no.""",
    )

    skip_finalize_solution_call: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""(advanced) Whether a call to NLPFinalizeSolution after
        optimization should be suppressed In some Ipopt applications, the
        user might want to call the FinalizeSolution method separately.
        Setting this option to "yes" will cause the IpoptApplication object
        to suppress the default call to that method. The default value for
        this string option is "no". Possible values: yes, no.""",
    )

    timing_statistics: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether to measure time spend in components of Ipopt
        and NLP evaluation The overall algorithm time is unaffected by this
        option. The default value for this string option is "no". Possible
        values: yes, no.""",
    )

    mu_max_fact: PositiveFloat = Field(
        default=1000.0,
        description="""Factor for initialization of maximum value for barrier parameter.
        This option determines the upper bound on the barrier parameter.
        This upper bound is computed as the average complementarity at the
        initial point times the value of this option. (Only used if option
        "mu_strategy" is chosen as "adaptive".) The valid range for this
        real option is 0 < mu_max_fact and its default value is 1000.""",
    )

    mu_max: PositiveFloat = Field(
        default=100000.0,
        description="""Maximum value for barrier parameter. This option specifies an
        upper bound on the barrier parameter in the adaptive mu selection
        mode. If this option is set, it overwrites the effect of
        mu_max_fact. (Only used if option "mu_strategy" is chosen as
        "adaptive".) The valid range for this real option is 0 < mu_max and
        its default value is 100000.""",
    )

    mu_min: PositiveFloat = Field(
        default=1e-11,
        description="""Minimum value for barrier parameter. This option specifies the
        lower bound on the barrier parameter in the adaptive mu selection
        mode. By default, it is set to the minimum of 1e-11 and
        min("tol","compl_inf_tol")/("barrier_tol_factor"+1), which should be
        a reasonable value. (Only used if option "mu_strategy" is chosen as
        "adaptive".) The valid range for this real option is 0 < mu_min and
        its default value is 10-11.""",
    )

    adaptive_mu_globalization: AdaptiveMuGlobalizationValues = Field(
        default=AdaptiveMuGlobalizationValues.OBJ_CONSTR_FILTER,
        description="""Globalization strategy for the adaptive mu selection mode. To
        achieve global convergence of the adaptive version, the algorithm
        has to switch to the monotone mode (Fiacco-McCormick approach) when
        convergence does not seem to appear. This option sets the criterion
        used to decide when to do this switch. (Only used if option
        "mu_strategy" is chosen as "adaptive".) The default value for this
        string option is "obj-constr-filter". Possible values:   kkt-error:
        nonmonotone decrease of kkt-error, obj-constr-filter: 2-dim filter
        for objective and constraint violation, never-monotone-mode:
        disables globalization.""",
    )

    adaptive_mu_kkterror_red_iters: NonNegativeInt = Field(
        default=4,
        description="""(advanced) Maximum number of iterations requiring sufficient
        progress. For the "kkt-error" based globalization strategy,
        sufficient progress must be made for
        "adaptive_mu_kkterror_red_iters" iterations. If this number of
        iterations is exceeded, the globalization strategy switches to the
        monotone mode. The valid range for this integer option is 0 ≤
        adaptive_mu_kkterror_red_iters and its default value is 4.""",
    )

    adaptive_mu_kkterror_red_fact: PositiveFloat = Field(
        default=0.9999,
        description="""(advanced) Sufficient decrease factor for "kkt-error"
        globalization strategy. For the "kkt-error" based globalization
        strategy, the error must decrease by this factor to be deemed
        sufficient decrease. The valid range for this real option is 0 <
        adaptive_mu_kkterror_red_fact < 1 and its default value is
        0.9999.""",
        lt=1.0,
    )

    filter_margin_fact: PositiveFloat = Field(
        default=1e-05,
        description="""(advanced) Factor determining width of margin for obj-constr-
        filter adaptive globalization strategy. When using the adaptive
        globalization strategy, "obj-constr-filter", sufficient progress for
        a filter entry is defined as follows: (new obj) < (filter obj) -
        filter_margin_fact*(new constr-viol) OR (new constr-viol) < (filter
        constr-viol) - filter_margin_fact*(new constr-viol). For the
        description of the "kkt-error-filter" option see
        "filter_max_margin". The valid range for this real option is 0 <
        filter_margin_fact < 1 and its default value is 10-05.""",
        lt=1.0,
    )

    filter_max_margin: PositiveFloat = Field(
        default=1.0,
        description="""(advanced) Maximum width of margin in obj-constr-filter adaptive
        globalization strategy. The valid range for this real option is 0 <
        filter_max_margin and its default value is 1.""",
    )

    adaptive_mu_restore_previous_iterate: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""(advanced) Indicates if the previous accepted iterate should be
        restored if the monotone mode is entered. When the globalization
        strategy for the adaptive barrier algorithm switches to the monotone
        mode, it can either start from the most recent iterate (no), or from
        the last iterate that was accepted (yes). The default value for this
        string option is "no". Possible values: yes, no.""",
    )

    adaptive_mu_monotone_init_factor: PositiveFloat = Field(
        default=0.8,
        description="""(advanced) Determines the initial value of the barrier parameter
        when switching to the monotone mode. When the globalization strategy
        for the adaptive barrier algorithm switches to the monotone mode and
        fixed_mu_oracle is chosen as "average_compl", the barrier parameter
        is set to the current average complementarity times the value of
        "adaptive_mu_monotone_init_factor". The valid range for this real
        option is 0 < adaptive_mu_monotone_init_factor and its default value
        is 0.8.""",
    )

    adaptive_mu_kkt_norm_type: NormTypeOptionValues = Field(
        default=NormTypeOptionValues.TWO_NORM_SQUARED,
        description="""(advanced) Norm used for the KKT error in the adaptive mu
        globalization strategies. When computing the KKT error for the
        globalization strategies, the norm to be used is specified with this
        option. Note, this option is also used in the
        QualityFunctionMuOracle. The default value for this string option is
        "2-norm-squared". Possible values: 1-norm: use the 1-norm (abs sum),
        2-norm-squared: use the 2-norm squared (sum of squares), max-norm:
        use the infinity norm (max), 2-norm: use 2-norm.""",
    )

    mu_strategy: MuStrategyValues = Field(
        default=MuStrategyValues.MONOTONE,
        description="""Update strategy for barrier parameter. Determines which barrier
        parameter update strategy is to be used. The default value for this
        string option is "monotone". Possible values:  monotone: use the
        monotone (Fiacco-McCormick) strategy, adaptive: use the adaptive
        update strategy.""",
    )

    mu_oracle: MuOracleValues = Field(
        default=MuOracleValues.QUALITY_FUNCTION,
        description="""Oracle for a new barrier parameter in the adaptive strategy.
        Determines how a new barrier parameter is computed in each "free-
        mode" iteration of the adaptive barrier parameter strategy. (Only
        considered if "adaptive" is selected for option "mu_strategy"). The
        default value for this string option is "quality-function". Possible
        values:   probing: Mehrotra's probing heuristic, loqo: LOQO's
        centrality rule, quality-function: minimize a quality function.""",
    )

    fixed_mu_oracle: FixedMuOracleValues = Field(
        default=FixedMuOracleValues.AVERAGE_COMPL,
        description="""Oracle for the barrier parameter when switching to fixed mode.
        Determines how the first value of the barrier parameter should be
        computed when switching to the "monotone mode" in the adaptive
        strategy. (Only considered if "adaptive" is selected for option
        "mu_strategy".) The default value for this string option is
        "average_compl". Possible values: probing: Mehrotra's probing
        heuristic, loqo: LOQO's centrality rule, quality-function: minimize
        a quality function, average_compl: base on current average
        complementarity.""",
    )

    mu_init: PositiveFloat = Field(
        default=0.1,
        description="""Initial value for the barrier parameter. This option determines
        the initial value for the barrier parameter (mu). It is only
        relevant in the monotone, Fiacco-McCormick version of the algorithm.
        (i.e., if "mu_strategy" is chosen as "monotone") The valid range for
        this real option is 0 < mu_init and its default value is 0.1.""",
    )

    barrier_tol_factor: PositiveFloat = Field(
        default=10.0,
        description="""Factor for mu in barrier stop test. The convergence tolerance for
        each barrier problem in the monotone mode is the value of the
        barrier parameter times "barrier_tol_factor". This option is also
        used in the adaptive mu strategy during the monotone mode. This is
        kappa_epsilon in implementation paper. The valid range for this real
        option is 0 < barrier_tol_factor and its default value is 10.""",
    )

    mu_linear_decrease_factor: PositiveFloat = Field(
        default=0.2,
        description="""Determines linear decrease rate of barrier parameter. For the
        Fiacco-McCormick update procedure the new barrier parameter mu is
        obtained by taking the minimum of mu*"mu_linear_decrease_factor" and
        mu^"superlinear_decrease_power". This is kappa_mu in implementation
        paper. This option is also used in the adaptive mu strategy during
        the monotone mode. The valid range for this real option is 0 <
        mu_linear_decrease_factor < 1 and its default value is 0.2.""",
        lt=1.0,
    )

    mu_superlinear_decrease_power: float = Field(
        default=1.5,
        description="""Determines superlinear decrease rate of barrier parameter. For
        the Fiacco-McCormick update procedure the new barrier parameter mu
        is obtained by taking the minimum of mu*"mu_linear_decrease_factor"
        and mu^"superlinear_decrease_power". This is theta_mu in
        implementation paper. This option is also used in the adaptive mu
        strategy during the monotone mode. The valid range for this real
        option is 1 < mu_superlinear_decrease_power < 2 and its default
        value is 1.5.""",
        gt=1.0,
        lt=2.0,
    )

    mu_allow_fast_monotone_decrease: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.YES,
        description="""(advanced) Allow skipping of barrier problem if barrier test is
        already met. The default value for this string option is "yes".
        Possible values:  no: Take at least one iteration per barrier
        problem even if the barrier test is already met for the updated
        barrier parameter, yes: Allow fast decrease of mu if barrier test it
        met.""",
    )

    tau_min: PositiveFloat = Field(
        default=0.99,
        description="""(advanced) Lower bound on fraction-to-the-boundary parameter tau.
        This is tau_min in the implementation paper. This option is also
        used in the adaptive mu strategy during the monotone mode. The valid
        range for this real option is 0 < tau_min < 1 and its default value
        is 0.99.""",
        lt=1.0,
    )

    sigma_max: PositiveFloat = Field(
        default=100.0,
        description="""(advanced) Maximum value of the centering parameter. This is the
        upper bound for the centering parameter chosen by the quality
        function based barrier parameter update. Only used if option
        "mu_oracle" is set to "quality-function". The valid range for this
        real option is 0 < sigma_max and its default value is 100.""",
    )

    sigma_min: NonNegativeFloat = Field(
        default=1e-06,
        description="""(advanced) Minimum value of the centering parameter. This is the
        lower bound for the centering parameter chosen by the quality
        function based barrier parameter update. Only used if option
        "mu_oracle" is set to "quality-function". The valid range for this
        real option is 0 ≤ sigma_min and its default value is 10-06.""",
    )

    quality_function_norm_type: NormTypeOptionValues = Field(
        default=NormTypeOptionValues.TWO_NORM_SQUARED,
        description="""(advanced) Norm used for components of the quality function. Only
        used if option "mu_oracle" is set to "quality-function". The default
        value for this string option is "2-norm-squared". Possible values:
        1-norm: use the 1-norm (abs sum), 2-norm-squared: use the 2-norm
        squared (sum of squares), max-norm: use the infinity norm (max),
        2-norm: use 2-norm.""",
    )

    quality_function_centrality: QualityFunctionCentralityValues = Field(
        default=QualityFunctionCentralityValues.NONE,
        description="""(advanced) The penalty term for centrality that is included in
        quality function. This determines whether a term is added to the
        quality function to penalize deviation from centrality with respect
        to complementarity. The complementarity measure here is the xi in
        the Loqo update rule. Only used if option "mu_oracle" is set to
        "quality-function". The default value for this string option is
        "none". Possible values: none: no penalty term is added, log:
        complementarity * the log of the centrality measure, reciprocal:
        complementarity * the reciprocal of the centrality measure, cubed-
        reciprocal: complementarity * the reciprocal of the centrality
        measure cubed.""",
    )

    quality_function_balancing_term: QualityFunctionBalancingTermValues = Field(
        default=QualityFunctionBalancingTermValues.NONE,
        description="""(advanced) The balancing term included in the quality function
        for centrality. This determines whether a term is added to the
        quality function that penalizes situations where the complementarity
        is much smaller than dual and primal infeasibilities. Only used if
        option "mu_oracle" is set to "quality-function". The default value
        for this string option is "none". Possible values:  none: no
        balancing term is added, cubic:
        Max(0,Max(dual_inf,primal_inf)-compl)^3.""",
    )

    quality_function_max_section_steps: NonNegativeInt = Field(
        default=8,
        description="""Maximum number of search steps during direct search procedure
        determining the optimal centering parameter. The golden section
        search is performed for the quality function based mu oracle. Only
        used if option "mu_oracle" is set to "quality-function". The valid
        range for this integer option is 0 ≤
        quality_function_max_section_steps and its default value is 8.""",
    )

    quality_function_section_sigma_tol: NonNegativeFloat = Field(
        default=0.01,
        description="""(advanced) Tolerance for the section search procedure determining
        the optimal centering parameter (in sigma space). The golden section
        search is performed for the quality function based mu oracle. Only
        used if option "mu_oracle" is set to "quality-function". The valid
        range for this real option is 0 ≤ quality_function_section_sigma_tol
        < 1 and its default value is 0.01.""",
        lt=1.0,
    )

    quality_function_section_qf_tol: NonNegativeFloat = Field(
        default=0.0,
        description="""(advanced) Tolerance for the golden section search procedure
        determining the optimal centering parameter (in the function value
        space). The golden section search is performed for the quality
        function based mu oracle. Only used if option "mu_oracle" is set to
        "quality-function". The valid range for this real option is 0 ≤
        quality_function_section_qf_tol < 1 and its default value is 0.""",
        lt=1.0,
    )

    line_search_method: LineSearchMethodValues = Field(
        default=LineSearchMethodValues.FILTER,
        description="""(advanced) Globalization method used in backtracking line search
        Only the "filter" choice is officially supported. But sometimes,
        good results might be obtained with the other choices. The default
        value for this string option is "filter". Possible values:   filter:
        Filter method, cg-penalty: Chen-Goldfarb penalty function, penalty:
        Standard penalty function.""",
    )

    alpha_red_factor: PositiveFloat = Field(
        default=0.5,
        description="""(advanced) Fractional reduction of the trial step size in the
        backtracking line search. At every step of the backtracking line
        search, the trial step size is reduced by this factor. The valid
        range for this real option is 0 < alpha_red_factor < 1 and its
        default value is 0.5.""",
        lt=1.0,
    )

    accept_every_trial_step: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Always accept the first trial step. Setting this option to "yes"
        essentially disables the line search and makes the algorithm take
        aggressive steps, without global convergence guarantees. The default
        value for this string option is "no". Possible values: yes, no.""",
    )

    accept_after_max_steps: int = Field(
        default=-1,
        description="""(advanced) Accept a trial point after maximal this number of
        steps even if it does not satisfy line search conditions. Setting
        this to -1 disables this option. The valid range for this integer
        option is -1 ≤ accept_after_max_steps and its default value is
        -1.""",
        ge=-1,
    )

    alpha_for_y: AlphaForYValues = Field(
        default=AlphaForYValues.PRIMAL,
        description="""Method to determine the step size for constraint multipliers
        (alpha_y) . The default value for this string option is "primal".
        Possible values:    primal: use primal step size, bound-mult: use
        step size for the bound multipliers (good for LPs), min: use the min
        of primal and bound multipliers, max: use the max of primal and
        bound multipliers, full: take a full step of size one, min-dual-
        infeas: choose step size minimizing new dual infeasibility, safer-
        min-dual-infeas: like "min_dual_infeas", but safeguarded by "min"
        and "max", primal-and-full: use the primal step size, and full step
        if delta_x <= alpha_for_y_tol, dual-and-full: use the dual step
        size, and full step if delta_x <= alpha_for_y_tol, acceptor: Call
        LSAcceptor to get step size for y.""",
    )

    alpha_for_y_tol: NonNegativeFloat = Field(
        default=10.0,
        description="""Tolerance for switching to full equality multiplier steps. This
        is only relevant if "alpha_for_y" is chosen "primal-and-full" or
        "dual-and-full". The step size for the equality constraint
        multipliers is taken to be one if the max-norm of the primal step is
        less than this tolerance. The valid range for this real option is 0
        ≤ alpha_for_y_tol and its default value is 10.""",
    )

    tiny_step_tol: NonNegativeFloat = Field(
        default=2.22045e-15,
        description="""(advanced) Tolerance for detecting numerically insignificant
        steps. If the search direction in the primal variables (x and s) is,
        in relative terms for each component, less than this value, the
        algorithm accepts the full step without line search. If this happens
        repeatedly, the algorithm will terminate with a corresponding exit
        message. The default value is 10 times machine precision. The valid
        range for this real option is 0 ≤ tiny_step_tol and its default
        value is 2.22045 · 10-15.""",
    )

    tiny_step_y_tol: NonNegativeFloat = Field(
        default=0.01,
        description="""(advanced) Tolerance for quitting because of numerically
        insignificant steps. If the search direction in the primal variables
        (x and s) is, in relative terms for each component, repeatedly less
        than tiny_step_tol, and the step in the y variables is smaller than
        this threshold, the algorithm will terminate. The valid range for
        this real option is 0 ≤ tiny_step_y_tol and its default value is
        0.01.""",
    )

    watchdog_shortened_iter_trigger: NonNegativeInt = Field(
        default=10,
        description="""Number of shortened iterations that trigger the watchdog. If the
        number of successive iterations in which the backtracking line
        search did not accept the first trial point exceeds this number, the
        watchdog procedure is activated. Choosing "0" here disables the
        watchdog procedure. The valid range for this integer option is 0 ≤
        watchdog_shortened_iter_trigger and its default value is 10.""",
    )

    watchdog_trial_iter_max: int = Field(
        default=3,
        description="""Maximum number of watchdog iterations. This option determines the
        number of trial iterations allowed before the watchdog procedure is
        aborted and the algorithm returns to the stored point. The valid
        range for this integer option is 1 ≤ watchdog_trial_iter_max and its
        default value is 3.""",
        ge=1,
    )

    theta_max_fact: PositiveFloat = Field(
        default=10000.0,
        description="""(advanced) Determines upper bound for constraint violation in the
        filter. The algorithmic parameter theta_max is determined as
        theta_max_fact times the maximum of 1 and the constraint violation
        at initial point. Any point with a constraint violation larger than
        theta_max is unacceptable to the filter (see Eqn. (21) in the
        implementation paper). The valid range for this real option is 0 <
        theta_max_fact and its default value is 10000.""",
    )

    theta_min_fact: PositiveFloat = Field(
        default=0.0001,
        description="""(advanced) Determines constraint violation threshold in the
        switching rule. The algorithmic parameter theta_min is determined as
        theta_min_fact times the maximum of 1 and the constraint violation
        at initial point. The switching rule treats an iteration as an
        h-type iteration whenever the current constraint violation is larger
        than theta_min (see paragraph before Eqn. (19) in the implementation
        paper). The valid range for this real option is 0 < theta_min_fact
        and its default value is 0.0001.""",
    )

    eta_phi: PositiveFloat = Field(
        default=1e-08,
        description="""(advanced) Relaxation factor in the Armijo condition. See Eqn.
        (20) in the implementation paper. The valid range for this real
        option is 0 < eta_phi < 0.5 and its default value is 10-08.""",
        lt=0.5,
    )

    delta: PositiveFloat = Field(
        default=1.0,
        description="""(advanced) Multiplier for constraint violation in the switching
        rule. See Eqn. (19) in the implementation paper. The valid range for
        this real option is 0 < delta and its default value is 1.""",
    )

    s_phi: float = Field(
        default=2.3,
        description="""(advanced) Exponent for linear barrier function model in the
        switching rule. See Eqn. (19) in the implementation paper. The valid
        range for this real option is 1 < s_phi and its default value is
        2.3.""",
        gt=1.0,
    )

    s_theta: float = Field(
        default=1.1,
        description="""(advanced) Exponent for current constraint violation in the
        switching rule. See Eqn. (19) in the implementation paper. The valid
        range for this real option is 1 < s_theta and its default value is
        1.1.""",
        gt=1.0,
    )

    gamma_phi: PositiveFloat = Field(
        default=1e-08,
        description="""(advanced) Relaxation factor in the filter margin for the barrier
        function. See Eqn. (18a) in the implementation paper. The valid
        range for this real option is 0 < gamma_phi < 1 and its default
        value is 10-08.""",
        lt=1.0,
    )

    gamma_theta: PositiveFloat = Field(
        default=1e-05,
        description="""(advanced) Relaxation factor in the filter margin for the
        constraint violation. See Eqn. (18b) in the implementation paper.
        The valid range for this real option is 0 < gamma_theta < 1 and its
        default value is 10-05.""",
        lt=1.0,
    )

    alpha_min_frac: PositiveFloat = Field(
        default=0.05,
        description="""(advanced) Safety factor for the minimal step size (before
        switching to restoration phase). This is gamma_alpha in Eqn. (23) in
        the implementation paper. The valid range for this real option is 0
        < alpha_min_frac < 1 and its default value is 0.05.""",
        lt=1.0,
    )

    max_soc: NonNegativeInt = Field(
        default=4,
        description="""Maximum number of second order correction trial steps at each
        iteration. Choosing 0 disables the second order corrections. This is
        p^{max} of Step A-5.9 of Algorithm A in the implementation paper.
        The valid range for this integer option is 0 ≤ max_soc and its
        default value is 4.""",
    )

    kappa_soc: PositiveFloat = Field(
        default=0.99,
        description="""(advanced) Factor in the sufficient reduction rule for second
        order correction. This option determines how much a second order
        correction step must reduce the constraint violation so that further
        correction steps are attempted. See Step A-5.9 of Algorithm A in the
        implementation paper. The valid range for this real option is 0 <
        kappa_soc and its default value is 0.99.""",
    )

    obj_max_inc: float = Field(
        default=5.0,
        description="""(advanced) Determines the upper bound on the acceptable increase
        of barrier objective function. Trial points are rejected if they
        lead to an increase in the barrier objective function by more than
        obj_max_inc orders of magnitude. The valid range for this real
        option is 1 < obj_max_inc and its default value is 5.""",
        gt=1.0,
    )

    max_filter_resets: NonNegativeInt = Field(
        default=5,
        description="""(advanced) Maximal allowed number of filter resets A positive
        number enables a heuristic that resets the filter, whenever in more
        than "filter_reset_trigger" successive iterations the last rejected
        trial steps size was rejected because of the filter. This option
        determine the maximal number of resets that are allowed to take
        place. The valid range for this integer option is 0 ≤
        max_filter_resets and its default value is 5.""",
    )

    filter_reset_trigger: int = Field(
        default=5,
        description="""(advanced) Number of iterations that trigger the filter reset. If
        the filter reset heuristic is active and the number of successive
        iterations in which the last rejected trial step size was rejected
        because of the filter, the filter is reset. The valid range for this
        integer option is 1 ≤ filter_reset_trigger and its default value is
        5.""",
        ge=1,
    )

    corrector_type: CorrectorTypeValues = Field(
        default=CorrectorTypeValues.NONE,
        description="""(advanced) The type of corrector steps that should be taken. If
        "mu_strategy" is "adaptive", this option determines what kind of
        corrector steps should be tried. Changing this option is
        experimental. The default value for this string option is "none".
        Possible values:   none: no corrector, affine: corrector step
        towards mu=0, primal-dual: corrector step towards current mu.""",
    )

    skip_corr_if_neg_curv: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.YES,
        description="""(advanced) Whether to skip the corrector step in negative
        curvature iteration. The corrector step is not tried if negative
        curvature has been encountered during the computation of the search
        direction in the current iteration. This option is only used if
        "mu_strategy" is "adaptive". Changing this option is experimental.
        The default value for this string option is "yes". Possible values:
        yes, no.""",
    )

    skip_corr_in_monotone_mode: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.YES,
        description="""(advanced) Whether to skip the corrector step during monotone
        barrier parameter mode. The corrector step is not tried if the
        algorithm is currently in the monotone mode (see also option
        "barrier_strategy"). This option is only used if "mu_strategy" is
        "adaptive". Changing this option is experimental. The default value
        for this string option is "yes". Possible values: yes, no.""",
    )

    corrector_compl_avrg_red_fact: PositiveFloat = Field(
        default=1.0,
        description="""(advanced) Complementarity tolerance factor for accepting
        corrector step. This option determines the factor by which
        complementarity is allowed to increase for a corrector step to be
        accepted. Changing this option is experimental. The valid range for
        this real option is 0 < corrector_compl_avrg_red_fact and its
        default value is 1.""",
    )

    soc_method: NonNegativeInt = Field(
        default=0,
        description="""Ways to apply second order correction This option determines the
        way to apply second order correction, 0 is the method described in
        the implementation paper. 1 is the modified way which adds alpha on
        the rhs of x and s rows. The valid range for this integer option is
        0 ≤ soc_method ≤ 1 and its default value is 0.""",
        le=1,
    )

    nu_init: PositiveFloat = Field(
        default=1e-06,
        description="""(advanced) Initial value of the penalty parameter. The valid
        range for this real option is 0 < nu_init and its default value is
        10-06.""",
    )

    nu_inc: PositiveFloat = Field(
        default=0.0001,
        description="""(advanced) Increment of the penalty parameter. The valid range
        for this real option is 0 < nu_inc and its default value is
        0.0001.""",
    )

    rho: PositiveFloat = Field(
        default=0.1,
        description="""(advanced) Value in penalty parameter update formula. The valid
        range for this real option is 0 < rho < 1 and its default value is
        0.1.""",
        lt=1.0,
    )

    kappa_sigma: PositiveFloat = Field(
        default=10000000000.0,
        description="""(advanced) Factor limiting the deviation of dual variables from
        primal estimates. If the dual variables deviate from their primal
        estimates, a correction is performed. See Eqn. (16) in the
        implementation paper. Setting the value to less than 1 disables the
        correction. The valid range for this real option is 0 < kappa_sigma
        and its default value is 10+10.""",
    )

    recalc_y: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Tells the algorithm to recalculate the equality and inequality
        multipliers as least square estimates. This asks the algorithm to
        recompute the multipliers, whenever the current infeasibility is
        less than recalc_y_feas_tol. Choosing yes might be helpful in the
        quasi-Newton option. However, each recalculation requires an extra
        factorization of the linear system. If a limited memory quasi-Newton
        option is chosen, this is used by default. The default value for
        this string option is "no". Possible values:  no: use the Newton
        step to update the multipliers, yes: use least-square multiplier
        estimates.""",
    )

    recalc_y_feas_tol: PositiveFloat = Field(
        default=1e-06,
        description="""Feasibility threshold for recomputation of multipliers. If
        recalc_y is chosen and the current infeasibility is less than this
        value, then the multipliers are recomputed. The valid range for this
        real option is 0 < recalc_y_feas_tol and its default value is
        10-06.""",
    )

    slack_move: NonNegativeFloat = Field(
        default=1.81899e-12,
        description="""(advanced) Correction size for very small slacks. Due to
        numerical issues or the lack of an interior, the slack variables
        might become very small. If a slack becomes very small compared to
        machine precision, the corresponding bound is moved slightly. This
        parameter determines how large the move should be. Its default value
        is mach_eps^{3/4}. See also end of Section 3.5 in implementation
        paper - but actual implementation might be somewhat different. The
        valid range for this real option is 0 ≤ slack_move and its default
        value is 1.81899 · 10-12.""",
    )

    constraint_violation_norm_type: ConstraintViolationNormType = Field(
        default=ConstraintViolationNormType.ONE_NORM,
        description="""(advanced) Norm to be used for the constraint violation in the
        line search. Determines which norm should be used when the algorithm
        computes the constraint violation in the line search. The default
        value for this string option is "1-norm". Possible values:   1-norm:
        use the 1-norm, 2-norm: use the 2-norm, max-norm: use the infinity
        norm.""",
    )

    linear_scaling_on_demand: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.YES,
        description="""Flag indicating that linear scaling is only done if it seems
        required. This option is only important if a linear scaling method
        (e.g., mc19) is used. If you choose "no", then the scaling factors
        are computed for every linear system from the start. This can be
        quite expensive. Choosing "yes" means that the algorithm will start
        the scaling method only when the solutions to the linear system seem
        not good, and then use it until the end. The default value for this
        string option is "yes". Possible values: yes, no.""",
    )

    mehrotra_algorithm: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether to do Mehrotra's predictor-corrector algorithm.
        If enabled, line search is disabled and the (unglobalized) adaptive
        mu strategy is chosen with the "probing" oracle, and
        "corrector_type=affine" is used without any safeguards; you should
        not set any of those options explicitly in addition. Also, unless
        otherwise specified, the values of "bound_push", "bound_frac", and
        "bound_mult_init_val" are set more aggressive, and sets
        "alpha_for_y=bound_mult". The Mehrotra's predictor-corrector
        algorithm works usually very well for LPs and convex QPs. The
        default value for this string option is "no". Possible values: yes,
        no.""",
    )

    fast_step_computation: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates if the linear system should be solved quickly. If
        enabled, the algorithm assumes that the linear system that is solved
        to obtain the search direction is solved sufficiently well. In that
        case, no residuals are computed to verify the solution and the
        computation of the search direction is a little faster. The default
        value for this string option is "no". Possible values: yes, no.""",
    )

    min_refinement_steps: NonNegativeInt = Field(
        default=1,
        description="""Minimum number of iterative refinement steps per linear system
        solve. Iterative refinement (on the full unsymmetric system) is
        performed for each right hand side. This option determines the
        minimum number of iterative refinements (i.e. at least
        "min_refinement_steps" iterative refinement steps are enforced per
        right hand side.) The valid range for this integer option is 0 ≤
        min_refinement_steps and its default value is 1.""",
    )

    max_refinement_steps: NonNegativeInt = Field(
        default=10,
        description="""Maximum number of iterative refinement steps per linear system
        solve. Iterative refinement (on the full unsymmetric system) is
        performed for each right hand side. This option determines the
        maximum number of iterative refinement steps. The valid range for
        this integer option is 0 ≤ max_refinement_steps and its default
        value is 10.""",
    )

    residual_ratio_max: PositiveFloat = Field(
        default=1e-10,
        description="""(advanced) Iterative refinement tolerance Iterative refinement is
        performed until the residual test ratio is less than this tolerance
        (or until "max_refinement_steps" refinement steps are performed).
        The valid range for this real option is 0 < residual_ratio_max and
        its default value is 10-10.""",
    )

    residual_ratio_singular: PositiveFloat = Field(
        default=1e-05,
        description="""(advanced) Threshold for declaring linear system singular after
        failed iterative refinement. If the residual test ratio is larger
        than this value after failed iterative refinement, the algorithm
        pretends that the linear system is singular. The valid range for
        this real option is 0 < residual_ratio_singular and its default
        value is 10-05.""",
    )

    residual_improvement_factor: PositiveFloat = Field(
        default=1.0,
        description="""(advanced) Minimal required reduction of residual test ratio in
        iterative refinement. If the improvement of the residual test ratio
        made by one iterative refinement step is not better than this
        factor, iterative refinement is aborted. The valid range for this
        real option is 0 < residual_improvement_factor and its default value
        is 1.""",
    )

    neg_curv_test_tol: NonNegativeFloat = Field(
        default=0.0,
        description="""Tolerance for heuristic to ignore wrong inertia. If nonzero,
        incorrect inertia in the augmented system is ignored, and Ipopt
        tests if the direction is a direction of positive curvature. This
        tolerance is alpha_n in the paper by Zavala and Chiang (2014) and it
        determines when the direction is considered to be sufficiently
        positive. A value in the range of [1e-12, 1e-11] is recommended. The
        valid range for this real option is 0 ≤ neg_curv_test_tol and its
        default value is 0.""",
    )

    neg_curv_test_reg: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.YES,
        description="""Whether to do the curvature test with the primal regularization
        (see Zavala and Chiang, 2014). The default value for this string
        option is "yes". Possible values:  yes: use primal regularization
        with the inertia-free curvature test, no: use original IPOPT
        approach, in which the primal regularization is ignored.""",
    )

    max_hessian_perturbation: PositiveFloat = Field(
        default=1e20,
        description="""Maximum value of regularization parameter for handling negative
        curvature. In order to guarantee that the search directions are
        indeed proper descent directions, Ipopt requires that the inertia of
        the (augmented) linear system for the step computation has the
        correct number of negative and positive eigenvalues. The idea is
        that this guides the algorithm away from maximizers and makes Ipopt
        more likely converge to first order optimal points that are
        minimizers. If the inertia is not correct, a multiple of the
        identity matrix is added to the Hessian of the Lagrangian in the
        augmented system. This parameter gives the maximum value of the
        regularization parameter. If a regularization of that size is not
        enough, the algorithm skips this iteration and goes to the
        restoration phase. This is delta_w^max in the implementation paper.
        The valid range for this real option is 0 < max_hessian_perturbation
        and its default value is 10+20.""",
    )

    min_hessian_perturbation: NonNegativeFloat = Field(
        default=1e-20,
        description="""Smallest perturbation of the Hessian block. The size of the
        perturbation of the Hessian block is never selected smaller than
        this value, unless no perturbation is necessary. This is delta_w^min
        in implementation paper. The valid range for this real option is 0 ≤
        min_hessian_perturbation and its default value is 10-20.""",
    )

    perturb_inc_fact_first: float = Field(
        default=100.0,
        description="""Increase factor for x-s perturbation for very first perturbation.
        The factor by which the perturbation is increased when a trial value
        was not sufficient - this value is used for the computation of the
        very first perturbation and allows a different value for the first
        perturbation than that used for the remaining perturbations. This is
        bar_kappa_w^+ in the implementation paper. The valid range for this
        real option is 1 < perturb_inc_fact_first and its default value is
        100.""",
        gt=1.0,
    )

    perturb_inc_fact: float = Field(
        default=8.0,
        description="""Increase factor for x-s perturbation. The factor by which the
        perturbation is increased when a trial value was not sufficient -
        this value is used for the computation of all perturbations except
        for the first. This is kappa_w^+ in the implementation paper. The
        valid range for this real option is 1 < perturb_inc_fact and its
        default value is 8.""",
        gt=1.0,
    )

    perturb_dec_fact: PositiveFloat = Field(
        default=0.333333,
        description="""Decrease factor for x-s perturbation. The factor by which the
        perturbation is decreased when a trial value is deduced from the
        size of the most recent successful perturbation. This is kappa_w^-
        in the implementation paper. The valid range for this real option is
        0 < perturb_dec_fact < 1 and its default value is 0.333333.""",
        lt=1.0,
    )

    first_hessian_perturbation: PositiveFloat = Field(
        default=0.0001,
        description="""Size of first x-s perturbation tried. The first value tried for
        the x-s perturbation in the inertia correction scheme. This is
        delta_0 in the implementation paper. The valid range for this real
        option is 0 < first_hessian_perturbation and its default value is
        0.0001.""",
    )

    jacobian_regularization_value: NonNegativeFloat = Field(
        default=1e-08,
        description="""Size of the regularization for rank-deficient constraint
        Jacobians. This is bar delta_c in the implementation paper. The
        valid range for this real option is 0 ≤
        jacobian_regularization_value and its default value is 10-08.""",
    )

    jacobian_regularization_exponent: NonNegativeFloat = Field(
        default=0.25,
        description="""(advanced) Exponent for mu in the regularization for rank-
        deficient constraint Jacobians. This is kappa_c in the
        implementation paper. The valid range for this real option is 0 ≤
        jacobian_regularization_exponent and its default value is 0.25.""",
    )

    perturb_always_cd: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""(advanced) Active permanent perturbation of constraint
        linearization. Enabling this option leads to using the delta_c and
        delta_d perturbation for the computation of every search direction.
        Usually, it is only used when the iteration matrix is singular. The
        default value for this string option is "no". Possible values: yes,
        no.""",
    )

    expect_infeasible_problem: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Enable heuristics to quickly detect an infeasible problem. This
        options is meant to activate heuristics that may speed up the
        infeasibility determination if you expect that there is a good
        chance for the problem to be infeasible. In the filter line search
        procedure, the restoration phase is called more quickly than
        usually, and more reduction in the constraint violation is enforced
        before the restoration phase is left. If the problem is square, this
        option is enabled automatically. The default value for this string
        option is "no". Possible values: yes, no.""",
    )

    expect_infeasible_problem_ctol: NonNegativeFloat = Field(
        default=0.001,
        description="""Threshold for disabling "expect_infeasible_problem" option. If
        the constraint violation becomes smaller than this threshold, the
        "expect_infeasible_problem" heuristics in the filter line search are
        disabled. If the problem is square, this options is set to 0. The
        valid range for this real option is 0 ≤
        expect_infeasible_problem_ctol and its default value is 0.001.""",
    )

    expect_infeasible_problem_ytol: PositiveFloat = Field(
        default=100000000.0,
        description="""Multiplier threshold for activating "expect_infeasible_problem"
        option. If the max norm of the constraint multipliers becomes larger
        than this value and "expect_infeasible_problem" is chosen, then the
        restoration phase is entered. The valid range for this real option
        is 0 < expect_infeasible_problem_ytol and its default value is
        10+08.""",
    )

    start_with_resto: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Whether to switch to restoration phase in first iteration.
        Setting this option to "yes" forces the algorithm to switch to the
        feasibility restoration phase in the first iteration. If the initial
        point is feasible, the algorithm will abort with a failure. The
        default value for this string option is "no". Possible values: yes,
        no.""",
    )

    soft_resto_pderror_reduction_factor: NonNegativeFloat = Field(
        default=0.9999,
        description="""Required reduction in primal-dual error in the soft restoration
        phase. The soft restoration phase attempts to reduce the primal-dual
        error with regular steps. If the damped primal-dual step (damped
        only to satisfy the fraction-to-the-boundary rule) is not decreasing
        the primal-dual error by at least this factor, then the regular
        restoration phase is called. Choosing "0" here disables the soft
        restoration phase. The valid range for this real option is 0 ≤
        soft_resto_pderror_reduction_factor and its default value is
        0.9999.""",
    )

    max_soft_resto_iters: NonNegativeInt = Field(
        default=10,
        description="""(advanced) Maximum number of iterations performed successively in
        soft restoration phase. If the soft restoration phase is performed
        for more than so many iterations in a row, the regular restoration
        phase is called. The valid range for this integer option is 0 ≤
        max_soft_resto_iters and its default value is 10.""",
    )

    required_infeasibility_reduction: NonNegativeFloat = Field(
        default=0.9,
        description="""Required reduction of infeasibility before leaving restoration
        phase. The restoration phase algorithm is performed, until a point
        is found that is acceptable to the filter and the infeasibility has
        been reduced by at least the fraction given by this option. The
        valid range for this real option is 0 ≤
        required_infeasibility_reduction < 1 and its default value is
        0.9.""",
        lt=1.0,
    )

    max_resto_iter: NonNegativeInt = Field(
        default=3000000,
        description="""(advanced) Maximum number of successive iterations in restoration
        phase. The algorithm terminates with an error message if the number
        of iterations successively taken in the restoration phase exceeds
        this number. The valid range for this integer option is 0 ≤
        max_resto_iter and its default value is 3000000.""",
    )

    evaluate_orig_obj_at_resto_trial: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.YES,
        description="""Determines if the original objective function should be evaluated
        at restoration phase trial points. Enabling this option makes the
        restoration phase algorithm evaluate the objective function of the
        original problem at every trial point encountered during the
        restoration phase, even if this value is not required. In this way,
        it is guaranteed that the original objective function can be
        evaluated without error at all accepted iterates; otherwise the
        algorithm might fail at a point where the restoration phase accepts
        an iterate that is good for the restoration phase problem, but not
        the original problem. On the other hand, if the evaluation of the
        original objective is expensive, this might be costly. The default
        value for this string option is "yes". Possible values: yes, no.""",
    )

    resto_penalty_parameter: PositiveFloat = Field(
        default=1000.0,
        description="""(advanced) Penalty parameter in the restoration phase objective
        function. This is the parameter rho in equation (31a) in the Ipopt
        implementation paper. The valid range for this real option is 0 <
        resto_penalty_parameter and its default value is 1000.""",
    )

    resto_proximity_weight: NonNegativeFloat = Field(
        default=1.0,
        description="""(advanced) Weighting factor for the proximity term in restoration
        phase objective. This determines how the parameter zeta in equation
        (29a) in the implementation paper is computed. zeta here is
        resto_proximity_weight*sqrt(mu), where mu is the current barrier
        parameter. The valid range for this real option is 0 ≤
        resto_proximity_weight and its default value is 1.""",
    )

    bound_mult_reset_threshold: NonNegativeFloat = Field(
        default=1000.0,
        description="""Threshold for resetting bound multipliers after the restoration
        phase. After returning from the restoration phase, the bound
        multipliers are updated with a Newton step for complementarity.
        Here, the change in the primal variables during the entire
        restoration phase is taken to be the corresponding primal Newton
        step. However, if after the update the largest bound multiplier
        exceeds the threshold specified by this option, the multipliers are
        all reset to 1. The valid range for this real option is 0 ≤
        bound_mult_reset_threshold and its default value is 1000.""",
    )

    constr_mult_reset_threshold: NonNegativeFloat = Field(
        default=0.0,
        description="""Threshold for resetting equality and inequality multipliers after
        restoration phase. After returning from the restoration phase, the
        constraint multipliers are recomputed by a least square estimate.
        This option triggers when those least-square estimates should be
        ignored. The valid range for this real option is 0 ≤
        constr_mult_reset_threshold and its default value is 0.""",
    )

    resto_failure_feasibility_threshold: NonNegativeFloat = Field(
        default=0.0,
        description="""(advanced) Threshold for primal infeasibility to declare failure
        of restoration phase. If the restoration phase is terminated because
        of the "acceptable" termination criteria and the primal
        infeasibility is smaller than this value, the restoration phase is
        declared to have failed. The default value is actually 1e2*tol,
        where tol is the general termination tolerance. The valid range for
        this real option is 0 ≤ resto_failure_feasibility_threshold and its
        default value is 0.""",
    )

    limited_memory_aug_solver: LimitedMemoryAugSolverValues = Field(
        default=LimitedMemoryAugSolverValues.SHERMAN_MORRISON,
        description="""(advanced) Strategy for solving the augmented system for low-rank
        Hessian. The default value for this string option is "sherman-
        morrison". Possible values:  sherman-morrison: use Sherman-Morrison
        formula, extended: use an extended augmented system.""",
    )

    limited_memory_max_history: NonNegativeInt = Field(
        default=6,
        description="""Maximum size of the history for the limited quasi-Newton Hessian
        approximation. This option determines the number of most recent
        iterations that are taken into account for the limited-memory quasi-
        Newton approximation. The valid range for this integer option is 0 ≤
        limited_memory_max_history and its default value is 6.""",
    )

    limited_memory_update_type: LimitedMemoryUpdateTypeValues = Field(
        default=LimitedMemoryUpdateTypeValues.BFGS,
        description="""Quasi-Newton update formula for the limited memory quasi-Newton
        approximation. The default value for this string option is "bfgs".
        Possible values:  bfgs: BFGS update (with skipping), sr1: SR1 (not
        working well).""",
    )

    limited_memory_initialization: LimitedMemoryInitializationValues = Field(
        default=LimitedMemoryInitializationValues.SCALAR1,
        description="""Initialization strategy for the limited memory quasi-Newton
        approximation. Determines how the diagonal Matrix B_0 as the first
        term in the limited memory approximation should be computed. The
        default value for this string option is "scalar1". Possible values:
        scalar1: sigma = s^Ty/s^Ts, scalar2: sigma = y^Ty/s^Ty, scalar3:
        arithmetic average of scalar1 and scalar2, scalar4: geometric
        average of scalar1 and scalar2, constant: sigma =
        limited_memory_init_val.""",
    )

    limited_memory_init_val: PositiveFloat = Field(
        default=1.0,
        description="""Value for B0 in low-rank update. The starting matrix in the low
        rank update, B0, is chosen to be this multiple of the identity in
        the first iteration (when no updates have been performed yet), and
        is constantly chosen as this value, if
        "limited_memory_initialization" is "constant". The valid range for
        this real option is 0 < limited_memory_init_val and its default
        value is 1.""",
    )

    limited_memory_init_val_max: PositiveFloat = Field(
        default=100000000.0,
        description="""Upper bound on value for B0 in low-rank update. The starting
        matrix in the low rank update, B0, is chosen to be this multiple of
        the identity in the first iteration (when no updates have been
        performed yet), and is constantly chosen as this value, if
        "limited_memory_initialization" is "constant". The valid range for
        this real option is 0 < limited_memory_init_val_max and its default
        value is 10+08.""",
    )

    limited_memory_init_val_min: PositiveFloat = Field(
        default=1e-08,
        description="""Lower bound on value for B0 in low-rank update. The starting
        matrix in the low rank update, B0, is chosen to be this multiple of
        the identity in the first iteration (when no updates have been
        performed yet), and is constantly chosen as this value, if
        "limited_memory_initialization" is "constant". The valid range for
        this real option is 0 < limited_memory_init_val_min and its default
        value is 10-08.""",
    )

    limited_memory_max_skipping: int = Field(
        default=2,
        description="""Threshold for successive iterations where update is skipped. If
        the update is skipped more than this number of successive
        iterations, the quasi-Newton approximation is reset. The valid range
        for this integer option is 1 ≤ limited_memory_max_skipping and its
        default value is 2.""",
        ge=1,
    )

    limited_memory_special_for_resto: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Determines if the quasi-Newton updates should be special during
        the restoration phase. Until Nov 2010, Ipopt used a special update
        during the restoration phase, but it turned out that this does not
        work well. The new default uses the regular update procedure and it
        improves results. If for some reason you want to get back to the
        original update, set this option to "yes". The default value for
        this string option is "no". Possible values: yes, no.""",
    )

    hessian_approximation: HessianApproximationValues = Field(
        default=HessianApproximationValues.EXACT,
        description="""Indicates what Hessian information is to be used. This determines
        which kind of information for the Hessian of the Lagrangian function
        is used by the algorithm. The default value for this string option
        is "exact". Possible values:  exact: Use second derivatives provided
        by the NLP., limited-memory: Perform a limited-memory quasi-Newton
        approximation.""",
    )

    hessian_approximation_space: HessianApproximationSpaceValues = Field(
        default=HessianApproximationSpaceValues.NONLINEAR_VARIABLES,
        description="""(advanced) Indicates in which subspace the Hessian information is
        to be approximated. The default value for this string option is
        "nonlinear-variables". Possible values:  nonlinear-variables: only
        in space of nonlinear variables., all-variables: in space of all
        variables (without slacks).""",
    )

    derivative_test: DerivativeTestValues = Field(
        default=DerivativeTestValues.NONE,
        description="""Enable derivative checker If this option is enabled, a (slow!)
        derivative test will be performed before the optimization. The test
        is performed at the user provided starting point and marks
        derivative values that seem suspicious The default value for this
        string option is "none". Possible values: none: do not perform
        derivative test, first-order: perform test of first derivatives at
        starting point, second-order: perform test of first and second
        derivatives at starting point, only-second-order: perform test of
        second derivatives at starting point.""",
    )

    derivative_test_first_index: int = Field(
        default=-2,
        description="""Index of first quantity to be checked by derivative checker If
        this is set to -2, then all derivatives are checked. Otherwise, for
        the first derivative test it specifies the first variable for which
        the test is done (counting starts at 0). For second derivatives, it
        specifies the first constraint for which the test is done; counting
        of constraint indices starts at 0, and -1 refers to the objective
        function Hessian. The valid range for this integer option is -2 ≤
        derivative_test_first_index and its default value is -2.""",
        ge=-2,
    )

    derivative_test_perturbation: PositiveFloat = Field(
        default=1e-08,
        description="""Size of the finite difference perturbation in derivative test.
        This determines the relative perturbation of the variable entries.
        The valid range for this real option is 0 <
        derivative_test_perturbation and its default value is 10-08.""",
    )

    derivative_test_tol: PositiveFloat = Field(
        default=0.0001,
        description="""Threshold for indicating wrong derivative. If the relative
        deviation of the estimated derivative from the given one is larger
        than this value, the corresponding derivative is marked as wrong.
        The valid range for this real option is 0 < derivative_test_tol and
        its default value is 0.0001.""",
    )

    derivative_test_print_all: YesOrNoOptionValues = Field(
        default=YesOrNoOptionValues.NO,
        description="""Indicates whether information for all estimated derivatives
        should be printed. Determines verbosity of derivative checker. The
        default value for this string option is "no". Possible values: yes,
        no.""",
    )

    point_perturbation_radius: NonNegativeFloat = Field(
        default=10.0,
        description="""Maximal perturbation of an evaluation point. If a random
        perturbation of a points is required, this number indicates the
        maximal perturbation. This is for example used when determining the
        center point at which the finite difference derivative test is
        executed. The valid range for this real option is 0 ≤
        point_perturbation_radius and its default value is 10.""",
    )

    mumps_print_level: NonNegativeInt = Field(
        default=0,
        description="""Debug printing level for the linear solver MUMPS 0: no printing;
        1: Error messages only; 2: Error, warning, and main statistic
        messages; 3: Error and warning messages and terse diagnostics; >=4:
        All information. The valid range for this integer option is 0 ≤
        mumps_print_level and its default value is 0.""",
    )

    mumps_pivtol: NonNegativeFloat = Field(
        default=1e-06,
        description="""Pivot tolerance for the linear solver MUMPS. A smaller number
        pivots for sparsity, a larger number pivots for stability. The valid
        range for this real option is 0 ≤ mumps_pivtol ≤ 1 and its default
        value is 10-06.""",
        le=1.0,
    )

    mumps_pivtolmax: NonNegativeFloat = Field(
        default=0.1,
        description="""Maximum pivot tolerance for the linear solver MUMPS. Ipopt may
        increase pivtol as high as pivtolmax to get a more accurate solution
        to the linear system. The valid range for this real option is 0 ≤
        mumps_pivtolmax ≤ 1 and its default value is 0.1.""",
        le=1.0,
    )

    mumps_mem_percent: NonNegativeInt = Field(
        default=1000,
        description="""Percentage increase in the estimated working space for MUMPS.
        When significant extra fill-in is caused by numerical pivoting,
        larger values of mumps_mem_percent may help use the workspace more
        efficiently. On the other hand, if memory requirement are too large
        at the very beginning of the optimization, choosing a much smaller
        value for this option, such as 5, might reduce memory requirements.
        The valid range for this integer option is 0 ≤ mumps_mem_percent and
        its default value is 1000.""",
    )

    mumps_permuting_scaling: NonNegativeInt = Field(
        default=7,
        description="""Controls permuting and scaling in MUMPS This is ICNTL(6) in
        MUMPS. The valid range for this integer option is 0 ≤
        mumps_permuting_scaling ≤ 7 and its default value is 7.""",
        le=7,
    )

    mumps_pivot_order: NonNegativeInt = Field(
        default=7,
        description="""Controls pivot order in MUMPS This is ICNTL(7) in MUMPS. The
        valid range for this integer option is 0 ≤ mumps_pivot_order ≤ 7 and
        its default value is 7.""",
        le=7,
    )

    mumps_scaling: int = Field(
        default=77,
        description="""Controls scaling in MUMPS This is ICNTL(8) in MUMPS. The valid
        range for this integer option is -2 ≤ mumps_scaling ≤ 77 and its
        default value is 77.""",
        ge=-2,
        le=77,
    )

    mumps_dep_tol: float = Field(
        default=0.0,
        description="""(advanced) Threshold to consider a pivot at zero in detection of
        linearly dependent constraints with MUMPS. This is CNTL(3) in MUMPS.
        The valid range for this real option is unrestricted and its default
        value is 0.""",
    )

    mumps_mpi_communicator: int = Field(
        default=-987654,
        description="""(advanced) MPI communicator used for matrix operations This sets
        the MPI communicator. MPI_COMM_WORLD is the default. Any other value
        should be the return value from MPI_Comm_c2f. The valid range for
        this integer option is unrestricted and its default value is
        -987654. This option is only available if MUMPS's libseq/mpi.h is
        not used.""",
    )

    user_provided_options: dict[str, Any] | None = Field(
        default=None,
        description="""Any additional IPOPT option provided by the user. To be used if
        passing options linked to external linear solvers. If using any
        linear solver other than "mumps", it must be passed under the key
        "linear_solver".""",
    )
