# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import numpy as np
from scipy.optimize import bisect


def _residual_3d_boundary_treatment(
    this_pitch,
    Np,
    pitch_w,
    pitch_a,
    gap_w,
    gap_a,
    height,
    dep_side,
    row,
    phi,
    acc_Nth_lat,
):
    """Evaluate the residual of given pitch_w for a given DLD system; to be
    used to find the correct pitch_w.

    Aiming at solving the following equation for this_pitch:

    dep side:
        this_R=R_b/(n.eps) : R_b denotes the resistance of a unit cell in
        bulk of domain
        this_ --> this boundary unit
        _b    --> bulk
        this_R/R_b = 1/(n.eps) ---Eq.2---> = pitch_w/this_pitch.this_f/f,
        wherein f denotes the whole correction factor for bulk, and this_f is
        that of this bounary unit.
        =>  pitch_w/this_pitch.this_f/f=Np/n
        Finally:
        ``this_f/this_pitch=f/pitch_w*Np/n``,


    acc side:
        - n<Np:
            this_R=R_b/(2-n.eps)
            this_R/R_b = 1/(2-n.eps)
            ---Eq.2---> = pitch_w/this_pitch.this_f/f
            pitch_w/this_pitch.this_f/f=Np/(2.Np-n)

            Finally:
            ``this_f/this_pitch=f/pitch_w*Np/(2.Np-n)``

        - n=Np:
            this_R+R_lat=R_b_axial+R_b_lateral.eps

            We define ``omega=R_b_lateral/R_b_axial``. Therefore:
            this_R+R_lat=R_b_axial(1+eps.omega)

            ``omega`` can be calculated as follows:
            omega=R_b_lateral/R_b_axial
            =[pitch_w/pitch_a.f(pitch_a)]/[pitch_a/pitch_w.f(pitch_w)],
            wherein ``f`` denotes the resistance correction factor (the
            bracket in Eq. 2 (Inglis et. al. 2020)).

            The expression for ``omega`` can be simplified into:
            omega=(pitch_w/pitch_a)**2.f(pitch_a)/f(pitch_w)

            From pressure balance:
            this_R+R_lat=R_b_axial(1+eps.omega)
            assume R_lat=phi.this_R
            this_R(1+phi)=R_b_axial(1+eps.omega)
            this_R/R_b_axial=(1+eps.omega)/(1+phi)
            -->
            [f(this_pitch)/this_pitch]/[f(pitch_w)/pitch_w]
            =(1+eps.omega)/(1+phi)

            Finally:
            f(this_pitch)/this_pitch=
                f(pitch_w)/pitch_w.(1+eps.omega)/(1+phi)


            #--- Lateral gap
            Also, from above we have the following for ``R_acc_N_lat``:
            this_R/R_b_axial=(1+eps.omega)/(1+phi)
            =>
            phi.this_R/R_b_axial=phi.(1+eps.omega)/(1+phi)
            R_lat/R_b_axial=phi.(1+eps.omega)/(1+phi)

            We know the following
            R_lat/R_b_axial=
            [pitch_w/this_pitch.f(this_pitch)]/[pitch_a/pitch_w.f(pitch_w)]
            which, from above, is equal to phi.(1+eps.omega)/(1+phi)

            Finally:
            f(this_pitch)/this_pitch=
                phi.pitch_a/pitch_w.[f(pitch_w)/pitch_w].(1+eps.omega)/(1+phi)

            Note:
                For `R_acc_N_lat`, the orientaion is 90-deg different from that
                of R_b (resistance of unit cell in bulk region in axial
                direction) as `R_acc_N_lat` is in the lateral direction.
                That is, ``this_pitch``, herein, denotes the axial pitch of
                Nth lateral resistance. As the axial pitch is fixed, the
                difference of the axial pitch values show the gap widening
                required through cutting the pillars.
    """

    # make sure row is in the range
    row %= Np
    if row == 0:
        row = Np

    # valid range
    D_over_W_valid_range = [0.3, 0.9]
    T_over_W_valid_range = [0.5, 4.5]

    # identifiers with same names as in original work
    T = height
    W = pitch_w
    L = pitch_a
    D_w = pitch_w - gap_w
    D_a = pitch_a - gap_a

    D_w_over_W = D_w / W
    D_a_over_L = D_a / L
    T_over_W = T / W

    if (
        min(D_w_over_W, D_a_over_L) < D_over_W_valid_range[0]
        or max(D_w_over_W, D_a_over_L) > D_over_W_valid_range[1]
    ):
        print(
            f"""(boundary_treatment='3d') Warning:
D_w/W={D_w_over_W} and D_a/L={D_a_over_L} while the valid range is
{D_over_W_valid_range}"""
        )
    if T_over_W < T_over_W_valid_range[0] or T_over_W > T_over_W_valid_range[1]:
        print(
            f"""(boundary_treatment='3d') Warning:
T/W={T_over_W} while the valid range is {T_over_W_valid_range}"""
        )

    # ------------------------------------------------------------------------
    # Note:
    #
    # Herein, we use the model developed by Inglis et. al. (2020) to determine
    # hydraulic resistances. The model was developed for circular cylinders.
    # We apply some modifications so it can be implemented for other cases,
    # e.g., elliptical pillars, rectangular pillars, and generally pillars
    # with any arbitrary shape. However, be mindful of possible noticeable
    # inaccuracies in estimating resistances, which can affect the accuracy of
    # model eventually.
    #
    # The current implementation replaces pillar of any shape with a
    # circular post of a diameter matching the sidelength of original pillar
    # normal to flow direction. That is, when estimating axial resistance,
    # pillar diameter is assumed to be equal to sidelength of pillar in
    # lateral direction, while sidelength of pillar in axial direction is
    # considered as diameter for estimating lateral resistance.
    #
    # This assumption is based on an "intuition" that gap between pillars
    # affects the resistance against a fluid flowing through the gap more
    # significantly than the contour of pillar relatively far away from the
    # opening.
    # ------------------------------------------------------------------------

    # resistance correction factor for flow along axis of channel
    f_a = correction_factor(D_w, W, T)

    # resistance correction factor for flow along width of channel
    f_w = correction_factor(D_a, L, T)

    # resistance correction factor for this local flow;
    # ``this_pitch``: pitch normal to local flow
    if acc_Nth_lat:
        this_f = correction_factor(D_a, this_pitch, T)
    else:
        this_f = correction_factor(D_w, this_pitch, T)

    # ------------------------------------------------------------------------
    # nondim params
    # pitch_ratio: lateral pitch over axial pitch
    # omega: resistance ratio of bulk grid (lateral over axial): R_b_l/R_b_a
    # ------------------------------------------------------------------------
    pitch_ratio = pitch_w / pitch_a
    omega = pitch_ratio**2.0 * f_w / f_a

    # ------------------------------------------------------------------------
    # nondim params
    # pitch_ratio: lateral pitch over axial pitch
    # omega: resistance ratio of bulk grid (lateral over axial): R_b_l/R_b_a
    # ------------------------------------------------------------------------
    pitch_ratio = pitch_w / pitch_a
    omega = pitch_ratio**2.0 * f_w / f_a

    # --- different cases
    #
    # General form:
    #
    # this_R = R_b_axial * psi
    #
    if dep_side:
        psi = Np / row
    else:
        eps = 1.0 / Np
        if row == Np and phi is not None:
            # axial resistance of Nth row on acc side
            psi = (1 + eps * omega) / (1 + phi)

            # lateral resistance of Nth row on acc side
            if acc_Nth_lat:
                psi *= phi / pitch_ratio
        else:
            psi = Np / (2 * Np - row)

    # --- residual
    lhs = this_f / this_pitch
    rhs = f_a / pitch_w * psi

    return lhs - rhs


