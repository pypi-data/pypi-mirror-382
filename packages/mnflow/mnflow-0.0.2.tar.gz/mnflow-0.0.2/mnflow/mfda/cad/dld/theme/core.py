# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


"""Core of DLD"""

from typing import Union

import numpy as np

from mnflow.mfda.cad.dld.utils.boundary_model import (
    get_gap_with_pressure_balance,
)


class DLD:
    """DLD core entities (posts/pillars). It can be used as a building block
    by child classes to make more complex designs, and ultimately a whole DLD
    device.

    A full set of DLD core entities consists of:
        - ``Np+1`` rows ranging from 0 (most downstream) to ``Np`` (most\
        upstream).
        - Three regions:
            - core: bulk of DLD entities residing on a tilted grid/matrix.
            - depletion: boundary wherein the particles larger than critical\
            diameter are depleted.
            - accumulation: boundary wherein the particles larger than\
            critical diameter are accumulated.

    The entities on depletion (dep.) and accumulation (acc.) lanes are
    configured based on the specified boundary treatment approach
    (``boundary_treatment``). Categorizing the DLD core entities in this
    manner should enable a convenient framework for developing new boundary
    treatment strategies in the future.

    .. Note::
        - All length dimensions are in micron.
        - The parameters are attempted to be assigned automatically for a\
        specific `standardized` design, also called `base design` herein, so\
        that a user can conveniently configure the DLD entities. For the cases\
        deviating from the base design, the corresponding parameters can be\
        explicitly set by passing appropriate values to the constructor. For\
        example:
            - If no value is passed for ``pitch_w``, it will be set equal to\
            ``2*gap_w`` if ``gap_w`` is available.
            - If ``gap_a`` and ``pitch_a`` are not given, they are set equal\
            to their lateral counterparts, `i.e.`, ``gap_w`` and ``pitch_w``,\
            respectively.
            - If both ``gap_a`` and ``pitch_a`` are provided, the axial length\
            of entity is adjusted so that both provided arguments are met. As\
            a result, for example, an ellipse with various major axis to minor\
            axis ratios can be configured  by passing desired ``gap_a`` and\
            ``pitch_a``.
            - If only one of ``gap_a`` and ``pitch_a`` is provided, the entity\
            is assumed to have an aspect ratio of 1. The provided argument is\
            used to evaluate the appropriate value for the missing parameter:
                - If ``pitch_a`` is provided, ``gap_a`` will be set equal to\
                ``gap_w+pitch_a-pitch_w``
                - If ``gap_a`` is provided, ``pitch_a`` will be set equal to\
                ``pitch_w-gap_w+gap_a``

    .. Important::
        (For developers) ``core.DLD`` stores the information related to the
        full set of entities of DLD core, `i.e.`, ``Np+1`` rows ranging from 0
        to ``Np``.
        Row ``Np`` provides some useful information for child classes aiming
        at producing complex DLD devices.
        However, row ``Np`` should not be included when arraying a DLD core.
        To produce a DLD device with a periodicity of ``Np``, only ``Np`` rows
        (0 to ``Np-1``) should be arrayed.
    """

    # available boundary treatment approaches
    available_boundary_treatments = [None, "pow", "pow_2", "pow_3", "3d", "mlb"]

    def __init__(
        self,
        # Core Geometry
        Np=None,
        d_c=None,
        width=None,
        Nw=None,
        gap_w=None,
        gap_a=None,
        pitch_w=None,
        pitch_a=None,
        height=None,
        # Boundary
        opt_enable_boundary_treatment_none=None,
        opt_acc_balance_pressure=None,
        boundary_treatment=None,
        pow_val=None,
        phi=None,
        acc_usm_gap_a_widening=None,
        _max_allowed_lateral_gap_widening_nondim=None,
        dep_top_gap_deviation_nondim=None,
        acc_top_gap_deviation_nondim=None,
        # Misc.
        ll=None,
    ):
        """
        **Constructor**

        Parameters
        ----------

        **Core Geometry**

        Np : int or NoneType, optional
            Periodicity of DLD, which is equal to the number of rows of
            entities in a DLD core, by default None
        width : int or NoneType, optional
            Desired width of core.DLD unit; Note that the actual width may be
            larger as ``Nw`` is calculated as ceiling of ``width/pitch_w``, by
            default None
        Nw : int or NoneType, optional
            Number of fluidic lanes (columns), which is equal to the number of
            entities per row minus one, by default None
        gap_w : float or NoneType, optional
            Spacing/gap between entities along the width of channel, also
            called lateral direction (normal to channel axis), by default None
        gap_a : float or NoneType, optional
            Spacing/gap between entities along the axis of channel (axial flow
            direction), by default None
        pitch_w : float or NoneType, optional
            Pitch of entities along the width of channel (lateral direction),
            by default None
        pitch_a : float or NoneType, optional
            Pitch of entities along the axis of channel (axial flow
            direction), by default None
        height : float, optional
            Pillars height; important when using '3d' type of
            ``boundary_treatment``, by default None.

        **Boundary**

        opt_enable_boundary_treatment_none : bool, optional
            The code automatically applies a boundary treatment approach to
            mitigate the issues associated with dep. and acc. sidewalls
            disturbing the nearby fluid flow. In the case that no special
            boundary treatment is needed, this parameter can be used:
            if ``True``, and ``boundary_treatment=None``:
            `No special boundary treatment needed`;
            if ``False``, and ``boundary_treatment=None``:
            a boundary treatment approach is automatically selected;
            by default False.
        opt_acc_balance_pressure : bool, optional
            This parameter enables the local pressure balance at the upstream-
            most row of accumulation sidewall. The local pressure balance
            feature is applied for the ``3d`` boundary treatment by default.
            Other boundary treatment approaches can also adopt this feature by
            passing ``opt_acc_balance_pressure=True`` in conjunction with
            an optional value for ``phi`` in the case that the default value
            of ``phi`` may need an adjustment. In order to disable this
            feature, pass ``opt_acc_balance_pressure=False``; by default True.
        boundary_treatment : str or NoneType, optional; by default 'pow_3'
            Type of boundary treatment; available options are:
                - None : no special treatment.
                - 'pow' : generic power relation between flux and gap as in\
                `Ebadi et. al. (2019)\
                <https://doi.org/10.1007/s42452-019-1064-5>`_. A value to be\
                provided for ``pow_val``; otherwise a default value of 2.463\
                is used as reported in the original work.
                - 'pow_2' : (special case of 'pow') flux through a gap is\
                assumed to be proportional to the square of the gap width. Not\
                exactly the same layout but using the square root dependency\
                of gap as in `Inglis (2009)\
                <https://doi.org/10.1063/1.3068750>`_.
                - 'pow_3' : (special case of 'pow') flux through a gap is\
                assumed to be proportional to the cube of the gap width. Not\
                exactly the same layout but using the cube root dependency of\
                gap for high aspect-ratio entities as pointed to in `Feng et.\
                al. (2017)\
                <https://aip.scitation.org/doi/10.1063/1.4981014>`_.
                - '3d' : flux through a gap is evaluated from a\
                computationally-curated dataset by `Inglis et. al. (2020)\
                <https://doi.org/10.1007/s10404-020-2323-x>`_, which takes\
                into account the 3-dimensional geometrical configuratin of DLD\
                system, e.g., diameter, hight, and axial and lateral pitch.

        pow_val : float, optional
            Power value when using 'pow' type of ``boundary_treatment``, by
            default 2.463.
        phi : float, optional
            Ratio of lateral resistance to axial resistance of unit cell close\
            to accumulation sidewall on :math:`N^{th}` row, when using '3d'\
            type of ``boundary_treatment``, by default None.
        acc_usm_gap_a_widening : float, optional
            (usm: up.stream.most) Gap widening magnitude for the upstreammost
            entity on acc. sidewall; it can override the automatic gap
            widening value that would otherwise be applied to satisfy the
            resistance ratio related to the ``phi`` value, by default None.
        _max_allowed_lateral_gap_widening_nondim : float, optional
            Maximum allowed lateral gap nondimensionalized by axial sidelength
            of entity, a value in the range of [0,2) is expected, by default
            1.5.
        dep_top_gap_deviation_nondim : list or tuple or NoneType, optional
            Deviation of lateral gap at the most upstream row of depletion
            lane(s) from the normal lateral gap (``gap_w``)
            non-dimensionalized by ``gap_w``; a negative value denotes
            decreasing gap; number of depletion lanes equals the lenght of
            list/tuple; relevant if ``boundary_treatment`` is set to 'mlb';
            by default None
        acc_top_gap_deviation_nondim : list or tuple or NoneType, optional
            Deviation of lateral gap at the most upstream row of accumulation
            lane(s) from the normal lateral gap (``gap_w``)
            non-dimensionalized by ``gap_w``; a negative value denotes
            decreasing gap; number of accumulation lanes equals the lenght of
            list/tuple; relevant if ``boundary_treatment`` is set to 'mlb';
            by default None



        **Misc.**

        ll : tuple or list, optional
            Stands for 'lower-leftmost': Coordinates of  lower-leftmost entity
            amongst the core entities of DLD core not considering the
            depletion and accumulation boundary lanes, can be superseded by
            ``target_ll`` of child classes, `e.g`, ``block.DLD``, by default
            (0, 0)
        """

        # --- default params
        if opt_enable_boundary_treatment_none is None:
            opt_enable_boundary_treatment_none = False

        if opt_acc_balance_pressure is None:
            opt_acc_balance_pressure = True

        if (
            boundary_treatment is None
            and not opt_enable_boundary_treatment_none
        ):  # default boundary treatment
            boundary_treatment = [None, "pow_2", "pow_3", "pow", "3d"][2]

        if pow_val is None:
            pow_val = 2.463

        if phi is None:
            # Once a more appropriate design rule is determined, this may be
            # revised.
            phi = 1

        if _max_allowed_lateral_gap_widening_nondim is None:
            _max_allowed_lateral_gap_widening_nondim = 1.5

        if ll is None:
            ll = (0, 0)

        # ---config to enable same name for static and instance methods
        self.get_dc = self._get_dc

        # ----------------------------------------------------------
        # self attributes
        # ----------------------------------------------------------
        lst_param_to_set = DLD.__init__.__code__.co_varnames[
            1 : DLD.__init__.__code__.co_argcount
        ]
        lcl = locals()
        for _sn_key, key in enumerate(lst_param_to_set):
            setattr(self, key, lcl[key])

        # --- geometrical attributes
        _dict_to_unpack = DLD.get_geom_config_auto(
            Np=Np,
            d_c=d_c,
            width=width,
            Nw=Nw,
            gap_w=gap_w,
            gap_a=gap_a,
            pitch_w=pitch_w,
            pitch_a=pitch_a,
            height=height,
        )
        for key in _dict_to_unpack:
            setattr(self, key, _dict_to_unpack.get(key))

        # --- default configs of boundary
        self._config_boundary()

        # --- preparing the coordinates of entities
        self._prep()

    def __repr__(self):
        var_lst = [
            "Np",
            "Nw",
            "gap_w",
            "pitch_w",
            "gap_a",
            "pitch_a",
            "height",
            "boundary_treatment",
        ]
        var_float = ["gap_w", "pitch_w", "gap_a", "pitch_a", "height"]
        msg = "core.DLD__"

        for var in var_lst:
            if var in var_float:
                msg += f"_{var}:{getattr(self, var):.3f}"
            else:
                msg += f"_{var}:{getattr(self, var)}"

        return msg

    def get_acc_theta(
        self,
    ):
        # Gets the tilt angle (rad) of acc. sidewall.

        p1 = self.acc_dots_full[-1][-1]
        p2 = self.acc_dots_full[-1][0]

        return np.arctan((p2[0] - p1[0]) / (p2[1] - p1[1]))

    def dots_core_row(
        self,
        row,
    ):
        """Returns the coordinates of entities in row number ``row`` of  the
        core of DLD core, i.e., excluding those related to the depletion and
        accumulation lanes.

        Parameters
        ----------
        row : int
            Number/Index of row with 0 referring to the most downstream row
            and ``Np-1`` referring to the most upstream one.

        Returns
        -------
        Numpy array
            Array of positions of entities residing on row ``row`` excluding
            those related to accumulation and depletion lanes.
        """
        dots = self.dots_core_full
        row = row % (self.Np + 1)

        if row == -1 % (self.Np + 1):  # last row (most upstream row)
            return dots[row * (self.core_dots_num_pillars_per_row) :]
        else:
            return dots[
                row
                * (self.core_dots_num_pillars_per_row) : (row + 1)
                * (self.core_dots_num_pillars_per_row)
            ]

    def _config_boundary(
        self,
    ):
        """Default configs for different boundary treatments."""

        # The gap deviations are wrt. the normal gaps.
        # A positive value denotes widening of gap and negative values
        # refer to shrinkage of gap.
        if self.boundary_treatment in DLD.available_boundary_treatments:

            # --------------
            # set pow_val
            # --------------
            if self.boundary_treatment == "pow_2":
                self.pow_val = 2
            elif self.boundary_treatment == "pow_3":
                self.pow_val = 3

            # --------------
            # set mlb
            # --------------
            if self.boundary_treatment == "mlb":
                if self.dep_top_gap_deviation_nondim is None:
                    self.dep_top_gap_deviation_nondim = [-0.75]

                if self.acc_top_gap_deviation_nondim is None:
                    self.acc_top_gap_deviation_nondim = [0.4]

            else:
                if self.dep_top_gap_deviation_nondim is not None:
                    raise ValueError(
                        f"""
``dep_top_gap_deviation_nondim`` needs to be None for boundary treatment other
than 'mlb'. Currently:
``boundary_treatment``: {self.boundary_treatment}
``self.dep_top_gap_deviation_nondim``: {self.dep_top_gap_deviation_nondim}"""
                    )

                if self.acc_top_gap_deviation_nondim is not None:
                    raise ValueError(
                        f"""
``acc_top_gap_deviation_nondim`` needs to be None for boundary treatment other
than 'mlb'. Currently:
``boundary_treatment``: {self.boundary_treatment}
``self.acc_top_gap_deviation_nondim``: {self.acc_top_gap_deviation_nondim}"""
                    )

        else:
            raise ValueError(
                f"""Not a valid value for ``boundary_treatment``:
{self.boundary_treatment}"""
            )

        # --------------------------------------------------------------------
        # number of lanes in dep boundaries
        # --------------------------------------------------------------------
        if self.dep_top_gap_deviation_nondim is None:
            self.dep_num_lanes = 1
        else:
            self.dep_num_lanes = len(self.dep_top_gap_deviation_nondim)

        # --------------------------------------------------------------------
        # number of lanes in acc boundaries
        # --------------------------------------------------------------------
        if self.acc_top_gap_deviation_nondim is None:
            self.acc_num_lanes = 1
        else:
            self.acc_num_lanes = len(self.acc_top_gap_deviation_nondim)

        """
        Core dots:
            number of lanes: `Nw-acc_num_lanes-dep_num_lanes`
            number of pillars per row: `number of lanes+1`
        """
        self.core_dots_num_lanes = (
            self.Nw - self.acc_num_lanes - self.dep_num_lanes
        )
        self.core_dots_num_pillars_per_row = self.core_dots_num_lanes + 1

        # --------------------------------------------------------------------
        # angle of DLD core entities with channel axis stored as a positive
        # value (dep. side on the left, and acc. side on the right)
        # --------------------------------------------------------------------
        self.theta = abs(np.arctan(self.pitch_w / self.pitch_a / self.Np))

        # mlb config
        if self.boundary_treatment == "mlb":
            self._config_mlb()

    def _config_mlb(
        self,
    ):
        # -------------------------------------------
        # set up the dep rotations and displacements
        # -------------------------------------------

        # total lateral displacement of entities on dep. lanes from their
        # unaltered positions on regular DLD matrix
        self.dep_top_disp_tot = []
        self.dep_theta_dev = []
        self.dep_theta = []
        for sn, gap_dev_nd in enumerate(self.dep_top_gap_deviation_nondim):
            if sn == 0:
                self.dep_top_disp_tot.append(0.0)
            else:
                self.dep_top_disp_tot.append(self.dep_top_disp_tot[-1])

            # A positive rotation/displacement is towards outwad of DLD core;
            # i.e. increasing the gap of boundary lanes
            self.dep_top_disp_tot[-1] += gap_dev_nd * self.gap_w
            self.dep_theta_dev.append(
                np.arctan(
                    self.dep_top_disp_tot[-1] / (self.Np - 1) / self.pitch_a
                )
            )

            # ``dep_theta``: tilt angle of dep. lanes.
            # Note that ``theta`` is stored as a positive value.
            # A ``dep_theta`` of zero refers to channel axis.
            # A positive ``dep_theta`` refers to a dep lane still having
            # the same "overall" direction similar to bulk of DLD.
            # A negative ``dep_theta`` refers to a dep lane having
            # the opposite overall direction compared to bulk of DLD.
            self.dep_theta.append(self.theta + self.dep_theta_dev[-1])

        # -------------------------------------------
        # set up the acc rotations and displacements
        # -------------------------------------------
        self.acc_top_disp_tot = []
        self.acc_theta_dev = []
        self.acc_theta = []
        for sn, gap_dev_nd in enumerate(self.acc_top_gap_deviation_nondim):
            if sn == 0:
                self.acc_top_disp_tot.append(0.0)
            else:
                self.acc_top_disp_tot.append(self.acc_top_disp_tot[-1])

            # A positive displacement is towards outwad of DLD core; i.e.
            # increasing the gap of boundary lanes
            self.acc_top_disp_tot[-1] += gap_dev_nd * self.gap_w

            # A positive rotation direction is towards outwad of DLD core;
            # i.e. increasing the gap of boundary lanes.
            self.acc_theta_dev.append(
                np.arctan(
                    self.acc_top_disp_tot[-1] / (self.Np - 1) / self.pitch_a
                )
            )

            # ``acc_theta``: tilt angle of acc. lanes.
            # Note that ``theta`` is stored as a positive value.
            # An ``acc_theta`` of zero refers to the channel axis.
            # A positive ``acc_theta`` refers to an acc. lane still having
            # the same overall direction compared to bulk of DLD.
            # A negative ``acc_theta`` refers to an acc. lane having
            # the opposite overall direction compared to bulk of DLD.
            self.acc_theta.append(self.theta - self.acc_theta_dev[-1])

    def _prep(
        self,
    ):
        """Configuring the entities of DLD core.

        Although this configuration can be modified as needed in child class
        of ``DLD``, for example, by applying a rotation and/or mirror
        transformation to the system, a specific reference scheme is laid
        down, herein, to build the DLD core in a parameterized fashion. Some
        key notes on the reference scheme:
            - The channel axis is vertical with top being upstream and bottom
            being downstream sides of core.
            - The depletion side is on the left and the accumulation side is
            on the right.
        """

        # shift factor of DLD
        shift = self.pitch_w / self.Np

        # ------------------------------------------------------------
        # position of core entities, i.e., excluding dep./acc. lanes
        # ------------------------------------------------------------

        # left side of mirror -- Core dots (excluding boundaries)
        tmp = []
        for i in range(self.Np + 1):
            y = self.ll[1] + i * self.pitch_a
            for j in range(self.core_dots_num_pillars_per_row):
                x = self.ll[0] + j * self.pitch_w - i * shift
                tmp.append([x, y])

        # extra entities on topmost row on the left side of mirror axis as
        # well as on the mirror axis
        for this_sn in range(self.acc_num_lanes + 1):
            y = self.ll[1] + self.Np * self.pitch_a
            x = (
                self.ll[0]
                + self.core_dots_num_pillars_per_row * self.pitch_w
                - self.Np * shift
                + self.pitch_w * (this_sn)
            )
            tmp.append([x, y])

        self.dots_core_full = np.array(tmp)

        # --------------------------------------------------------------------
        # Entities on depletion boundary lanes
        # --------------------------------------------------------------------
        self.dep_dots_full = []
        self._dep_gap = []  # solely for report and dev.
        for boundary_lane_ind in range(self.dep_num_lanes):
            tmp = []
            self._dep_gap.append([])
            for i in range(self.Np + 1):
                rot_base = [
                    self.ll[0] - self.pitch_w * (boundary_lane_ind + 1),
                    self.ll[1],
                ]
                y_abs = rot_base[1] + i * self.pitch_a
                x_abs = rot_base[0] - i * shift
                r_rel = [x_abs - rot_base[0], y_abs - rot_base[1]]

                # --- dev; to be removed
                dist1 = i * self.pitch_a / np.cos(self.theta)
                dist2 = np.sqrt(
                    (x_abs - rot_base[0]) ** 2 + (y_abs - rot_base[1]) ** 2
                )
                assert np.isclose(
                    dist2, dist1, atol=1e-8, rtol=1e-5
                ), f"""Error in dep-side -- distance calc.
{i}\t{dist1}\t{dist2}"""
                # --------------------------

                if self.boundary_treatment is None:
                    # No special treatment is applied
                    y = y_abs
                    x = x_abs

                elif self.boundary_treatment in ["pow_2", "pow_3", "pow"]:
                    # ---------------------------------------------
                    # Here, 'i' starts from 0 at the downstreammost
                    # row of core. So, it has the opposite
                    # direction of index compared to the work of
                    # Inglis (2009), Feng, et. al. (2017), and Ebadi et. al.
                    # (2019).
                    #
                    # That is:
                    # n = Np - i
                    #
                    # wherein `n` is the row index in above mentioned
                    # works, and `i` is the index in this code.
                    # In the above mentioned works, `n` goes from 1
                    # at the upstreammost row of core to Np
                    # at the downstreammost row of core.
                    # In this code, `i` goes from 0
                    # at the downstreammost row of core to Np-1
                    # at the upstreammost row of core, and to Np
                    # at the next upstream row, which is the downstreammost
                    # row of the next upstream core and will be discarded
                    # from the core DLD.
                    #
                    # post_x_deviation/gap_w=1-(n.eps)^(1./pow_val)
                    # ---------------------------------------------
                    x = x_abs + self.gap_w * (
                        1 - ((self.Np - i) / self.Np) ** (1.0 / self.pow_val)
                    )
                    y = y_abs

                elif self.boundary_treatment == "3d":
                    # ---------------------------------------------
                    # Similar to above, direction of index
                    # is opposite of that in Inglis (2020):
                    # n = Np - i
                    # ---------------------------------------------
                    row = self.Np - i
                    acc_Nth_lat = False
                    dep_side = True
                    args = (
                        self.Np,
                        self.pitch_w * 1e-6,
                        self.pitch_a * 1e-6,
                        self.gap_w * 1e-6,
                        self.gap_a * 1e-6,
                        self.height * 1e-6,
                        dep_side,
                        row,
                        self.phi,
                        acc_Nth_lat,
                    )

                    this_gap = get_gap_with_pressure_balance(
                        *args,
                        estimate=self.pitch_w * 1e-6,
                        verbose=False,
                    )

                    if this_gap < 0:
                        raise ValueError(
                            f"""Error:
`gap_w` for row {row} of dep. boundary is negative: {this_gap}.
Please, take note of the configurations and report this bug."""
                        )

                    x = x_abs + (self.gap_w - this_gap * 1.0e6)
                    y = y_abs

                elif self.boundary_treatment == "mlb":
                    # ---------------------------------------------------------
                    # Note:
                    #
                    # For a counter-clockwise rotation of angle alpha:
                    # transformation matrix:
                    # [cos(alpha), -sin(alpha); sin(alpha), cos(alpha)]
                    #
                    # For depletion lanes on left side of mirror axis,
                    # positive direction of rotation is counter-clockwise.
                    # ---------------------------------------------------------
                    x = (
                        rot_base[0]
                        + r_rel[0]
                        * np.cos(self.dep_theta_dev[boundary_lane_ind])
                        - r_rel[1]
                        * np.sin(self.dep_theta_dev[boundary_lane_ind])
                    )
                    y = y_abs

                else:
                    raise ValueError(
                        f"""Invalid ``boundary_treatment``:
{self.boundary_treatment}"""
                    )

                # adding entity coords to list
                tmp.append([x, y])

                # adding gap to list
                self._dep_gap[-1].append(self.gap_w - (x - x_abs))

            self.dep_dots_full.append(np.array(tmp))

        # --------------------------------------------------------------------
        # Entities on accumulation boundary lanes
        # --------------------------------------------------------------------
        self.acc_dots_full = []
        self._acc_gap = []  # solely for report and dev.
        for boundary_lane_ind in range(self.acc_num_lanes):
            tmp = []
            self._acc_gap.append([])
            for i in range(self.Np):
                rot_base = [
                    self.ll[0]
                    + (self.core_dots_num_pillars_per_row) * self.pitch_w
                    + self.pitch_w * (boundary_lane_ind),
                    self.ll[1],
                ]
                y_abs = rot_base[1] + i * self.pitch_a
                x_abs = rot_base[0] - i * shift
                r_rel = [x_abs - rot_base[0], y_abs - rot_base[1]]

                # --- dev; to be removed
                dist1 = i * self.pitch_a / np.cos(self.theta)
                dist2 = np.sqrt(
                    (x_abs - rot_base[0]) ** 2 + (y_abs - rot_base[1]) ** 2
                )
                assert np.isclose(
                    dist2, dist1, atol=1e-8, rtol=1e-5
                ), f"""Error in acc-side -- distance calc.
{i}\t{dist1}\t{dist2}"""
                # --------------------------

                if self.boundary_treatment is None:
                    # No special treatment is applied
                    y = y_abs
                    x = x_abs

                # The following to be applied for certain situations:
                # - 3d model on non-usm rows (i!=0)
                # - Any model including 3d on usm row (i==0) only if pressure
                # balance is needed: ``opt_acc_balance_pressure==True``
                elif (self.boundary_treatment == "3d" and i != 0) or (
                    self.opt_acc_balance_pressure and i == 0
                ):
                    # ---------------------------------------------
                    # Similar to above:
                    # n = Np - i
                    # ---------------------------------------------
                    row = self.Np - i
                    acc_Nth_lat = False
                    dep_side = False
                    args = (
                        self.Np,
                        self.pitch_w * 1e-6,
                        self.pitch_a * 1e-6,
                        self.gap_w * 1e-6,
                        self.gap_a * 1e-6,
                        self.height * 1e-6,
                        dep_side,
                        row,
                        self.phi,
                        acc_Nth_lat,
                    )
                    this_gap = get_gap_with_pressure_balance(
                        *args,
                        estimate=self.pitch_w * 1e-6,
                        verbose=False,
                    )

                    if this_gap < 0:
                        raise ValueError(
                            f"""Error:
`gap_w` for row {row} of acc. boundary is negative: {this_gap}.
Please, take note of the configurations and report this bug."""
                        )
                    elif this_gap * 1.0e6 < self.gap_w:
                        print(
                            f"""Warning:
The ``phi`` value ({self.phi}) seems to be too low for the current
geometrical configuration, as a result of which the axial gap of upstreammost
row next to accumulation sidewall ({this_gap*1e6:.3f}) is smaller than the
bulk value ({self.gap_w}).
While the pressure balance is still valid, this may not be a good design; gaps
next to accumulation sidewall should be at least equal to that of the bulk
grid.
                            """
                        )

                    x = x_abs + (-self.gap_w + this_gap * 1.0e6)
                    y = y_abs

                    # --- lateral resistance on upstreammost row
                    if row == self.Np and self.acc_usm_gap_a_widening is None:
                        acc_Nth_lat = True
                        args = (
                            self.Np,
                            self.pitch_w * 1e-6,
                            self.pitch_a * 1e-6,
                            self.gap_w * 1e-6,
                            self.gap_a * 1e-6,
                            self.height * 1e-6,
                            dep_side,
                            row,
                            self.phi,
                            acc_Nth_lat,
                        )
                        this_gap = get_gap_with_pressure_balance(
                            *args,
                            estimate=self.pitch_a * 1e-6,
                            verbose=False,
                        )

                        if this_gap < 0:
                            raise ValueError(
                                f"""Error:
`this_gap` for lateral resistance of row {row} of acc. boundary is negative:
{this_gap}.
Please, take note of the configurations and report this bug."""
                            )
                        elif this_gap * 1.0e6 < self.gap_a:
                            print(
                                f"""Warning:
The ``phi`` value ({self.phi}) seems to be too high for the current
geometrical configuration, as a result of which no gap widening is needed
in lateral direction of upstreammost row next to accumulation sidewall.
In fact, the required lateral gap is {this_gap*1e6:.3f}, which is smaller than
the original lateral gap of bulk grid ({self.gap_a}).
In the case that the difference between these values is large, the phi value
should be adjusted to reduce the difference as much as possible for more
accurate pressure balance in this region.
                            """
                            )

                        self.acc_usm_gap_a_widening = max(
                            0.0, this_gap * 1.0e6 - self.gap_a
                        )

                elif self.boundary_treatment in ["pow_2", "pow_3", "pow", "3d"]:
                    # post_x_deviation/gap_w=-1+(2-n.eps)^(1/pow_val)
                    # for i=0: gives x=x_abs (no deviation from bulk)
                    x = x_abs + self.gap_w * (
                        -1
                        + (2.0 - (self.Np - i) / self.Np)
                        ** (1.0 / self.pow_val)
                    )
                    y = y_abs

                elif self.boundary_treatment == "mlb":
                    # ---------------------------------------------------------
                    # Note:
                    #
                    # For a counter-clockwise rotation of angle alpha:
                    # transformation matrix:
                    # [cos(alpha), -sin(alpha); sin(alpha), cos(alpha)]
                    # For accumulation lanes on left side of mirror axis,
                    # positive direction of rotation is clockwise.
                    # ---------------------------------------------------------
                    x = (
                        rot_base[0]
                        + r_rel[0]
                        * np.cos(self.acc_theta_dev[boundary_lane_ind])
                        + r_rel[1]
                        * np.sin(self.acc_theta_dev[boundary_lane_ind])
                    )
                    y = y_abs

                else:
                    raise ValueError(
                        f"""Invalid ``boundary_treatment``:
{self.boundary_treatment}"""
                    )

                # adding entity coords to list
                tmp.append([x, y])

                # adding gap to list
                self._acc_gap[-1].append(self.gap_w + (x - x_abs))

            self.acc_dots_full.append(np.array(tmp))

        # --------------------------------------------------------------------
        # preparing attributes needed by child classes to construct a dld
        # system
        # --------------------------------------------------------------------

        # removing the most upstream row of entities from dep boundary lanes
        # If this row is included when arraying this DLD building block in
        # the child classes, it overlaps the most downstream
        # row of the neighboring upstream DLD core.
        concat_arr = np.concatenate([*self.dep_dots_full], axis=1)[:-1]
        self.dep_dots = np.hsplit(concat_arr, self.dep_num_lanes)

        # for consistency, `acc_dots` is assigned while it is
        # the same as `acc_dots_full`
        self.acc_dots = self.acc_dots_full

        # ``dots_core_core_full``: all entities of core of DLD core, i.e.,
        # excluding the dep. and acc. lanes, with the correct periodicity of
        # DLD core (``Np``);
        # discarding the row # ``Np`` which becomes the most downstream row
        # (#0) of the upper neighboring DLD core when arraying this DLD core.
        self.dots_core_core_full = self.dots_core_full[
            : self.Np * (self.core_dots_num_pillars_per_row)
        ]

        # --------------------------------------------------------------------
        # x_mirror is an important parameter when building sidewalls of DLD
        # core. For example:
        # if opt_mirror from a child class is True, then
        # mirroring could be done around x.mirr=acc_dots_full[-1][0,0]
        # --------------------------------------------------------------------
        self.x_mirror = self.acc_dots_full[-1][0, 0]

        # --------------------------------------------------------------------
        # ``_dots_full_wo_mirror``: a full set (``Np+1`` rows ranging from 0
        # to ``Np``) of DLD entities including those related to regions
        # 1. core, 2. depletion, and 3. accumulation.
        #
        # ``_dots_full_w_mirror``: union of ``_dots_full_wo_mirror`` and its
        # mirror.
        #
        # ``_dots_full_wo_mirror`` and ``_dots_full_w_mirror`` to be used for
        # the purposes of visualization using the ``plot()`` method,
        # debugging, and model development. They are not meant to be used by
        # child classes.
        # --------------------------------------------------------------------
        self._dots_full_wo_mirror = np.concatenate(
            [
                self.dots_core_full,
                np.concatenate(self.dep_dots_full, axis=0),
                np.concatenate(self.acc_dots_full, axis=0),
            ],
            axis=0,
        )

        _dots_full_mirrored = self.mirror(
            self._dots_full_wo_mirror,
            x_mirror=self.x_mirror,
        )
        self._dots_full_w_mirror = np.concatenate(
            [
                self._dots_full_wo_mirror,
                _dots_full_mirrored,
            ],
            axis=0,
        )

        # ---------------------------------------------------------------
        # Final sanity check
        # ---------------------------------------------------------------
        if (
            self._max_allowed_lateral_gap_widening_nondim < 0
            or self._max_allowed_lateral_gap_widening_nondim >= 2
        ):
            print(
                f"""The ``_max_allowed_lateral_gap_widening_nondim`` is
{self._max_allowed_lateral_gap_widening_nondim}, while it is expected to be in
the range of [0, 2)."""
            )

            raise ValueError(
                """Invalid parameter:
'_max_allowed_lateral_gap_widening_nondim'"""
            )

        max_allowed_lateral_gap_cut = (
            self._max_allowed_lateral_gap_widening_nondim * self.side_length_a
        )
        if self.acc_usm_gap_a_widening is not None:
            if self.acc_usm_gap_a_widening > max_allowed_lateral_gap_cut:
                print(
                    f"""Note:
`acc_usm_gap_a_widening` is {self.acc_usm_gap_a_widening}, which is greater
than maximum allowed widening: {max_allowed_lateral_gap_cut}.
The maximum allowed value is conidered instead. The maximum limit can also be
adjusted through ``_max_allowed_lateral_gap_widening_nondim`` as needed."""
                )
                self.acc_usm_gap_a_widening = max_allowed_lateral_gap_cut
        # ---------------------------------------------------------------

    def _get_dc(
        self,
    ):
        """Returning the critical diameter."""

        return DLD.get_dc(
            Np=self.Np,
            gap_w=self.gap_w,
            pitch_w=self.pitch_w,
            pitch_a=self.pitch_a,
        )

    def mirror(
        self,
        dots: Union[list, tuple, np.ndarray],
        x_mirror=None,
        tol=1e-10,
    ):
        """Mirroring a set of entities wrt. a given mirror axis.

        Parameters
        ----------
        dots : Union[list, tuple, np.ndarray]
            Entities to be mirrored
        x_mirror : float or NoneType, optional
            Mirror axis ``x=x_mirror``, by default None
        tol : float, optional
            Tolerance: entities on the right side of ``x=x_mirror-tol`` are
            ignored, by default 1e-10

        Returns
        -------
        np.ndarray
            Mirrored entities.
        """
        dots = np.array(dots)
        if x_mirror is None:
            x_mirror = self.x_mirror

        tmp = []
        for sn, item in enumerate(dots.copy()):
            x = item[0]
            y = item[1]

            if x_mirror - x > tol:
                x = x_mirror + (x_mirror - x)
                tmp.append([x, y])

        return np.array(tmp)

    def write(self, fname):
        """Writing coordinates of entities to a file.

        Parameters
        ----------
        fname : str
            A (csv) filename with extension (can include a path).
        """
        import csv  # not needed if writing is revised.

        dots = np.concatenate(
            [
                self.dots_core_core_full,
                np.concatenate(self.dep_dots, axis=0),
                np.concatenate(self.acc_dots_full, axis=0),
            ],
            axis=0,
        )

        with open(fname, "w", newline="") as fp:
            writer = csv.writer(fp, delimiter=",")
            for dot in dots:
                writer.writerow(
                    [
                        dot[0],
                        dot[1],
                    ]
                )

    def plot(self, fname=None, opt_mirror=False, **kwargs):
        """Plotting the entities.

        Parameters
        ----------
        fname : str or NoneType, optional
            A (png) filename with extension (can include a path), by default
            None
        opt_mirror : bool, optional
            Whether to plot the entities together with their mirrored ones, by
            default False
        """
        import matplotlib.pyplot as plt

        markersize = kwargs.pop("markersize", 3)
        markeredgewidth = kwargs.pop("markeredgewidth", 0.1)

        if opt_mirror:
            dots = self._dots_full_w_mirror
        else:
            dots = self._dots_full_wo_mirror

        fig = plt.figure(**kwargs)
        plt.plot(
            dots[:, 0],
            dots[:, 1],
            ".",
            markersize=markersize,
            markeredgewidth=markeredgewidth,
            markeredgecolor="black",
        )
        fig.axes[0].set_aspect(1.0)

        if fname is not None:
            plt.savefig(
                fname,
                bbox_inches="tight",
            )

    def get_boundary_gaps(
        self,
    ):
        """Get the dep. and acc. boundary gaps.

        Returns
        -------
        dict
        """
        boundary_gaps = {
            "dep": self.get_dep_gaps(),
            "acc": self.get_acc_gaps(),
            "acc_usm_gap_a_widening": self.acc_usm_gap_a_widening,
        }

        return boundary_gaps

    def get_dep_gaps(
        self,
    ):
        """Get the dep. boundary gaps."""

        return np.array(self._dep_gap)

    def get_acc_gaps(
        self,
    ):
        """Get the acc. boundary gaps."""

        return np.array(self._acc_gap)

    # ------------------------------------------------------------------------
    # Static methods
    # ------------------------------------------------------------------------

    @staticmethod
    def get_dc(
        Np,
        gap_w,
        pitch_w=None,
        pitch_a=None,
    ):
        """Returning the critical diameter."""

        eps = 1.0 / Np

        # --- The following may need to be revisited for asym. structures
        if pitch_a is not None and pitch_w is not None:
            eps *= pitch_a / pitch_w

        return 1.4 * gap_w * eps**0.48

    @staticmethod
    def get_geom_config_auto(
        Np=None,
        d_c=None,
        width=None,
        Nw=None,
        gap_w=None,
        gap_a=None,
        pitch_w=None,
        pitch_a=None,
        height=None,
    ):
        """Get a full set of geometrical attributes after applying any\
        configurations that may be needed automatically."""

        # --- Np: periodicity
        if Np is not None:
            this_Np = Np
        else:
            this_Np = 20

        # --- gap_w
        this_gap_w = gap_w
        if this_gap_w is None:
            if d_c is not None:  # automation from critical diameter
                this_gap_w = d_c / 1.4 / (1 / this_Np) ** 0.48
            elif gap_a is not None:
                this_gap_w = gap_a
            elif pitch_w is not None:
                this_gap_w = pitch_w / 2.0
            elif pitch_a is not None:
                this_gap_w = pitch_a / 2.0
            else:
                raise ValueError(
                    """At least one of ``gap_w``, ``gap_a``,
``pitch_w``, ``pitch_a``, and ``d_c`` must be provided."""
                )

        # --- pitch_w
        this_pitch_w = pitch_w
        if this_pitch_w is None:
            this_pitch_w = 2 * this_gap_w

        # --- gap_a & pitch_a
        # the case that neither of `pitch_a` and `gap_a` is given
        if pitch_a is None and gap_a is None:
            this_gap_a = this_gap_w
            this_pitch_a = this_pitch_w

        # the case that only `gap_a` is given -- axial sidelength of entity is
        # set equal to lateral one.
        elif pitch_a is None and gap_a is not None:
            this_gap_a = gap_a
            this_pitch_a = this_pitch_w - this_gap_w + gap_a

        # the case that only `pitch_a` is given -- axial sidelength of entity
        # is set equal to lateral one.
        elif pitch_a is not None and gap_a is None:
            this_pitch_a = pitch_a
            this_gap_a = this_gap_w + pitch_a - this_pitch_w

        # the case that both `pitch_a` and `gap_a` are given -- different
        # axial and lateral sidelengths are enabled herein.
        else:
            this_gap_a = gap_a
            this_pitch_a = pitch_a

        # representations of sidelength of entity along the channel axis and
        # along the width of channel.
        this_side_length_w = this_pitch_w - this_gap_w
        this_side_length_a = this_pitch_a - this_gap_a

        # --- height of pillars
        this_height = height
        if this_height is None:
            this_height = 4 * this_gap_w  # assuming high aspect-ratio pillars

        # --------------------------------------------------------------------
        # Nw: number of fluidic lanes/columns --- Minimize Nw for the given Np
        # --------------------------------------------------------------------
        if width is not None:
            # --- sanity check
            if Nw is not None:
                if Nw != np.ceil(width / this_pitch_w):
                    raise ValueError(
                        f"""Both ``Nw`` and ``width`` are
provided, and are inconsistent:
Nw={Nw} and width={width}.
The latter requires Nw of {int(np.ceil(width/this_pitch_w))}
in presence of pitch_w: {this_pitch_w}"""
                    )
            # -----------------
            this_Nw = int(np.ceil(width / this_pitch_w))

        elif Nw is not None:
            this_Nw = Nw
        else:
            this_Nw = 10

        # --- params to update after auto config execution
        dict_to_return = {}
        dict_to_return["Np"] = this_Np
        dict_to_return["Nw"] = this_Nw
        dict_to_return["gap_w"] = this_gap_w
        dict_to_return["gap_a"] = this_gap_a
        dict_to_return["pitch_w"] = this_pitch_w
        dict_to_return["pitch_a"] = this_pitch_a
        dict_to_return["height"] = this_height
        dict_to_return["side_length_w"] = this_side_length_w
        dict_to_return["side_length_a"] = this_side_length_a

        return dict_to_return