def correction_factor(D, W, T):
    """Returns the correction factor in the bracket in Eq. 2 (Inglis et.
    al. 2020)."""

    # fit params
    a = 1.702
    b = 0.600
    c = 2.682
    d = 1.833

    f = 1.0 + a * (b + np.tan(np.pi / 2.0 * D / W)) ** c * (T / W) ** d

    return f


def get_gap_with_pressure_balance(
    Np,
    pitch_w,
    pitch_a,
    gap_w,
    gap_a,
    height,
    dep_side,
    row,
    phi,
    acc_Nth_lat,
    estimate=None,
    verbose=True,
):
    """Get gap_w for a DLD system" """

    # estimate of pitch
    if estimate is None:
        if acc_Nth_lat:
            estimate = pitch_a
        else:
            estimate = pitch_w

    if acc_Nth_lat:
        pitch = pitch_a
        diameter = pitch_a - gap_a
    else:
        pitch = pitch_w
        diameter = pitch_w - gap_w

    # ----------------------------------------
    # range to examine to find solution
    # lower bound: reducing gap to almost 0
    # upper bound: a sufficiently large number
    # ----------------------------------------

    # Small number as the minimum allowed gap (for stability of solver)
    _EPSILON = 1e-15

    lower_bound = diameter + _EPSILON
    upper_bound = 10 * max(estimate, pitch_w, pitch_a)

    # args for ``_residual_3d_boundary_treatment`` function
    args = (
        Np,
        pitch_w,
        pitch_a,
        gap_w,
        gap_a,
        height,
        dep_side,
        row,
        phi,
        acc_Nth_lat,
    )

    # --- Both ``brentq`` & ``bisect`` work well
    this_pitch, msg = bisect(
        _residual_3d_boundary_treatment,
        lower_bound,
        upper_bound,
        args=args,
        maxiter=1000,
        xtol=1e-15,
        full_output=True,
    )

    # --- ``root_scalar`` can be used as well
    # sol = root_scalar(
    #     _residual_3d_boundary_treatment,
    #     args=args,
    #     method='toms748',
    #     bracket=[lower_bound, upper_bound])
    # this_pitch=sol.root

    # --- ``root`` does not allow lower bound, which causes issue as there are
    # typically multiple non-physical roots for negative gaps (pitch<diameter).
    # msg = root(
    #     fun=_residual_3d_boundary_treatment,
    #     x0=estimate,
    #     args=args,
    #     method='lm',
    # )
    # this_pitch=msg.x[0]

    # --- gap and residual
    this_gap = this_pitch - diameter
    residual = _residual_3d_boundary_treatment(this_pitch, *args)

    # --- check desired tolerance --

    # a representative of the magnitude of terms on rhs of equation to be
    # solved (f/pitch_w*Np)
    residual_mag_ref = (
        correction_factor(D=diameter, W=pitch, T=height) / pitch_w * Np
    )

    # residual relative to ref. magnitude of terms in equation to be solved.
    residual_rel = residual / residual_mag_ref

    # desired tol: this means we want the absolute residual, i.e.,
    # ``residual`` to be smaller than ``atol*residual_mag_ref``. Equivalently,
    # ``residual_rel`` needs to be smaller than ``atol``.

    atol = 1e-6
    # rtol=1e-5 #not needed for rel. residual
    check_tol = np.isclose(0.0, residual_rel, atol=atol)

    if not check_tol:
        print(
            f"""Warning: Root found for row {row} on
{'dep. side' if dep_side else 'acc. side'} is {this_pitch:.3e}.
The rel. residual is {residual_rel:.3e} and does NOT meet the specified
residual tolerance of atol: {atol:.1e}."""
        )

    if verbose:
        print("msg: ", msg)
        print("sol: ", this_pitch)
        print("residual:", residual)
        print("check tol:", check_tol)

    return this_gap
