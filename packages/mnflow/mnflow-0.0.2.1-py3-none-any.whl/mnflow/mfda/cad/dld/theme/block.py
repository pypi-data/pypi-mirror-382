# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


"""DLD-based sytem | Theme: Block"""

import copy
import pprint

import klayout.db as db
import numpy as np

from mnflow.mfda.cad.components.element import Element
from mnflow.mfda.cad.components.multichannel import Multi_IO
from mnflow.mfda.cad.components.utils import filter_with_sidewall
from mnflow.mfda.cad.components.utils import grating_with_sidewall
from mnflow.mfda.cad.components.utils import pad_light
from mnflow.mfda.cad.dld.theme.core import DLD as core_DLD
from mnflow.mfda.cad.dld.theme.sidewall import lst_get_sidewall_acc
from mnflow.mfda.cad.dld.theme.sidewall import lst_get_sidewall_dep
from mnflow.mfda.cad.utils.common import merge_two_dicts
from mnflow.mfda.cad.utils.common import resist_channel
from mnflow.mfda.cad.utils.common import resist_dld
from mnflow.mfda.cad.utils.common import vfr_SI_to_ml_per_hr
from mnflow.mfda.cad.utils.common import vfr_SI_to_ul_per_min
from mnflow.mfda.cad.utils.inspections import bbox
from mnflow.mfda.cad.utils.operations import generic_array
from mnflow.mfda.cad.utils.operations import reverse_tone
from mnflow.mfda.cad.utils.shapes import beam_c
from mnflow.mfda.cad.utils.shapes import beam_i
from mnflow.mfda.cad.utils.shapes import beam_l
from mnflow.mfda.cad.utils.shapes import beam_t
from mnflow.mfda.cad.utils.shapes import circle
from mnflow.mfda.cad.utils.shapes import generic_shape
from mnflow.mfda.cad.utils.shapes import polygon
from mnflow.mfda.cad.utils.shapes import rectangle
from mnflow.mfda.cad.utils.shapes import square
from mnflow.mfda.cad.utils.shapes import triangle


class DLD(Element, core_DLD):
    """A standard uniform DLD system with optional components, e.g.,
    multi-inlet, filter, preload, sideway collections, and full width
    collection channels.
    It can be configured flexibly with numerous parameters.
    The class inherits from ``core.DLD`` and aims at configuring how to array
    the DLD core to make a more complex DLD design and/or a full DLD device.
    It can be used as a component (Element) in other classes to build other
    architectures, `e.g.`, multi-stage, condenser-and-sorter, etc.

    .. note::
        Similar to ``core.DLD``, herein, the parameters are attempted to be
        assigned automatically for a **reference** design so that user can
        conveniently produce a CAD file for a target DLD system by providing
        as few args as possible (at least, that is the goal!). Regardless,
        user should be able to pass valid args to adjust details of design as
        needed.
        For example, if no value is passed for ``num_unit``, an appropriate
        value is set based on the
        number of fluidic lanes ``Nw`` and additional number of units
        configured from ``num_unit_extra`` and/or ``num_unit_extra_nondim`` as
        a safety margin for full-width injection schemes.
        As another example, the **standardized** design, hererin, does not
        mirror the features wrt.
        a line along the channel axis next to the accumulation sidewall.
        However, a `mirrored design` can be produced by passing
        ``opt_mirror=True``.


    .. note::
        Order of processes and pertinent parameters:

        - Standard DLD structure & mirrored design if ``opt_mirror`` is True.
        - Add any up-/down-stream component as needed, `e.g.`,\
        ``opt_multi_inlet=True``, ``opt_filter=True``, ``opt_preload=True``,\
        ``opt_collection=True``, ``opt_collection_sideway_right_side=True``,\
        ``opt_collection_sideway_left_side=True``, etc.
        - Mirror.x for the case that ``opt_mirror_x=True``
        - Mirror.y for the case that ``opt_mirror_y=True``
        - Rotation for the case that a valid value is provided for\
        ``rotation_angle_deg_before_array``.
        - Arraying (and Mirroring) if ``sum(array_counts)>2``:
            - Check if mirroring is needed from ``opt_mirror_before_array``.
            - Configure spacing between mirrors from\
            ``spacing_between_mirrors_before_array``.
            - Configure spacing between copies from ``array_spacing``.
        - Apply padding if ``opt_padding_features=True`` (mainly for\
        nanoimprint lithography (NIL)).
        - Set lower left coordinates if a valid ``target_ll`` is given.

    .. note::
        - Some parameters are None by default, which means the program\
        attempts to infer appropriate values based on the other configurations.
        - Some parameters are dimensionless as described in Parameters\
        Section.
        - The length unit for dimensional parameters is micron unless\
        otherwise stated.

    .. important::
        When optimizing params by applying constraints, remove any component
        that can be potentially added to system, `e.g.`, up-/downstream
        components of preload, filter, collection, etc., because:

        - The current implementation of constraints considers solely the\
        areas with DLD pillars when calculating dimensions, area, flow\
        rate, etc.
        - It probably makes sense to do so!

    .. caution::
        The current implementation of constraints is relatively slow; it may
        take up to several seconds depending on system config. The underlying
        reason is that it attempts to scan the whole parameter space
        sequentially. More efficient algorithms, `e.g.`, bisection, etc.,
        can be applied in the future to improve the performance.

    .. important::
        (For developers) Some of the long list of params may be grouped into
        several dictionaries.
        For example, currently, filter component can get several args including
        ``filter_len_nondim``, ``filter_half_pitch_nondim``,
        ``filter_margin_top``, ``filter_margin_top_nondim``,
        ``filter_offset_w``, etc.
        They can be grouped into a single config param similar to that for
        multi-inlet component, `i.e.`, ``config_multi_inlet``.
        However, the current version, `i.e.`, passing each single param
        separately may be more user-friendly.
    """

    # built-in profile shapes for pillars
    CORE_SHAPE = {
        "circle": circle,
        "triangle": triangle,
        "rectangle": rectangle,
        "square": square,
        "beam_c": beam_c,
        "beam_t": beam_t,
        "beam_i": beam_i,
        "beam_l": beam_l,
    }

    # ------------------------------------------------------------------
    # auto geometrical attr
    #
    # list of params from ``core.DLD`` and ``block.DLD`` required to
    # be taken into account to determine a full set of geometrical
    # configurations automatically.
    # ------------------------------------------------------------------

    # core.DLD param to be auto determined
    lst_param_auto_core = list(
        core_DLD.get_geom_config_auto.__code__.co_varnames[
            : core_DLD.get_geom_config_auto.__code__.co_argcount
        ]
    )

    # block params needed for auto design of core.DLD (mainly for constraints
    # evaluation)
    lst_param_auto_block = [
        # considerations
        "num_unit_extra",
        "num_unit_extra_nondim",
        "fluid_mu",
    ]

    def __init__(
        self,
        # Config shape of core entities
        core_shape=None,
        core_shape_rot_angle=None,
        num_points_per_circle=None,
        # General
        num_unit=None,
        sidewall_width=None,
        opt_mirror=None,
        spacing_between_mirrors_within_single_unit=None,
        dot_offset=None,
        target_ll=None,
        opt_smoothen_dep_sidewall=None,
        opt_reverse_tone=None,
        # Optional components
        opt_multi_inlet=None,
        opt_filter=None,
        opt_preload=None,
        opt_collection=None,
        opt_collection_sideway_right_side=None,
        opt_collection_sideway_left_side=None,
        # Potential transformations before mirror/array
        opt_mirror_x=None,
        opt_mirror_y=None,
        rotation_angle_deg_before_array=None,
        # Mirror/Array
        array_counts=None,
        array_spacing=None,
        opt_mirror_before_array=None,
        spacing_between_mirrors_before_array=None,
        mirror_before_array_around_negative_edge=None,
        # Cover on acc side
        opt_cover_acc=None,
        acc_cover_half_width_min=None,
        acc_cover_excess_width_over_gap_w=None,
        # Optional addtional row capping the topmost DLD unit
        opt_cap_top_row=None,
        cap_top_row_block_width_acc_side=None,
        cap_top_row_block_width_dep_side=None,
        # Multi_inlet
        config_multi_inlet=None,
        # Filter
        filter_shape=None,
        filter_preload_spacing=None,
        filter_len_nondim=None,
        filter_half_pitch_nondim=None,
        filter_margin_top=None,
        filter_margin_top_nondim=None,
        filter_offset_w=None,
        filter_block_width_acc_side=None,
        filter_block_width_dep_side=None,
        # Preload
        preload_offset_w=None,
        preload_offset_a=None,
        preload_bar_pitch=None,
        preload_bar_dims=None,
        preload_margin_top=None,
        preload_margin_top_nondim=None,
        preload_block_width_acc_side=None,
        preload_block_width_dep_side=None,
        # Collection
        collection_margin_top_nondim=None,
        opt_collection_with_via=None,
        # -- Simple collection
        collection_bar_pitch_nondim=None,
        collection_bar_dims=None,
        collection_offset_w=None,
        collection_offset_a=None,
        # --- Sideway collection
        collection_sideway_width=None,
        # -- Collection with via
        via_dia=None,
        via_dia_outer_ring=None,
        via_dia_outer_ring_over_via_dia=None,
        vias_spacing_min=None,
        zz_width_to_width_tot=None,
        zz_len_downstream_init_extension=None,
        zz_len_downstream_bottom=None,
        zz_len_upstream=None,
        zz_len_downstream=None,
        zz_bar_pitch_nondim=None,
        zz_bar_gap_over_gap_w=None,
        zz_bar_offset_w=None,
        zz_ds_top_win__topright_tip_width_large=None,
        zz_ds_top_win__topright_tip_width_small=None,
        bmp_bar_pitch_nondim=None,
        bmp_bar_gap_over_gap_w=None,
        bmp_bar_offset_w=None,
        opt_report_collection=None,
        # -- Decorative entities inside collection component for NIL
        collection_entity_dim=None,
        collection_entity_pitch_out=None,
        collection_entity_pitch_in=None,
        # -- Geom config for 1D model
        height_deep=None,
        bus_width=None,
        bus_length=None,
        # Padding for NIL
        opt_padding_features=None,
        layer_padding=None,
        padding_width=None,
        padding_entity_dim=None,
        padding_entity_pitch=None,
        opt_padding_reverse_tone=None,
        # Relatively detailed config params
        # --- Callback function to generate entities with arbitrary profile
        core_entity_func=None,
        kwargs_entity_gen=None,
        # --- Callback function for additional regions to be inserted
        single_unit_extra_shapes=None,
        # --- Misc.
        dep_sidewall_theme=None,
        acc_sidewall_theme=None,
        top_cell_name=None,
        layer_1=None,
        layer_2=None,
        beam_thickness=None,
        verbose=None,
        opt_process_upon_init=None,
        opt_write_upon_init=None,
        opt_save_image=None,
        use_top_cell_if_exists=None,
        # Considerations for design automation
        num_unit_extra=None,
        num_unit_extra_nondim=None,
        get_geom_config_auto_use_auto_num_unit=None,
        # Constraints for design automation
        range_Np=None,
        range_Nw=None,
        range_width=None,
        range_length=None,
        # --- Volumetric flow rate (vfr)
        min_vfr_per_bar=None,
        min_vfr_ul_per_min_per_bar=None,
        min_vfr_ml_per_hr_per_bar=None,
        fluid_mu=None,
        # --- Die area (mm square)
        max_die_area_mmsq=None,
        # --- Gap over critical dia.
        min_gap_over_dc=None,
        # --- Constraint OFF mode
        turn_off_constraints=None,
        *args,
        **kwargs,
    ):
        """
        **Constructor**

        Parameters
        ----------
        **Config shape of core entities**

        core_shape : str, optional
            Shape of DLD entities (pillars), e.g. 'circle', 'triangle',
            'rectangle', etc., by default None, `i.e.`, 'circle'
        core_shape_rot_angle : float, optional
            Rotational angle (deg.) to be applied to DLD entities
            counter-clockwise, by default 0.
        num_points_per_circle : int, optional
            Number of points/vertices in a polygon representing circular
            entities, by default 32

        **General**

        num_unit : int, optional
            Number of DLD units (core.DLD) arrayed along the channel, by
            default None
        sidewall_width : float, optional
            Width of sidewalls, by default None
        opt_mirror : bool, optional
            Whether to have a mirrored design, by default False
        spacing_between_mirrors_within_single_unit : float, optional
            Spacing between mirrors within a single unit when ``opt_mirror``
            is true, by default 0.
        dot_offset : list, optional
            Offset of core DLD entities in each direction, by default [0, 0]
        target_ll : list, optional
            Desired lower left coordinates of bounding box of entire system
            at the end, by default None
        opt_smoothen_dep_sidewall : bool, optional
            Whether to smooth out the dep. sidewall downstream of system, by
            default False
        opt_reverse_tone : bool, optional
            Whether to reverse the tone of layout, which may be desirable for
            some manufacturing techniques and/or photoresist tones, by default
            False

        **Optional components**

        opt_multi_inlet : bool, optional
            Whether to include a multi-inlet upstream of system, can be
            configured to serve as a single-inlet as well, by default False
        opt_filter : bool, optional
            Whether to include a filter upstream of system, by default False
        opt_preload : bool, optional
            Whether to include a preload upstream of system, by default False
        opt_collection : bool, optional
            Whether to include a collection component downstream of system, by
            default False
        opt_collection_sideway_right_side : bool, optional
            Whether to include a sideway collection component with opening on
            right side downstream of system, byt default False
        opt_collection_sideway_left_side : bool, optional
            Whether to include a sideway collection component with opening on
            left side downstream of system, byt default False

        **Potential transformations before mirror/array**

        opt_mirror_x : bool, optional
            Whether to mirror the DLD unit around x axis before mirror/array,
            by default False
        opt_mirror_y : bool, optional
            Whether to mirror the DLD unit around y axis before mirror/array,
            by default False
        rotation_angle_deg_before_array : float, optional
            Rotational angle (deg) for rotatoin of DLD unit
            before mirror/array, by default None

        **Mirror/Array**

        array_counts : list, optional
            Count of DLD units in each direction in case an array of DLD
            units is needed, by default [1, 1]
        array_spacing : list, optional
            Spacing between neighboring DLD units when the original DLD
            unit is arrayed, by default [0, 0]
        opt_mirror_before_array : list, optional
            Whether to mirror DLD unit around each of x and y axes before
            arraying the unit, by default [False, False]
        spacing_between_mirrors_before_array : list, optional
            Spacing between mirrors of DLD unit in each direction before
            arraying them, by default [0, 0]
        mirror_before_array_around_negative_edge : list, optional
            Whether to cosider lower edge of bounding box in each direction if
            mirroring is needed, otherwise the higher edge to be used, by
            default [False, False]

        **Cover on acc side**

        opt_cover_acc : bool, optional
            Whether the accumulation side to be covered with a polygon
            potentially for a smooth profile, by default None
        acc_cover_half_width_min : float, optional
            Length of smaller side of a trapezoidal cover that can potentially
            cover the accumulation sidewall, by default None
        acc_cover_excess_width_over_gap_w : float, optional
            Distance to extend the accumulation side's cover laterally without
            changing the slope of its sides, by default 0.

        **Optional addtional row capping the topmost DLD unit**

        opt_cap_top_row : bool, optional
            Whether adding a row of entities before the most upstream row of
            DLD entities, by default False
        cap_top_row_block_width_acc_side : int, optional
            Width of additional block covering the acc. sidewall on top row,
            by default 0
        cap_top_row_block_width_dep_side : int, optional
            Width of additional block covering the dep. sidewall on top row,
            by default 0

        **Multi_inlet**

        config_multi_inlet : dict, optional
            Config of multi-inlet component, by default None

        **Filter**

        filter_shape : str, optional
            Shape of entities within filter, by default 'square'
        filter_preload_spacing : float, optional
            Spacing between preload and filter, by default None
        filter_len_nondim : int, optional
            Filter length nondimensionalized by pitch of entities, by default
            39
        filter_half_pitch_nondim : int, optional
            Half-pitch of serpentine filter non-dimensionalized by pitch of
            entities, by default 3
        filter_margin_top : float, optional
            Minimum distance between filter inlet and its entities, by default
            None.
        filter_margin_top_nondim : float, optional
            Similar to ``filter_margin_top`` but nondimensionalized by
            ``pitch_a``, by default None.
        filter_offset_w : float, optional
            A parameter enabling the displacement of filter laterally for a
            potentially better configuration, by default 0.
        filter_block_width_acc_side : float, optional
            Width of an additional block used to cover the acc. sidewall of
            filter, by default 0.
        filter_block_width_dep_side : float, optional
            Width of an additional block used to cover the dep. sidewall of
            filter, by default 0.

        **Preload**

        preload_offset_w : float, optional
            A parameter enabling the displacement of preload laterally for a
            potentially better configuration, by default 0.
        preload_offset_a : float, optional
            A parameter enabling the displacement of preload axially for a
            potentially better configuration, by default 0.
        preload_bar_pitch : float, optional
            Pitch of bar array in preload, by default None
        preload_bar_dims : list, optional
            Dimensions of bars in preload, by default None
        preload_margin_top : float, optional
            Minimum distance between preload inlet and its entities, by
            default 0.
        preload_margin_top_nondim : float, optional
            Similar to ``preload_margin_top`` but nondimensionalized by
            ``pitch_a``, by default None.
        preload_block_width_acc_side : float, optional
            Width of an additional block used to cover the acc. sidewall of
            preload, by default 0.
        preload_block_width_dep_side : float, optional
            Width of an additional block used to cover the dep. sidewall of
            preload, by default 0.

        **Collection**

        collection_margin_top_nondim : float, optional
            Spacing between collection entities and DLD post array in
            downstream of system non-dimensionalized by pitch of entities, by
            default 2.
        opt_collection_with_via : bool, optional
            Whether to use the collection-with-via scheme, by default False

        `Simple collection`

        collection_bar_pitch_nondim : float, optional
            Pitch of bars in `simple` collection component non-dimensionalized
            by pitch of entities, by default None
        collection_bar_dims : list, optional
            Dimensions of bars in `simple` collection component in x and y
            directions, by default None
        collection_offset_w : float, optional
            A parameter enabling the displacement of collection channels
            laterally for a potentially better configuration, by default None
        collection_offset_a : float, optional
            A parameter enabling the displacement of collection channels
            axially for a potentially better configuration, by default None

        `Sideway collection`

        collection_sideway_width : float, optional
            Width of sideway collection, by default None

        `Collection with via`

        via_dia : float, optional
            Diameter of through-wafer via, by default None
        via_dia_outer_ring : float, optional
            Diameter of a ring equal to or larger than that of through-wafer
            via centered on via, by default None
        via_dia_outer_ring_over_via_dia : float, optional
            Ratio of diameter of outer ring of via to that of via, by default
            1.2
        vias_spacing_min : float, optional
            Minimum allowed distance between vias, by default 60.
        zz_width_to_width_tot : float, optional
            Ratio of width of zig-zag (zz) collection section to the total
            width of DLD unit; this parameter dictates the concentration
            enhancement ratio, by default 0.9
        zz_len_downstream_init_extension : float, optional
            Distance between the inlet of collection component and the tip of
            its bars, by default 20.
        zz_len_downstream_bottom : int, optional
            Minimum distance between outer ring of via and end of collection
            component downstream of system, by default 50.
        zz_len_upstream : float, optional
            Length of zig-zag collection channels, by default 300.
        zz_len_downstream : float, optional
            Minimum distance between zig-zag collection channels and end of
            collection component downstream of system, by default 400.
        zz_bar_pitch_nondim : float, optional
            Pitch of zig-zag collection bars (channels) non-dimensionalized by
            pitch of DLD entities, by default 3.
        zz_bar_gap_over_gap_w : float, optional
            Ratio of opening of zz collection channels to lateral gap between
            DLD entities, by default 1.75
        zz_bar_offset_w : float, optional
            A parameter enabling the displacement of zz collection channels
            laterally for a potentially better configuration, by default 0.
        zz_ds_top_win__topright_tip_width_large : float, optional
            Width of larger upper right tip of zz sidewall, by default None
        zz_ds_top_win__topright_tip_width_small : float, optional
            Width of smaller upper right tip of zz sidewall, by default None
        bmp_bar_pitch_nondim : float, optional
            Pitch of bars (channels) within bump collection section
            non-dimensionalized by pitch of DLD entities, by default 2.
        bmp_bar_gap_over_gap_w : float, optional
            Ratio of opening of bump collection channels to lateral gap between
            DLD entities, by default 2.
        bmp_bar_offset_w : float, optional
            A parameter enabling the displacement of bump collection channels
            laterally for a potentially better configuration, by default 0.
        opt_report_collection : bool, optional
            Whether to report the modeling/evaluation results regarding the
            design of collection channels to have a better insight on how the
            design would perform and to readjust the configs as needed, by
            default True

        `Decorative entities inside collection component for NIL`

        collection_entity_dim : list, optional
            (Mainly for NIL) Dimensions of decorative unit to be arrayed
            within collection component, by default None
        collection_entity_pitch_out : list, optional
            (Mainly for NIL) Pitch of decorative unit in each direction to be
            arrayed within collection sidewall, by default None
        collection_entity_pitch_in : list, optional
            (Mainly for NIL) Pitch of decorative unit in each direction to be
            arrayed within zz collection channels in fluid connection with via,
            by default None

        `Geom config for 1D model`

        height_deep : float, optional
            Height/Depth of channel in deep region, e.g., inlet/outlet fluidic
            buses, required to evaluate the hydraulic resistance of system and
            performance of design, by default None. Note that ``core.DLD`` has
            a ``height`` parameter that is used as Height/Depth of channel in
            shallow region.
        bus_width : float, optional
            Width of fluidic buses, required to evaluate the hydraulic
            resistance of system and performance of design, by default None
        bus_length : float, optional
            Total length of fluidic buses, required to evaluate the hydraulic
            resistance of system and performance of design, by default None

        **Padding for NIL**

        opt_padding_features : bool, optional
            (NIL) Whether to add decorative features, by default False
        layer_padding : tuple or list, optional
            (NIL) Layer info for padding features, optional.
        padding_width : dict, optional
            (NIL) Padding width of decorative stripes around the design, by
            default {'low': 30, 'right': 30, 'top': 30, 'left': 30, }
        padding_entity_dim : list or tuple, optional
            (NIL) Dimensions of decorative entity, by default None
        padding_entity_pitch : list or tuple, optional
            (NIL) Pitch of decorative entities array in each direction, by
            default None
        opt_padding_reverse_tone : bool, optional
            (NIL) Whether to reverse tone of padding features.

        **Relatively detailed config params**

        `Callback function to generate entities with arbitrary profile`

        core_entity_func : function, optional
            A callback function to generate and return an arbitrary region as
            profile of DLD entities, by default None
        kwargs_entity_gen : dict, optional
            Keyword arguments to pass to arbitrary ``core_entity_func``, by
            default None

        `Callback function for additional regions to be inserted`

        single_unit_extra_shapes : function, optional
            A callback function to generate and return a list of arbitrary
            regions to be inserted inside the DLD unit structure before
            arraying, by default None

        `Misc.`

        dep_sidewall_theme : int, optional
            An identifier denoting a given design of dep. sidewall, by
            default 0
        acc_sidewall_theme : int, optional
            An identifier denoting a given design of acc. sidewall, by
            default 0
        top_cell_name : str
            Name of top cell to be created as needed.
        layer_1 : tuple, optional
            Specs of Layer 1 in layout, by default (1, 0)
        layer_2 : tuple, optional
            Specs of Layer 1 in layout, by default (2, 0)
        beam_thickness : float, optional
            Thickness of beam profile, by default None
        verbose : bool, optional
            verbose, by default True
        opt_process_upon_init : bool, optional
            Whether to invoke the ``process`` method from inside the
            constructor to design the system, by default True
        opt_write_upon_init : bool, optional
            Whether to invoke the ``write`` method from inside the
            constructor to write the GDS/DXF layout file, by default True
        opt_save_image : bool, optional
            Whether to invoke the ``save_image`` method from inside the
            constructor to save layout as png file(s), by default False
        use_top_cell_if_exists : bool, optional
            Whether to use top cell of layout in the case that layout is not
            empty; if False, a top_cell to be created, by default None.

        **Considerations for design automation**

        num_unit_extra : int, optional
            Number of additional DLD units (core.DLD) to be considered to be
            conservative; only relevant if ``num_unit`` is not provided
            explicitly, by default None
        num_unit_extra_nondim : int, optional
            Nondimensional form of ``num_unit_extra_nondim`` --
            nondimensionalized by the theoretical number of units required to
            displace all large particles and collect them next to the
            accumulation sidewall, only relevant if ``num_unit`` and
            ``num_unit_extra`` are not provided explicitly, by default None
        get_geom_config_auto_use_auto_num_unit : bool, optional
            Whether to consider a **full** DLD system when evaluating the
            constraints regardless of any explicitly provided ``num_unit``; if
            False, constraints will be applied by considering the explicitly
            provided ``num_unit``; setting this param to True can be useful
            when constraints should be evaluated for a full system, but the
            mask should be prepared for a partial system, `e.g.`, for
            computational modeling where one to a few units would suffice, by
            default False.

        **Constraints for design automation**

        range_Np : list, optional
            Min and Max allowed Np for the structure, by default None.
        range_Nw : list, optional
            Min and Max allowed Nw for the structure, by default None.
        range_width : list, optional
            Min and Max allowed width of structure, by default None.
        range_length : list, optional
            Min and Max allowed length of overall DLD system in the case that
            a **full** DLD is to be constructed, by default None.

        `Volumetric flow rate constraint`

        min_vfr_per_bar : float, optional
            Min allowed throughput, `i.e.`, volumetric flow rate, in unit of
            :math:`m^3/sec/bar`, by default None
        min_vfr_ul_per_min_per_bar : float, optional
            Min allowed throughput, `i.e.`, volumetric flow rate, in unit of
            :math:`\\mu L/min/bar`, by default None
        min_vfr_ml_per_hr_per_bar : float, optional
            Min allowed throughput, `i.e.`, volumetric flow rate, in unit of
            :math:`m L/hr/bar`, by default None
        fluid_mu : float, optional
            Fluid dynamic viscosity with a unit of :math:`Pa.sec`, relevant if
            throughput constraint is applied, by default 1e-3

        `Die area (mm square)`

        max_die_area_mmsq : float, optional
            Max allowed die area; Note that only the area occupied by DLD
            pillars is considered; sidewalls and additional up-/downstream
            components are not taken into account. by default None

        `Gap over critical diameter`

        min_gap_over_dc : float, optional
            Min allowed lateral gap over critical diameter, by default None

        `Constraints OFF mode`

        turn_off_constraints : bool, optional
            Whether to turn off the constraints, by default False
        """

        # --- default params

        # Config shape of core entities
        if core_shape is None:
            core_shape = "circle"
        if core_shape_rot_angle is None:
            core_shape_rot_angle = 0.0
        if num_points_per_circle is None:
            num_points_per_circle = 32
        # General
        if opt_mirror is None:
            opt_mirror = False
        if spacing_between_mirrors_within_single_unit is None:
            spacing_between_mirrors_within_single_unit = 0.0
        if dot_offset is None:
            dot_offset = [0, 0]
        if opt_smoothen_dep_sidewall is None:
            opt_smoothen_dep_sidewall = False
        if opt_reverse_tone is None:
            opt_reverse_tone = False
        # Optional components
        if opt_multi_inlet is None:
            opt_multi_inlet = False
        if opt_filter is None:
            opt_filter = False
        if opt_preload is None:
            opt_preload = False
        if opt_collection is None:
            opt_collection = False
        if opt_collection_sideway_right_side is None:
            opt_collection_sideway_right_side = False
        if opt_collection_sideway_left_side is None:
            opt_collection_sideway_left_side = False
        # Potential transformations before mirror/array
        if opt_mirror_x is None:
            opt_mirror_x = False
        if opt_mirror_y is None:
            opt_mirror_y = False
        # Mirror/Array
        if array_counts is None:
            array_counts = [1, 1]
        if array_spacing is None:
            array_spacing = [0.0, 0.0]
        if opt_mirror_before_array is None:
            opt_mirror_before_array = [False, False]
        if spacing_between_mirrors_before_array is None:
            spacing_between_mirrors_before_array = [0.0, 0.0]
        if mirror_before_array_around_negative_edge is None:
            mirror_before_array_around_negative_edge = [False, False]
        # Cover on acc side
        if acc_cover_excess_width_over_gap_w is None:
            acc_cover_excess_width_over_gap_w = 0.0
        # Optional addtional row capping the topmost DLD unit
        if opt_cap_top_row is None:
            opt_cap_top_row = False
        if cap_top_row_block_width_acc_side is None:
            cap_top_row_block_width_acc_side = 0
        if cap_top_row_block_width_dep_side is None:
            cap_top_row_block_width_dep_side = 0
        # Filter
        if filter_shape is None:
            filter_shape = "square"
        if filter_len_nondim is None:
            filter_len_nondim = 39
        if filter_half_pitch_nondim is None:
            filter_half_pitch_nondim = 3
        if filter_margin_top_nondim is None:
            filter_margin_top_nondim = 5
        if filter_offset_w is None:
            filter_offset_w = 0.0
        if filter_block_width_acc_side is None:
            filter_block_width_acc_side = 0.0
        if filter_block_width_dep_side is None:
            filter_block_width_dep_side = 0.0
        # Preload
        if preload_offset_w is None:
            preload_offset_w = 0.0
        if preload_margin_top_nondim is None:
            preload_margin_top_nondim = 0.0
        if preload_block_width_acc_side is None:
            preload_block_width_acc_side = 0.0
        if preload_block_width_dep_side is None:
            preload_block_width_dep_side = 0.0
        # Collection
        if collection_margin_top_nondim is None:
            collection_margin_top_nondim = 2.0
        if opt_collection_with_via is None:
            opt_collection_with_via = False
        # --- Collection with via
        if via_dia_outer_ring_over_via_dia is None:
            via_dia_outer_ring_over_via_dia = 1.2
        if vias_spacing_min is None:
            vias_spacing_min = 60.0
        if zz_width_to_width_tot is None:
            zz_width_to_width_tot = 0.9
        if zz_len_downstream_init_extension is None:
            zz_len_downstream_init_extension = 20.0
        if zz_len_downstream_bottom is None:
            zz_len_downstream_bottom = 50.0
        if zz_len_upstream is None:
            zz_len_upstream = 300.0
        if zz_len_downstream is None:
            zz_len_downstream = 400.0
        if zz_bar_pitch_nondim is None:
            zz_bar_pitch_nondim = 3.0
        if zz_bar_gap_over_gap_w is None:
            zz_bar_gap_over_gap_w = 1.75
        if zz_bar_offset_w is None:
            zz_bar_offset_w = 0.0
        if bmp_bar_pitch_nondim is None:
            bmp_bar_pitch_nondim = 2.0
        if bmp_bar_gap_over_gap_w is None:
            bmp_bar_gap_over_gap_w = 2.0
        if bmp_bar_offset_w is None:
            bmp_bar_offset_w = 0.0
        if opt_report_collection is None:
            opt_report_collection = True
        # Padding for NIL
        if opt_padding_features is None:
            opt_padding_features = False
        if padding_width is None:
            padding_width = {
                "low": 30,
                "right": 30,
                "top": 30,
                "left": 30,
            }
        if opt_padding_reverse_tone is None:
            opt_padding_reverse_tone = False
        if layer_padding is None:
            layer_padding = (1, 0)
        # Relatively detailed config params
        if dep_sidewall_theme is None:
            dep_sidewall_theme = 0
        if acc_sidewall_theme is None:
            acc_sidewall_theme = 0
        if top_cell_name is None:
            top_cell_name = "Block"
        if layer_1 is None:
            layer_1 = (1, 0)
        if layer_2 is None:
            layer_2 = (2, 0)
        if verbose is None:
            verbose = True
        if opt_process_upon_init is None:
            opt_process_upon_init = True
        if opt_write_upon_init is None:
            opt_write_upon_init = True
        if opt_save_image is None:
            opt_save_image = False
        if use_top_cell_if_exists is None:
            use_top_cell_if_exists = False
        # Considerations for design automation
        if get_geom_config_auto_use_auto_num_unit is None:
            get_geom_config_auto_use_auto_num_unit = False
        if fluid_mu is None:
            fluid_mu = 1e-3
        # --- Constraint OFF mode
        if turn_off_constraints is None:
            turn_off_constraints = False

        # --- to have same name for staticmethod and instance method
        self.get_flow_rate = self._get_flow_rate
        self.get_num_parallel_core_dld_1D_array = (
            self._get_num_parallel_core_dld_1D_array
        )

        # -------------------------------
        # Auto config
        # -------------------------------
        lst_param_auto_core = DLD.lst_param_auto_core.copy()
        lst_param_auto_block = DLD.lst_param_auto_block.copy()

        # if constraints are to be applied with an explicitly provided
        # ``num_unit``, this param (``num_unit``) needs to be passed to function
        # ``get_geom_config_auto``; otherwise, a **full** DLD system to be
        # considered regardless of any explicitly provided ``num_unit``.
        if not get_geom_config_auto_use_auto_num_unit:
            lst_param_auto_block += ["num_unit"]

        # Number of parallel core.DLD arrays
        num_parallel_unit = DLD.get_num_parallel_core_dld_1D_array(
            array_counts=array_counts,
            opt_mirror_before_array=opt_mirror_before_array,
            opt_mirror=opt_mirror,
        )

        # --- consistency check
        if not turn_off_constraints and (
            opt_multi_inlet
            or opt_preload
            or opt_filter
            or opt_collection
            or opt_collection_sideway_left_side
            or opt_collection_sideway_right_side
        ):
            print(
                f"""Warning:\nConstraints should be applied mainly to DLD
pillars regions, i.e., no up-/downstream component should be included.
Currently, the provided arguments require:
``turn_off_constraints``:{turn_off_constraints}
``opt_multi_inlet``:{opt_multi_inlet}
``opt_preload``:{opt_preload}
``opt_filter``:{opt_filter}
``opt_collection``:{opt_collection}
``opt_collection_sideway_left_side``:{opt_collection_sideway_left_side}
``opt_collection_sideway_right_side``:{opt_collection_sideway_right_side}"""
            )

        # determining params subject to constraints
        _dict_to_unpack = DLD.get_geom_config_auto(
            # constraints
            range_Np=range_Np,
            range_Nw=range_Nw,
            range_width=range_width,
            range_length=range_length,
            # volumetric flow rate (vfr)
            min_vfr_per_bar=min_vfr_per_bar,
            min_vfr_ul_per_min_per_bar=min_vfr_ul_per_min_per_bar,
            min_vfr_ml_per_hr_per_bar=min_vfr_ml_per_hr_per_bar,
            num_parallel_unit=num_parallel_unit,
            # Die area (mm square)
            max_die_area_mmsq=max_die_area_mmsq,
            # gap over critical dia.
            min_gap_over_dc=min_gap_over_dc,
            # constraint Off mode
            turn_off_constraints=turn_off_constraints,
            **{key: kwargs.get(key) for key in lst_param_auto_core},
            **{key: locals()[key] for key in lst_param_auto_block},
        )

        # -------------------------------------------------------------------
        # update given params for geometrical configurations
        # locals are updated manually (do not use one-line implementations with
        # adverse side effects!)
        # ``kwargs`` for parent constructors params
        # -------------------------------------------------------------------

        # locals (block)
        num_unit_extra = _dict_to_unpack.get("num_unit_extra")
        num_unit_extra_nondim = _dict_to_unpack.get("num_unit_extra_nondim")
        fluid_mu = _dict_to_unpack.get("fluid_mu")

        # core
        for key in lst_param_auto_core:
            kwargs[key] = _dict_to_unpack.get(key)
        # -------------------------------------------------------------------

        # ---------------------------
        # Constructors
        # ---------------------------
        lst_param_Element = Element.__init__.__code__.co_varnames
        lst_param_core_DLD = core_DLD.__init__.__code__.co_varnames

        # --- Parent: Element
        _kwargs_Element = {}
        for key in lst_param_Element:
            if key in kwargs:
                _kwargs_Element[key] = kwargs.pop(key)
        Element.__init__(self, *args, **_kwargs_Element)

        # --- Parent: core_DLD
        _kwargs_Core = {}
        for key in lst_param_core_DLD:
            if key in kwargs:
                _kwargs_Core[key] = kwargs.pop(key)

        core_DLD.__init__(self, *args, **_kwargs_Core)

        # --- sanity check
        if len(kwargs) > 0:
            raise ValueError(f"Invalid parameter(s): {[key for key in kwargs]}")
        #####################

        # --------------------------------------------------------------------
        # Determine number of units
        #
        # Note:
        #   It could be revised to be set from the dict. returned by
        # ``DLD.get_geom_config_auto``.
        # It needs to be done in a manner consistent with the current
        # available feature that enables run of ``DLD.get_geom_config_auto``
        # for **full** DLD while a specific value passed by user for number of
        # units, e.g, ``num_unit=1``, which is currently accomplished by
        # not passing ``num_unit`` (or passing None) to
        # ``DLD.get_geom_config_auto``
        # (``get_geom_config_auto_use_auto_num_unit=True``).
        # --------------------------------------------------------------------
        _, num_unit = DLD.get_full_length(
            Np=self.Np,
            Nw=self.Nw,
            num_unit=num_unit,
            pitch_a=self.pitch_a,
            num_unit_extra=num_unit_extra,
            num_unit_extra_nondim=num_unit_extra_nondim,
        )

        # --------------------------------------------------------------------
        # self attributes
        # --------------------------------------------------------------------
        lst_param_to_set = DLD.__init__.__code__.co_varnames[
            1 : DLD.__init__.__code__.co_argcount
        ]
        lcl = locals()
        for _sn_key, key in enumerate(lst_param_to_set):
            setattr(self, key, lcl[key])

        # --------------------------------------------------------------------
        # config default configs
        # --------------------------------------------------------------------

        if self.height_deep is None:
            # assuming much deeper channels than those for shallow regions
            self.height_deep = 10 * self.height
        if self.bus_width is None:
            self.bus_width = 100
        if self.bus_length is None:
            self.bus_length = 1e5

        # beam-shaped entities
        if self.beam_thickness is None:
            self.beam_thickness = 0.25 * min(
                self.side_length_w, self.side_length_a
            )

        # sidewalls
        if self.sidewall_width is None:
            self.sidewall_width = self.pitch_w
        if self.sidewall_width < 0:
            raise ValueError(
                f"""Negative values are not allowed for ``sidewall_width``.
The current value is {self.sidewall_width}."""
            )

        # preload
        if self.preload_offset_a is None:
            self.preload_offset_a = self.pitch_a
        if self.preload_bar_dims is None:
            self.preload_bar_dims = [self.side_length_w, 10 * self.pitch_a]
        if self.preload_bar_pitch is None:
            self.preload_bar_pitch = 2 * self.pitch_w

        # preload-filter
        if self.filter_preload_spacing is None:
            self.filter_preload_spacing = 5 * self.pitch_a

        # multi-inlet
        if self.config_multi_inlet is not None:
            self.opt_multi_inlet = True

        # ----------------------------------------------------------------
        # simple collection
        # ----------------------------------------------------------------
        if self.collection_bar_pitch_nondim is None:
            self.collection_bar_pitch_nondim = 2
        if self.collection_bar_dims is None:
            self.collection_bar_dims = [self.pitch_w / 2, 10 * self.pitch_a]
        if self.collection_offset_w is None:
            self.collection_offset_w = self.pitch_w / 4
        if self.collection_offset_a is None:
            self.collection_offset_a = 2 * self.pitch_a  # act as lower margin
        self.collection_bar_pitch = (
            self.collection_bar_pitch_nondim * self.pitch_w
        )

        # --------------------------------------------------------------------
        # sideway collection
        # --------------------------------------------------------------------
        if self.collection_sideway_width is None:
            self.collection_sideway_width = max(
                int(25.0 / self.pitch_a) * self.pitch_a, 5 * self.pitch_a
            )

        # --------------------------------------------------------------------
        # collection with via: dimensionalization & appropriate via diameter
        # --------------------------------------------------------------------
        self.collection_core_width_tot = (
            self.acc_dots_full[-1][0, 0] - self.dep_dots_full[-1][0, 0]
        )

        if self.via_dia_outer_ring is None:
            if self.via_dia is not None:
                self.via_dia_outer_ring = (
                    self.via_dia_outer_ring_over_via_dia * self.via_dia
                )
            else:
                self.via_dia_outer_ring = 300
                self.via_dia = 250

        self.via_dia_outer_ring = min(
            self.via_dia_outer_ring,
            2 * self.collection_core_width_tot
            + 2 * self.sidewall_width
            - self.vias_spacing_min,
        )

        if self.opt_collection and self.opt_collection_with_via:
            assert (
                self.via_dia_outer_ring > 0
            ), f"""`via_dia_outer_ring` is {self.via_dia_outer_ring}, while it
must be greater than zero. The minimum spacing between vias
(`vias_spacing_min`) is currently {vias_spacing_min}.
An option could be to lower down the value of this parameter if feasible."""

        if self.via_dia is None:
            self.via_dia = (
                self.via_dia_outer_ring / self.via_dia_outer_ring_over_via_dia
            )

        if self.opt_collection and self.opt_collection_with_via:
            assert (
                self.via_dia <= self.via_dia_outer_ring
            ), f"""``via_dia`` cannot be greater than ``via_dia_outer_ring``.
via_dia: {self.via_dia}
via_dia_outer_ring: {self.via_dia_outer_ring}"""

        self.collection_margin_top = (
            self.collection_margin_top_nondim * self.pitch_a
        )
        self.bmp_len = self.zz_len_upstream + self.zz_len_downstream

        self.zz_bar_pitch = self.zz_bar_pitch_nondim * self.pitch_w
        self.zz_bar_gap = self.zz_bar_gap_over_gap_w * self.gap_w
        self.zz_bar_width = self.zz_bar_pitch - self.zz_bar_gap
        self.zz_bar_dim = [self.zz_bar_width, self.zz_len_upstream]

        self.bmp_bar_pitch = self.bmp_bar_pitch_nondim * self.pitch_w
        self.bmp_bar_gap = self.bmp_bar_gap_over_gap_w * self.gap_w
        self.bmp_bar_width = self.bmp_bar_pitch - self.bmp_bar_gap
        self.bmp_bar_dim = [self.bmp_bar_width, self.bmp_len]

        # ----------------------------------------------------
        # config option cover for acc. side
        # ----------------------------------------------------
        if self.opt_cover_acc is None:
            if self.opt_mirror:
                self.opt_cover_acc = True
            else:
                self.opt_cover_acc = False

        # --------------------------------------------------------------------
        # updating x_mirror depending on config
        #
        # In case of opt_mirror==True:
        # The x_mirror which by default is ``self.acc_dots_full[-1][0,0]`` can
        # be updated to enable a spacing between mirrors within the single
        # unit.
        #
        # In case of opt_mirror==False:
        # An appropriate x_mirror is defined in such a way that the mirror of
        # a component from left gives the right counterpart. For example,
        # sidewalls of top cap row, smooth_col_cell, etc.
        # --------------------------------------------------------------------
        if self.opt_mirror:
            self.x_mirror += (
                self.spacing_between_mirrors_within_single_unit / 2.0
            )
        else:
            x_max = self.acc_dots_full[-1][0, 0]
            x_min = self.dep_dots_full[-1][0, 0]
            self.x_mirror = (x_max + x_min) / 2.0

        # --------------------------------------------------------------------
        # A reference point is determined here, for capping the most upstream
        # row of DLD with an additional row of entities as needed.
        # --------------------------------------------------------------------
        # bounding box of center of posts including acc and dep boundaries
        x_min = min(self.dep_dots_full[-1][0, 0], self.dep_dots_full[-1][-2, 0])
        x_max = max(self.acc_dots_full[-1][0, 0], self.dep_dots_full[-1][-1, 0])
        y_min = self.ll[1]
        y_max = self.ll[1] + self.num_unit * self.Np * self.pitch_a
        self.box_all_dots_of_unit = [(x_min, y_min), (x_max, y_max)]

        # ref point for topmost row
        self.topmost_row_leftmost_point = [
            float(
                self.dots_core_row(-1)[0, 0]
                - (self.dep_num_lanes - 1) * self.pitch_w
            ),
            float(self.box_all_dots_of_unit[1][1]),
        ]

        # -----------------------------------------------------
        # Any final sanity checks
        # -----------------------------------------------------

        # ------------------------
        # Process
        # ------------------------
        if opt_process_upon_init:
            DLD.process(
                self,
                opt_write_upon_init=opt_write_upon_init,
                opt_save_image=opt_save_image,
            )

    def __repr__(self):
        # parent class
        msg = core_DLD.__repr__(
            self,
        )

        # --- new line
        msg += "\n"

        # ---add to
        var_lst = [
            "num_unit",
            "opt_mirror",
            "array_counts",
            "opt_mirror_before_array",
        ]
        msg += "block.DLD__"
        for var in var_lst:
            # float
            if var in []:
                msg += f"_{var}:{getattr(self, var):.3f}"
            else:
                msg += f"_{var}:{getattr(self, var)}"

        return msg

    def get_die_info(self):
        """Returning the die information."""

        # parent class
        out_dict = super().get_die_info()
        area = out_dict["area"] * 1.0e-12
        area_mmsq = area * 1.0e6

        # --- add keys to dict.
        d_c = self.get_dc()
        num_parallel_core_dld = self.get_num_parallel_core_dld_1D_array()
        vfr_per_bar = self.get_flow_rate()
        gap_over_dc = self.gap_w / d_c

        resistance = 1e5 / vfr_per_bar
        vfr_ul_per_min = vfr_SI_to_ul_per_min(vfr_per_bar)
        vfr_ml_per_hr = vfr_SI_to_ml_per_hr(vfr_per_bar)

        out_dict["Np"] = self.Np
        out_dict["Nw"] = self.Nw
        out_dict["d_c"] = d_c
        out_dict["count of 1D arrays of core.DLD"] = num_parallel_core_dld
        out_dict["resistance (Pa.sec/m^3)"] = resistance
        out_dict["volumetric flow rate at 1 bar (m^3/sec)"] = vfr_per_bar
        out_dict["volumetric flow rate at 1 bar (milli-liter/hr)"] = (
            vfr_ml_per_hr
        )

        performance = {
            "gap over crit. dia.": gap_over_dc,
            "volumetric flow rate at 1 bar (micro-liter/min)": vfr_ul_per_min,
            "die area (mm-sq)": area_mmsq,
            "Flow rate @ 1 bar/area (micro-liter/min/mm-sq)": vfr_ul_per_min
            / area_mmsq,
        }
        out_dict["performance"] = performance

        return out_dict

    def process(
        self,
        use_top_cell_if_exists=None,
        *args,
        **kwargs,
    ):
        """
        The main method for building the system.

        Parameters
        ----------
        use_top_cell_if_exists : bool, optional
            Whether to use top cell of layout in the case that layout is not
            empty; if False, a top_cell to be created, by default None.

        Returns
        -------
        db.Layout
            The layout object.

        """

        # --- layout
        if self.layout is None:
            self.layout = db.Layout()
            self.layout.dbu = 1e-3

        # ly = db.Layout()
        ly = self.layout
        l1 = ly.layer(*self.layer_1)
        TDBU = db.CplxTrans(ly.dbu).inverted()

        # self.layout = ly
        self.TDBU = TDBU
        self.l1 = l1

        # --------------------------------------
        # Creating a top cell as needed
        # --------------------------------------
        if use_top_cell_if_exists is None:
            use_top_cell_if_exists = self.use_top_cell_if_exists

        available_top_cells = self.layout.top_cells()
        if len(available_top_cells) > 0 and use_top_cell_if_exists:
            top_cell = available_top_cells[0]
        else:
            top_cell = ly.create_cell(self.top_cell_name)

        # --------------------------------------
        # adding cells to TOP
        # --------------------------------------

        # Make a column (array) of DLD units.
        col_cell = self._add_col_cell()
        top_cell.insert(db.DCellInstArray(col_cell.cell_index(), db.DTrans()))

        # Add preload as needed
        if self.opt_preload:
            preload_cell = self._add_preload()
            top_cell.insert(
                db.DCellInstArray(preload_cell.cell_index(), db.DTrans())
            )

        # Make an inlet filter as needed
        if self.opt_filter:
            filter_cell = self._add_filter()
            top_cell.insert(
                db.DCellInstArray(filter_cell.cell_index(), db.DTrans())
            )

        # Make a sideway collection component as needed
        if (
            self.opt_collection_sideway_right_side
            or self.opt_collection_sideway_left_side
        ):
            collection_sideway_cell = self._add_collection_sideway()
            top_cell.insert(
                db.DCellInstArray(
                    collection_sideway_cell.cell_index(), db.DTrans()
                )
            )
            # self.prune('unit_grating')

        # Make a collection component as needed
        if self.opt_collection:
            if self.opt_collection_with_via:
                # Make a collection component with vias
                collection_tot_cell = self._add_collection()
            else:
                # Make a simple collection component
                collection_tot_cell = self._add_collection_simple()

            top_cell.insert(
                db.DCellInstArray(collection_tot_cell.cell_index(), db.DTrans())
            )

        # Make a multi-inlet as needed (To be done after all components are
        # made as multi-inlet affects width and bbox of block)
        if self.opt_multi_inlet:
            self._add_multi_inlet()

        # -------------------------------------
        # mirroring x as needed
        # -------------------------------------
        if self.opt_mirror_x:
            self.mirror_x()

        # -------------------------------------
        # mirroring y as needed
        # -------------------------------------
        if self.opt_mirror_y:
            self.mirror_y()

        # -------------------------------------
        # Rotation before arraying as needed
        # -------------------------------------
        if self.rotation_angle_deg_before_array is not None:
            self.rotate(self.rotation_angle_deg_before_array)

        # -------------------------------------
        # Reverse tone as needed
        # -------------------------------------
        if self.opt_reverse_tone:
            cell_src = [self.single_unit_cell]

            if self.opt_cap_top_row:
                cell_src.append(self.top_row_tot_cell)
            if self.opt_preload:
                cell_src.append(preload_cell)
            if self.opt_filter:
                cell_src.append(filter_cell)
            if self.opt_collection:
                cell_src.append(collection_tot_cell)
            if (
                self.opt_collection_sideway_left_side
                or self.opt_collection_sideway_right_side
            ):
                cell_src.append(collection_sideway_cell)

            cell_name_to_prune = [
                "filter_cell",
                "Core",
                "Sidewall",
                "cover",
                "grating",
                "top_row",
                "top_row_sidewall_mirror_y",
                "Core_mirror_y",
                "top_row_mirror_y",
                "collection",
                "collection_sideway",
            ]
            reverse_tone(
                cell_src=cell_src,
                cell_target=cell_src,
                layer=self.l1,
                cell_name_to_prune=cell_name_to_prune,
                clip_pad=None,  # pad the bounding box clip outward
            )

        # -------------------------------------
        # Creating an array of columns
        # Mirroring can be applied prior to arraying
        # -------------------------------------
        if (
            np.sum(self.array_counts) > 2
            or self.opt_mirror_before_array[0]
            or self.opt_mirror_before_array[1]
        ):
            self._add_array()

        # -------------------------------------
        # Creating padding features (mainly for NIL)
        # -------------------------------------
        if self.opt_padding_features:
            self._add_padding_light()

        # -------------------------------------
        # setting lower left coordinates as needed
        # -------------------------------------
        if self.target_ll is not None:
            self.set_ll(self.target_ll)

        # --- after all logics
        Element.process(
            self,
            *args,
            **kwargs,
        )

        # --------------------------------------
        # log at the end of process
        # --------------------------------------
        if self.verbose:
            print("-" * 40)
            print(self)
            print("-" * 40)
            info_dic = DLD.get_die_info(
                self,
            )
            pprint.pprint(info_dic)

        return self.layout

    def _add_padding_light(
        self,
        opt_padding_reverse_tone=None,
        layer_padding=None,
    ):
        """Add padding (mainly for NIL)."""

        # sanity check
        if self.padding_entity_dim is None or self.padding_entity_pitch is None:
            raise ValueError(
                """``padding_entity_dim`` and
                ``padding_entity_pitch`` are needed."""
            )

        # default config
        if opt_padding_reverse_tone is None:
            opt_padding_reverse_tone = self.opt_padding_reverse_tone

        # layer to write features on
        if layer_padding is None:
            layer_padding = self.layer_padding
        padding_layer = self.layout.layer(*layer_padding)

        # bounding box
        bb = bbox(self.layout.top_cell())
        padding_width = self.padding_width
        pad_cell = self.layout.create_cell("Pad")
        self.layout.top_cells()[0].insert(
            db.DCellInstArray(pad_cell.cell_index(), db.DTrans())
        )

        # pad low
        length_raw = (
            bb[1][0]
            - bb[0][0]
            + padding_width["left"]
            + padding_width["right"],
            padding_width["low"],
        )
        length = list(length_raw)
        # ensuring length is an integer multiplier of pitch
        for sn_dir, len_dir in enumerate(length_raw):
            length[sn_dir] = (
                np.ceil(len_dir / self.padding_entity_pitch[sn_dir])
                * self.padding_entity_pitch[sn_dir]
            )

        ll = (
            bb[0][0]
            - np.ceil(padding_width["left"] / self.padding_entity_pitch[0])
            * self.padding_entity_pitch[0],
            bb[0][1] - length[1],
        )
        pad_light(
            layout=self.layout,
            padding_entity_dim=self.padding_entity_dim,
            pitch=self.padding_entity_pitch,
            length=length,
            ll=ll,
            layer=padding_layer,
            cell_target=pad_cell,
            opt_reverse_tone=opt_padding_reverse_tone,
        )

        # pad top
        length_raw = (
            bb[1][0]
            - bb[0][0]
            + padding_width["left"]
            + padding_width["right"],
            padding_width["top"],
        )
        length = list(length_raw)
        # ensuring length is an integer multiplier of pitch
        for sn_dir, len_dir in enumerate(length_raw):
            length[sn_dir] = (
                np.ceil(len_dir / self.padding_entity_pitch[sn_dir])
                * self.padding_entity_pitch[sn_dir]
            )
        ll = (
            bb[0][0]
            - np.ceil(padding_width["left"] / self.padding_entity_pitch[0])
            * self.padding_entity_pitch[0],
            bb[1][1],
        )
        pad_light(
            layout=self.layout,
            padding_entity_dim=self.padding_entity_dim,
            pitch=self.padding_entity_pitch,
            length=length,
            ll=ll,
            layer=padding_layer,
            cell_target=pad_cell,
            opt_reverse_tone=opt_padding_reverse_tone,
        )

        # pad right
        length_raw = (
            padding_width["right"],
            bb[1][1] - bb[0][1],
        )
        length = list(length_raw)
        # ensuring length is an integer multiplier of pitch
        for sn_dir, len_dir in enumerate(length_raw):
            length[sn_dir] = (
                np.ceil(len_dir / self.padding_entity_pitch[sn_dir])
                * self.padding_entity_pitch[sn_dir]
            )
        ll = (bb[1][0], bb[0][1])
        pad_light(
            layout=self.layout,
            padding_entity_dim=self.padding_entity_dim,
            pitch=self.padding_entity_pitch,
            length=length,
            ll=ll,
            layer=padding_layer,
            cell_target=pad_cell,
            opt_reverse_tone=opt_padding_reverse_tone,
        )

        # pad left
        length_raw = (
            padding_width["left"],
            bb[1][1] - bb[0][1],
        )
        length = list(length_raw)
        # ensuring length is an integer multiplier of pitch
        for sn_dir, len_dir in enumerate(length_raw):
            length[sn_dir] = (
                np.ceil(len_dir / self.padding_entity_pitch[sn_dir])
                * self.padding_entity_pitch[sn_dir]
            )
        ll = (
            bb[0][0]
            - np.ceil(padding_width["left"] / self.padding_entity_pitch[0])
            * self.padding_entity_pitch[0],
            bb[0][1],
        )
        pad_light(
            layout=self.layout,
            padding_entity_dim=self.padding_entity_dim,
            pitch=self.padding_entity_pitch,
            length=length,
            ll=ll,
            layer=padding_layer,
            cell_target=pad_cell,
            opt_reverse_tone=opt_padding_reverse_tone,
        )

    def _add_array(
        self,
        cell_src_ind=None,
        array_spacing=None,
        opt_mirror_before_array=None,
        spacing_between_mirrors_before_array=None,
        mirror_before_array_around_negative_edge=None,
    ):
        """Make an array of column of DLD units. Mirroring can be applied
        prior to arraying."""

        # --------------------------------------
        # creating an array for a given cell index
        # --------------------------------------
        if cell_src_ind is None:
            cell_src_ind = self.layout.top_cell().cell_index()
        if array_spacing is None:
            array_spacing = self.array_spacing
        if opt_mirror_before_array is None:
            opt_mirror_before_array = self.opt_mirror_before_array
        if spacing_between_mirrors_before_array is None:
            spacing_between_mirrors_before_array = (
                self.spacing_between_mirrors_before_array
            )
        if mirror_before_array_around_negative_edge is None:
            mirror_before_array_around_negative_edge = (
                self.mirror_before_array_around_negative_edge
            )

        arr = self.layout.create_cell("ARRAY")
        cell_src = self.layout.cell(cell_src_ind)

        unit_cell_to_array = self.layout.create_cell("UNIT_TO_ARRAY")
        unit_cell_to_array.insert(
            db.DCellInstArray(cell_src.cell_index(), db.DTrans())
        )

        for sn_dir in range(2):
            bb = bbox(cell_src)
            if opt_mirror_before_array[sn_dir]:
                # required translation after M90 or M0 around the positive
                # edge(right/top)
                trns = (
                    2 * bb[1][sn_dir]
                    + spacing_between_mirrors_before_array[sn_dir]
                )
                if mirror_before_array_around_negative_edge[sn_dir]:
                    # adjusting translation for mirroring around the
                    # negative edge(left/bottom)
                    trns -= 2 * (
                        bb[1][sn_dir]
                        - bb[0][sn_dir]
                        + spacing_between_mirrors_before_array[sn_dir]
                    )
                if sn_dir == 0:
                    # --------------------
                    # mirror y-axis
                    # --------------------
                    this_translation = [trns, 0]
                    this_transformation = db.DTrans(
                        db.DTrans.M90, db.DVector(*this_translation)
                    )
                    mrr_y = self.layout.create_cell("mirror_y_before_array")
                    mrr_y.insert(
                        db.DCellInstArray(cell_src, this_transformation)
                    )
                    unit_cell_to_array.insert(
                        db.DCellInstArray(mrr_y.cell_index(), db.DTrans())
                    )

                else:
                    # --------------------
                    # mirror x-axis
                    # --------------------
                    this_translation = [0, trns]
                    this_transformation = db.DTrans(
                        db.DTrans.M0, db.DVector(*this_translation)
                    )
                    mrr_x = self.layout.create_cell("mirror_x_before_array")
                    mrr_x.insert(
                        db.DCellInstArray(cell_src, this_transformation)
                    )
                    # mirroring mirror_y (if applicable) around x-axis
                    if opt_mirror_before_array[0]:
                        mrr_x.insert(
                            db.DCellInstArray(mrr_y, this_transformation)
                        )
                    unit_cell_to_array.insert(
                        db.DCellInstArray(mrr_x.cell_index(), db.DTrans())
                    )

        bb = bbox(unit_cell_to_array)

        dim = [
            bb[1][0] - bb[0][0],
            bb[1][1] - bb[0][1],
        ]

        pitch = [dim[0] + array_spacing[0], dim[1] + array_spacing[1]]
        length = [
            pitch[0] * self.array_counts[0],
            pitch[1] * self.array_counts[1],
        ]

        generic_array(
            layout=self.layout,
            cell_src=unit_cell_to_array,
            pitch=pitch,
            length=length,
            trans=[0, 0],
            cell_target=arr,
        )

    def _get_core_entity_region(
        self,
        core_entity_func=None,
        side_length_w=None,
        side_length_a=None,
        num_points_per_circle=None,
        beam_thickness=None,
        dbu=None,
        clip_dim=None,
        clip_nondim=None,
    ):
        """Generates and returns an entity (pillar) depending on the
        configurations.
        For example, it can be built from the built-in profiles, or by passing
        a list of corrdinates defining the perimeter of profile, or by passing
        a profile generator callback function.
        """

        # --- config generall
        if side_length_w is None:
            side_length_w = self.side_length_w
        if side_length_a is None:
            side_length_a = self.side_length_a
        if num_points_per_circle is None:
            num_points_per_circle = self.num_points_per_circle
        if beam_thickness is None:
            beam_thickness = self.beam_thickness
        if dbu is None:
            dbu = self.layout.dbu

        # --- (pretty much always herein) falls back to
        # ``self.core_entity_func``, but this is a general function that can
        # be called while passing different ``core_entity_func`` functions
        if core_entity_func is None:
            core_entity_func = self.core_entity_func

        # --- If no valid ``core_entity_func`` available:
        # In case a valid core_shape key (type of string) is provided -->
        # falling back to built-in entity generators
        # In case a list of coordinates is provided --> to use generic_shape,
        # which is processed in the following.
        if core_entity_func is None:
            if type(self.core_shape) in [str]:
                if self.core_shape in DLD.CORE_SHAPE:
                    core_entity_func = DLD.CORE_SHAPE[self.core_shape]

        # circle profile
        if core_entity_func == circle:
            core_entity = core_entity_func(
                lx=side_length_w,
                ly=side_length_a,
                num_points=num_points_per_circle,
                dbu=dbu,
                clip_dim=clip_dim,
                clip_nondim=clip_nondim,
            )

        # rectangle profile
        elif core_entity_func == rectangle:
            core_entity = core_entity_func(
                lx=side_length_w,
                ly=side_length_a,
                dbu=dbu,
                clip_dim=clip_dim,
                clip_nondim=clip_nondim,
            )

        # square profile
        elif core_entity_func == square:
            core_entity = core_entity_func(
                length=side_length_w,
                dbu=dbu,
                clip_dim=clip_dim,
                clip_nondim=clip_nondim,
            )

        # triangle profile
        elif core_entity_func == triangle:
            core_entity = core_entity_func(
                length=side_length_w,
                dbu=dbu,
                clip_dim=clip_dim,
                clip_nondim=clip_nondim,
            )

        # beam profile
        elif (
            core_entity_func == beam_c
            or core_entity_func == beam_t
            or core_entity_func == beam_i
            or core_entity_func == beam_l
        ):
            core_entity = core_entity_func(
                lx=side_length_w,
                ly=side_length_a,
                t=beam_thickness,
                dbu=dbu,
                clip_dim=clip_dim,
                clip_nondim=clip_nondim,
            )

        # --- core_shape being a list of coordinates  centered at (0, 0)
        elif type(self.core_shape) in [list, tuple, np.ndarray]:
            core_entity = generic_shape(
                self.core_shape,
                dbu=dbu,
                target_len_x=side_length_w,
                clip_dim=clip_dim,
                clip_nondim=clip_nondim,
            )

        # --- a callback function to generate the entity
        elif core_entity_func is not None:
            core_entity = core_entity_func(**self.kwargs_entity_gen)

        # --- failure
        else:
            raise ValueError(
                "Not enough information to build shape of core entities."
            )

        return core_entity

    def _add_col_cell(
        self,
    ):
        """Make a column (array) of DLD units."""
        l1 = self.l1

        # ----------------------------------------------
        # Core Unit
        # ----------------------------------------------

        # Multiple arrays of DLD unit
        col_cell = self.layout.create_cell("COL")

        # One single unit of DLD including core, sidewalls, potentially
        # arbitrary regions, etc.
        single_unit_cell = self.layout.create_cell("SINGLE_UNIT")
        core_cell = self.layout.create_cell("Core")  # Dots of a unit of DLD

        core_core_cell = self.layout.create_cell("Core_core")  # Core of DLD
        core_dep_cell = self.layout.create_cell("Core_dep")  # Depletion lanes
        core_acc_cell = self.layout.create_cell(
            "Core_acc"
        )  # Accumulation lanes

        # hierarchy of core
        core_cell.insert(db.DCellInstArray(core_core_cell, db.DTrans()))
        core_cell.insert(db.DCellInstArray(core_dep_cell, db.DTrans()))
        core_cell.insert(db.DCellInstArray(core_acc_cell, db.DTrans()))

        # core is one of the subcells of single_unit cell
        single_unit_cell.insert(db.DCellInstArray(core_cell, db.DTrans()))

        self.single_unit_cell = single_unit_cell
        self.col_cell = col_cell

        # --------------------------------------------------------------------
        # add DLD entities
        #
        # the coordinates of the  entities are coming from ``core.DLD``, but
        # the profile of
        # each entity can be individually configured as needed to develop more
        # effective
        # boundary treatment schemes.
        #
        # core dots including:
        # - core core dots
        # - core dep dots
        # - core acc dots
        #
        # entities on dep and acc lanes can be potentially different from
        # those of core. The parameters can be cofigured to be passed by user
        # in the future to develop more effective boundary treatment schemes.
        # -------------------------------------------------------------------
        core_entity = self._get_core_entity_region()
        cell_core_entity = self.layout.create_cell(
            "Core_core_entity"
        )  # Core entity cell
        cell_core_entity.shapes(l1).insert(
            core_entity,
            db.DCplxTrans(1, self.core_shape_rot_angle, False, 0.0, 0.0),
        )

        # down.stream.most (dsm) entity of core adjacent to up.stream.most
        # (usm) entity on acc. sidewall
        if self.acc_usm_gap_a_widening is not None:
            acc_entity_usm_neighbor = self._get_core_entity_region(
                clip_dim={"bottom": self.acc_usm_gap_a_widening / 2.0}
            )
            cell_acc_entity_usm_neighbor = self.layout.create_cell(
                "Core_acc_entity_usm_neighbor"
            )  # Core entity cell usm neighbor
            cell_acc_entity_usm_neighbor.shapes(l1).insert(
                acc_entity_usm_neighbor,
                db.DCplxTrans(1, self.core_shape_rot_angle, False, 0.0, 0.0),
            )

        # --- core
        for dot in self.dots_core_core_full:
            dot_loc = [
                dot[0] + self.dot_offset[0],
                dot[1] + self.dot_offset[1],
            ]

            # downstreammost entity from neighboring upstream unit
            if (
                self.acc_usm_gap_a_widening is not None
                and np.isclose(
                    dot, self.dots_core_row(0)[-1], atol=1e-3, rtol=1e-5
                ).all()
            ):
                core_core_cell.insert(
                    db.DCellInstArray(
                        cell_acc_entity_usm_neighbor, db.DTrans(*dot_loc)
                    )
                )

            # regular entities
            else:
                core_core_cell.insert(
                    db.DCellInstArray(cell_core_entity, db.DTrans(*dot_loc))
                )

        # --- dep entity
        dep_entity = self._get_core_entity_region()
        cell_dep_entity = self.layout.create_cell(
            "Core_dep_entity"
        )  # Core entity cell
        cell_dep_entity.shapes(l1).insert(
            dep_entity,
            db.DCplxTrans(1, self.core_shape_rot_angle, False, 0.0, 0.0),
        )

        # --- acc entity
        acc_entity = self._get_core_entity_region()
        cell_acc_entity = self.layout.create_cell(
            "Core_acc_entity"
        )  # Core entity cell
        cell_acc_entity.shapes(l1).insert(
            acc_entity,
            db.DCplxTrans(1, self.core_shape_rot_angle, False, 0.0, 0.0),
        )

        # upstreammost entity on acc sidewall --- usm: up.stream.most
        if self.acc_usm_gap_a_widening is not None:
            acc_entity_usm = self._get_core_entity_region(
                clip_dim={"top": self.acc_usm_gap_a_widening / 2.0}
            )
            cell_acc_entity_usm = self.layout.create_cell(
                "Core_acc_entity_usm"
            )  # Core entity cell usm
            cell_acc_entity_usm.shapes(l1).insert(
                acc_entity_usm,
                db.DCplxTrans(1, self.core_shape_rot_angle, False, 0.0, 0.0),
            )

        # --- dep lane(s)
        for lane in self.dep_dots:
            for dot in lane:
                dot_loc = [
                    dot[0] + self.dot_offset[0],
                    dot[1] + self.dot_offset[1],
                ]
                core_dep_cell.insert(
                    db.DCellInstArray(cell_dep_entity, db.DTrans(*dot_loc))
                )

        # --- acc lane(s)
        for lane in self.acc_dots:
            for dot in lane:
                dot_loc = [
                    dot[0] + self.dot_offset[0],
                    dot[1] + self.dot_offset[1],
                ]
                # usm entity of unit
                if (
                    self.acc_usm_gap_a_widening is not None
                    and np.isclose(
                        dot, self.acc_dots_full[-1][-1], atol=1e-3, rtol=1e-5
                    ).all()
                ):
                    core_acc_cell.insert(
                        db.DCellInstArray(
                            cell_acc_entity_usm, db.DTrans(*dot_loc)
                        )
                    )
                # regular entities
                else:
                    core_acc_cell.insert(
                        db.DCellInstArray(cell_acc_entity, db.DTrans(*dot_loc))
                    )

        # --------------------------------------------------------------------
        # mirrored dots as needed
        # --------------------------------------------------------------------
        if self.opt_mirror:
            core_mirr_y_cell = self.layout.create_cell("Core_mirror_y")
            single_unit_cell.insert(
                db.DCellInstArray(core_mirr_y_cell, db.DTrans())
            )
            core_mirr_y_cell.insert(
                db.DCellInstArray(
                    core_cell, db.DTrans(db.DTrans.M90, 2 * self.x_mirror, 0)
                )
            )

        # ------------------------------------
        # adding cover to acc side
        # ------------------------------------
        if self.opt_cover_acc:
            cover_cell = self.layout.create_cell("cover")
            single_unit_cell.insert(db.DCellInstArray(cover_cell, db.DTrans()))

            # ---- tilt angle
            acc_theta_abs = abs(self.get_acc_theta())

            if self.acc_cover_half_width_min is None:
                if self.opt_mirror:
                    acc_cover_half_width_min = min(
                        0.5 * self.side_length_w,
                        self.pitch_w / 2,
                        self.gap_w / 2,
                    )
                else:
                    acc_cover_half_width_min = 0
            else:
                acc_cover_half_width_min = self.acc_cover_half_width_min

            # trim cover
            y_min = self.ll[1] + np.abs(
                acc_cover_half_width_min / np.tan(acc_theta_abs)
            )
            y_min_snap = (
                self.ll[1]
                + np.floor((y_min - self.ll[1]) / self.pitch_a) * self.pitch_a
            )
            if self.opt_mirror:
                y_min_snap -= self.side_length_w / 2
            y_min = y_min_snap
            half_width_min = np.abs(
                (y_min - self.ll[1]) * np.tan(acc_theta_abs)
            )
            # y_max = self.ll[1]+(self.Np-1)*self.pitch_a
            y_max = (
                self.ll[1]
                + (self.Np - 1) * self.pitch_a
                + self.side_length_w / 2
            )
            # in case of gap widening for the upstreammost row
            if self.acc_usm_gap_a_widening is not None:
                y_max -= self.acc_usm_gap_a_widening / 2.0

            half_width_max = np.abs(
                (y_max - self.ll[1]) * np.tan(acc_theta_abs)
            )

            # adding extra width to cap; slope remains the same as already
            # calculated above.
            acc_cap_excess_width = (
                self.acc_cover_excess_width_over_gap_w * self.gap_w
            )
            half_width_min += acc_cap_excess_width
            half_width_max += acc_cap_excess_width

            # left cover
            dx_min = half_width_min
            dx_max = half_width_max

            p1 = [self.acc_dots_full[-1][0, 0], y_min]
            p2 = [self.acc_dots_full[-1][0, 0] - dx_min, y_min]
            p3 = [self.acc_dots_full[-1][0, 0] - dx_max, y_max]
            p4 = [self.acc_dots_full[-1][0, 0], y_max]
            cover_left = db.Region(self.TDBU * polygon([p1, p2, p3, p4]))

            # clipping the cover cap to make sure it is not extending the
            # bounding box of dots
            clip_box = db.Region(
                self.TDBU
                * db.DBox(
                    *self.dep_dots_full[-1][0],
                    # at this point, this is the bounding box of dots
                    *bbox(single_unit_cell)[1],
                )
            )
            cover_left &= clip_box
            cover_cell.shapes(l1).insert(cover_left)

            # mirror of cover
            dx_trans = 2.0 * self.x_mirror
            cover_cell.shapes(l1).insert(
                cover_left, db.DTrans(db.DTrans.M90, dx_trans, 0)
            )

        # --------------------------------------------------------------------
        # Sidewalls of single unit cell
        # --------------------------------------------------------------------
        # if self.sidewall_width is not None:
        if self.sidewall_width > 0:
            sidewall_cell = self.layout.create_cell("Sidewall")
            single_unit_cell.insert(
                db.DCellInstArray(sidewall_cell, db.DTrans())
            )

            # --- dep sidewall
            self.dep_sidewall, _ = lst_get_sidewall_dep[
                self.dep_sidewall_theme
            ](
                dep_dots_full=self.dep_dots_full,
                sidewall_width=self.sidewall_width,
            )
            sidewall_cell.shapes(l1).insert(self.dep_sidewall)

            # --- acc sidewall

            # mirrored design
            if self.opt_mirror or self.acc_sidewall_theme == -1:
                dx_trans = 2.0 * self.x_mirror / self.layout.dbu
                this_transf = db.DTrans(db.DTrans.M90, dx_trans, 0)
                self.acc_sidewall = self.dep_sidewall.transformed(this_transf)
            else:
                self.acc_sidewall, _ = lst_get_sidewall_acc[
                    self.acc_sidewall_theme
                ](
                    acc_dots_full=self.acc_dots_full,
                    sidewall_width=self.sidewall_width,
                )

            sidewall_cell.shapes(l1).insert(self.acc_sidewall)

        # --------------------------------------------------------------------
        # adding provided shapes by user to single unit
        # --------------------------------------------------------------------
        if self.single_unit_extra_shapes is not None:
            extra_shape_lst = self.single_unit_extra_shapes(self)
            for extra_shape in extra_shape_lst:
                single_unit_cell.shapes(l1).insert(extra_shape, db.DTrans())

        # --------------------------------------------------------------------
        # array in y-dir
        # --------------------------------------------------------------------
        i2 = db.DCellInstArray(
            single_unit_cell.cell_index(),
            db.DTrans(db.DTrans()),
            db.DVector(0, self.Np * self.pitch_a),
            db.DVector(0, 0),
            self.num_unit,
            1,
        )
        col_cell.insert(i2)

        # --------------------------------------------------------------------
        # Capping the top of array with one row
        # --------------------------------------------------------------------
        if self.opt_cap_top_row:
            # bottom to top level
            top_row_unit_cell = self.layout.create_cell("unit_top_row")
            top_row_cell = self.layout.create_cell("top_row")
            top_row_tot_cell = self.layout.create_cell("top_row_tot")
            self.top_row_tot_cell = top_row_tot_cell

            # top to bottom level
            col_cell.insert(db.DCellInstArray(top_row_tot_cell, db.DTrans()))
            top_row_tot_cell.insert(
                db.DCellInstArray(top_row_cell, db.DTrans())
            )

            top_row_unit_cell.shapes(l1).insert(
                core_entity,
                db.DCplxTrans(
                    1,
                    self.core_shape_rot_angle,
                    False,
                    db.DVector(*self.topmost_row_leftmost_point),
                ),
            )

            generic_array(
                layout=self.layout,
                cell_src=top_row_unit_cell,
                cell_target=top_row_cell,
                pitch=[self.pitch_w, 1],
                length=[
                    self.box_all_dots_of_unit[1][0]
                    - self.box_all_dots_of_unit[0][0]
                    + 2.0 * self.pitch_w,
                    0,
                ],
                trans=[0, 0],
            )

            if (
                bbox(top_row_cell)[0][0] < bbox(col_cell)[0][0]
                or bbox(top_row_cell)[1][0] > bbox(col_cell)[1][0]
            ):
                clip_box = db.Region(
                    self.TDBU
                    * db.DBox(
                        *bbox(col_cell)[0],
                        bbox(col_cell)[1][0],
                        bbox(top_row_cell)[1][1],
                    )
                )
                region = db.Region(top_row_cell.begin_shapes_rec(l1))
                region = region & clip_box
                top_row_cell.clear()
                top_row_cell.shapes(l1).insert(region)
                self.layout.prune_cell(top_row_unit_cell.cell_index(), -1)

            # -------------------
            # mirroring entities
            # -------------------
            if self.opt_mirror:
                top_row_mirror_cell = self.layout.create_cell(
                    "top_row_mirror_y"
                )
                top_row_tot_cell.insert(
                    db.DCellInstArray(top_row_mirror_cell, db.DTrans())
                )

                top_row_mirror_cell.insert(
                    db.DCellInstArray(
                        top_row_cell,
                        db.DTrans(db.DTrans.M90, 2 * self.x_mirror, 0),
                    )
                )

            # -------------------------------------------
            # adding sidewall for the topmost cap row
            # -------------------------------------------
            # if self.sidewall_width is not None:
            if self.sidewall_width > 0:
                top_row_sidewall_cell = self.layout.create_cell(
                    "top_row_sidewall"
                )
                top_row_tot_cell.insert(
                    db.DCellInstArray(top_row_sidewall_cell, db.DTrans())
                )

                bb = bbox(self.dep_sidewall)
                top_row_sidewall_left_ll = [
                    bb[0][0],
                    self.topmost_row_leftmost_point[1] - self.pitch_a / 2,
                ]
                top_row_sidewall_left_upper_right = [
                    top_row_sidewall_left_ll[0] + self.sidewall_width,
                    top_row_sidewall_left_ll[1] + self.pitch_a,
                ]

                reg_sidewall_left = db.Region(
                    self.TDBU
                    * db.DBox(
                        *top_row_sidewall_left_ll,
                        *top_row_sidewall_left_upper_right,
                    )
                )

                top_row_sidewall_cell.shapes(l1).insert(reg_sidewall_left)

                # mirror of sidewall
                top_row_sidewall_mirror_cell = self.layout.create_cell(
                    "top_row_sidewall_mirror_y"
                )
                top_row_tot_cell.insert(
                    db.DCellInstArray(top_row_sidewall_mirror_cell, db.DTrans())
                )
                top_row_sidewall_mirror_cell.insert(
                    db.DCellInstArray(
                        top_row_sidewall_cell,
                        db.DTrans(db.DTrans.M90, 2 * self.x_mirror, 0),
                    )
                )

            # ---------------------------------------------
            # blocks on dep and acc sides
            # ---------------------------------------------
            if self.cap_top_row_block_width_dep_side > 0:
                block_bar_dep = rectangle(
                    self.cap_top_row_block_width_dep_side,
                    self.pitch_a,
                    reg_ll=[
                        top_row_sidewall_left_ll[0] + self.sidewall_width,
                        top_row_sidewall_left_ll[1],
                    ],
                    dbu=self.layout.dbu,
                )
                top_row_tot_cell.shapes(self.l1).insert(block_bar_dep)

            if self.cap_top_row_block_width_acc_side > 0:
                block_bar_acc = rectangle(
                    self.cap_top_row_block_width_acc_side,
                    self.pitch_a,
                    reg_ll=[
                        bbox(top_row_sidewall_mirror_cell)[0][0]
                        - self.cap_top_row_block_width_acc_side,
                        top_row_sidewall_left_ll[1],
                    ],
                    dbu=self.layout.dbu,
                )
                top_row_tot_cell.shapes(self.l1).insert(block_bar_acc)
            # ---------------------------------------------

        # --------------------------------------------------------------------
        # Smoothing overall (not single unit cell) dep sidewall
        # --------------------------------------------------------------------
        if self.opt_smoothen_dep_sidewall:
            self._smoothen_dep_sidewall(col_cell, l1)

        # --------------------------------------------------------------------
        # END of Smoothing overall (not single unit cell) dep sidewall
        # --------------------------------------------------------------------

        return col_cell

    def _add_preload(
        self,
    ):
        """Make a preload."""

        preload_cell = self.layout.create_cell("preload")

        # --- config
        sidewall_width = self.sidewall_width
        bb = bbox(self.layout.top_cells()[0])
        grating_area_ll = [
            bb[0][0] + sidewall_width,
            bb[1][1],
        ]
        grating_area_dims = bb[1][0] - bb[0][0] - 2 * sidewall_width
        num_extra_bar_column = 4

        # top margin
        if self.preload_margin_top is not None:
            preload_margin_top = self.preload_margin_top
        else:
            preload_margin_top = self.preload_margin_top_nondim * self.pitch_a

        # --- build
        self.preload_cell, _ = grating_with_sidewall(
            layout=self.layout,
            layer=self.l1,
            grating_pitch=self.preload_bar_pitch,
            grating_area_dims=grating_area_dims,  # area between sidewalls
            bar_dims=self.preload_bar_dims,  # bar dimensions: rectangular bar
            bar=None,  # A `db.Region` object as the bar entity
            cell_target=preload_cell,  # target cell for grating with sidewall
            grating_area_ll=grating_area_ll,
            bar_offset=[
                self.preload_offset_w - self.pitch_w / 4.0,
                self.preload_offset_a,
            ],
            sidewall_width=sidewall_width,  # sidewall width
            num_extra_bar_column=num_extra_bar_column,
            opt_clip=True,  # whether to clip bars outside of grating area
            grating_cell_name="grating",
            unit_grating_cell_name="unit_grating",
            margin_top=preload_margin_top,
            block_width=[
                self.preload_block_width_dep_side,
                self.preload_block_width_acc_side,
            ],
        )

        return self.preload_cell

    def _add_filter(
        self,
    ):
        """Make a serpentine filter."""

        # --- cells
        filter_cell = self.layout.create_cell("filter_cell_tot")
        filter_core_entity_func = DLD.CORE_SHAPE[self.filter_shape]
        filter_core_entity = filter_core_entity_func(
            self.side_length_w, dbu=self.layout.dbu
        )

        # --- config
        bb = bbox(self.layout.top_cells()[0])
        sidewall_width = self.sidewall_width
        filter_area_dims = bb[1][0] - bb[0][0] - 2 * sidewall_width
        filter_area_ll = [
            bb[0][0] + sidewall_width,
            bb[1][1],
        ]
        filter_len_nondim = self.filter_len_nondim
        filter_pitch_entity = self.pitch_w
        filter_half_pitch_nondim = self.filter_half_pitch_nondim
        filter_core_entity_offset = [
            self.filter_offset_w
            - self.filter_half_pitch_nondim / 2.0 * self.pitch_w
            + self.gap_w / 2.0,
            self.filter_preload_spacing,
        ]
        num_extra_column = 8
        sidewall_width = sidewall_width
        opt_clip = [False, True][1]
        cell_target = filter_cell
        filter_cell_name = "filter_cell"
        filter_row_unit_name = "filter_row_unit"
        filter_unit_name = "filter_unit"
        filter_col_unit_name = "filter_col_unit"
        filter_col_unit2_name = "filter_col_unit2"
        cell_ll = [None, [0, 0]][0]

        # top margin
        if self.filter_margin_top is not None:
            filter_margin_top = self.filter_margin_top
        else:
            filter_margin_top = self.filter_margin_top_nondim * self.pitch_a

        # --- build
        self.filter_cell = filter_with_sidewall(
            layout=self.layout,
            layer=self.l1,
            filter_len_nondim=filter_len_nondim,
            filter_pitch_entity=filter_pitch_entity,
            filter_half_pitch_nondim=filter_half_pitch_nondim,
            filter_area_ll=filter_area_ll,
            filter_area_dims=filter_area_dims,
            filter_core_entity=filter_core_entity,
            filter_core_entity_offset=filter_core_entity_offset,
            filter_margin_top=filter_margin_top,
            num_extra_column=num_extra_column,
            sidewall_width=sidewall_width,
            cell_target=cell_target,
            opt_clip=opt_clip,
            filter_cell_name=filter_cell_name,
            filter_row_unit_name=filter_row_unit_name,
            filter_unit_name=filter_unit_name,
            filter_col_unit_name=filter_col_unit_name,
            filter_col_unit2_name=filter_col_unit2_name,
            block_width=[
                self.filter_block_width_dep_side,
                self.filter_block_width_acc_side,
            ],
            # decorator kwargs
            cell_ll=cell_ll,
        )

        # return cell_target
        return self.filter_cell

    def _add_multi_inlet(
        self,
    ):
        """Make a multi-inlet."""

        # --- set var from self attr
        config = self.config_multi_inlet

        # --- pop any key required at the assembly level that should not be
        # passed to downstream
        assembly_offset = None
        if type(config) is dict:
            assembly_offset = config.pop("assembly_offset", None)

        # build
        bb = bbox(self.layout)
        inlet = DLD.get_multi_io_element(
            config=config,
            bb=bb,
            config_default={
                "sidewall_width_leftmost": self.sidewall_width,
                "sidewall_width_rightmost": self.sidewall_width,
                "sidewall_width": self.side_length_w,
                "bar_dims": [self.side_length_w, 3000],
                "pitch": self.pitch_w,
            },
        )

        # assembly
        self.add(
            element=inlet,
            snap_direction="top",
            offset=assembly_offset,
            target_cell_name="Inlet",
        )

    def _add_collection(
        self,
    ):
        """Make a collection component with vias."""

        collection = self.layout.create_cell("collection")
        collection_tot = self.layout.create_cell("collection_tot")
        self.collection_tot = collection_tot
        self.collection = collection

        collection_tot.insert(
            db.DCellInstArray(collection.cell_index(), db.DTrans())
        )

        """
        Can use different splitter elements for zig-zag and bump collecting
        channels.
        """
        l1 = self.l1

        if self.opt_mirror:
            print(
                f"""{"-" * 70}
NOTE:
`opt_mirror` is True. The collection design is not comprehensively tested with
this feature yet. Check the design of collection channels and their hydraulic
resistance balance.
In particular, there may be a bump collection channel crossing the mirror axis.
The resistance of this channel is currently considered as that of a pair of
parallel channels with a width equal to half of that of the real central
channel. If the width (compared to height) is sufficiently large, the error
should be negligible.
Otherwise, there can be large errors associated with the hydraulic resistance of
this central channel.
{"-" * 70}
                """
            )

        # --------------------------------------------------------------------
        # coordinates/dims of key points
        # --------------------------------------------------------------------
        # ------------------------------------
        # adding collection sidewalls
        # ------------------------------------
        # if self.sidewall_width is not None:
        if self.sidewall_width > 0:
            p1_collection_sidewall = [
                self.dep_dots_full[-1][0, 0],
                bbox(self.single_unit_cell)[0][1]
                - self.collection_margin_top
                - self.zz_len_upstream
                - self.zz_len_downstream,
            ]

            p2_collection_sidewall = [
                p1_collection_sidewall[0],
                bbox(self.single_unit_cell)[0][1],
            ]
            p3_collection_sidewall = [
                bbox(self.col_cell)[0][0],
                p2_collection_sidewall[1],
            ]
            p4_collection_sidewall = [
                p3_collection_sidewall[0],
                p1_collection_sidewall[1],
            ]

            collection_sidewall_points = [
                p1_collection_sidewall,
                p2_collection_sidewall,
                p3_collection_sidewall,
                p4_collection_sidewall,
            ]
            collection_left_sidewall = db.Region(
                self.TDBU * polygon(collection_sidewall_points)
            )

        zz_collection_width = (
            self.zz_width_to_width_tot * self.collection_core_width_tot
        )
        zz_collection_width = (
            np.round(zz_collection_width / self.zz_bar_pitch)
            * self.zz_bar_pitch
        )
        bmp_collection_width = (
            self.collection_core_width_tot - zz_collection_width
        )

        zz_num_ch_side_us = np.ceil(zz_collection_width / self.zz_bar_pitch)
        bmp_num_ch_central = np.ceil(bmp_collection_width / self.bmp_bar_pitch)

        # --------------------------------------------------------------------
        # check resistances of bmp and zz channels to
        # ensure an acceptable balance
        # --------------------------------------------------------------------
        # target depth of deep and shallow channels
        height = self.height * 1e-6
        height_deep = self.height_deep * 1e-6
        bus_width = self.bus_width * 1e-6
        bus_length = self.bus_length * 1e-6

        # fluid thrmoprops
        fluid_mu = self.fluid_mu

        # condition of balance
        R_zz_over_R_bmp_target = bmp_collection_width / zz_collection_width

        # central channels
        len_central = (self.zz_len_downstream + self.zz_len_upstream) * 1e-6
        channel_center_resist = (
            resist_channel(
                length=len_central,
                width=self.bmp_bar_gap * 1e-6,
                height=height,
                mu=fluid_mu,
            )
            / bmp_num_ch_central
        )

        # side channels
        len_side_us = self.zz_len_upstream * 1e-6
        len_side_ds = (
            self.zz_len_downstream
            - self.zz_len_downstream_bottom
            - 0.5 * self.via_dia_outer_ring
        ) * 1e-6

        # avg of inlet (W) and outlet (~W/2) of ds,
        # where W=w_tot_side-w_tot_center (non-mirrored widths)
        w_side_ds = (
            0.5 * (zz_collection_width + self.via_dia_outer_ring / 2) * 1e-6
        )

        # side channels resistance
        side_us_resist = (
            resist_channel(
                length=len_side_us,
                width=self.zz_bar_gap * 1e-6,
                height=height,
                mu=fluid_mu,
            )
            / zz_num_ch_side_us
        )

        side_ds_resist = resist_channel(
            length=len_side_ds,
            width=w_side_ds,
            height=height,
            mu=fluid_mu,
        )
        channel_side_resist = side_us_resist + side_ds_resist

        # Deep bus channels
        channel_bus_resist = resist_channel(
            length=bus_length, width=bus_width, height=height_deep, mu=fluid_mu
        )

        # -------------------------------------
        # resistance ratios
        # -------------------------------------
        R_bus = channel_bus_resist
        R_zz = channel_side_resist
        R_bmp = channel_center_resist
        R_zz_ds = side_ds_resist
        R_zz_us = side_us_resist

        R_zz_over_R_bmp = R_zz / R_bmp
        R_bus_over_R_zz = R_bus / R_zz
        R_bus_over_R_bmp = R_bus / R_bmp
        R_zz_ds_over_R_zz_us = R_zz_ds / R_zz_us

        if self.opt_report_collection:
            print(
                f"""collection specs
{"-" * 60}
concentration enhancement factor:\
{self.collection_core_width_tot/bmp_collection_width: .3f}
{"-" * 60}
Note:
A higher level of automation is still lacking. Therefore, read the following
carefully.
Compare important specified parameters (input) related to the geometry of
collection component with those in the produced CAD file to make sure they
match.
Check for the number of zz and bump channels, and their gaps.
In particular, the last zz/bump channel close to the sidewall may be narrower
than the specified value due to lack of space, in which case its hydraulic
resistance may be different from that estimated by using the specified gap.
Note that `zz_bar_offset_w` and `bmp_bar_offset_w` can be used to slide the
bars left or right as needed to mitigate the issue with lack of space.

zz_collection_width: {zz_collection_width}
bmp_collection_width: {bmp_collection_width}
zz_bar_gap: {self.zz_bar_gap}
bmp_bar_gap: {self.bmp_bar_gap}
zz_num_ch_side_us: {zz_num_ch_side_us}
bmp_num_ch_central: {bmp_num_ch_central}
{"-" * 50}
Important metrics reflecting the correctness of the hydraulic balance.
In particular, `R_zz_over_R_bmp/R_zz_over_R_bmp_target` needs to be close to
1.0. In order to add a slight bias towards bmp collection to prevent large
particles from escaping towards the zz collection at the end of channel, the
value of `R_zz_over_R_bmp/R_zz_over_R_bmp_target` could be configured to be
slightly larger than 1.0. For example, between 1.0 and 1.05.

R_zz/R_bmp: {R_zz_over_R_bmp}
R_zz/R_bmp target: {R_zz_over_R_bmp_target}
R_zz_over_R_bmp/R_zz_over_R_bmp_target: {R_zz_over_R_bmp/R_zz_over_R_bmp_target}
{"-" * 50}
R_bmp: {R_bmp}
R_zz: {R_zz}
R_zz_ds: {R_zz_ds}
R_zz_us: {R_zz_us}
R_zz_ds/R_zz_us: {R_zz_ds_over_R_zz_us}
{"-" * 50}
Comparing resistances with that of i/o bus to check if the i/o bus has a
negligible resistance.

R_bus/R_zz: {R_bus_over_R_zz}
R_bus/R_bmp: {R_bus_over_R_bmp}
{"-" * 50}
"""
            )

        # --------------------------------------------------------------------

        # Adding extra dummy bars on both side of zz and bmp windows to allow
        # for offseting (sliding) laterally. The excess will be clipped later.
        zz_num_excess_dummy_bars_each_side = 2
        bmp_num_excess_dummy_bars_each_side = 2

        # ref points
        p1 = [
            self.dep_dots_full[-1][0, 0],
            bbox(self.single_unit_cell)[0][1]
            - self.collection_margin_top
            - self.zz_len_upstream
            - self.zz_len_downstream,
        ]

        p2 = [self.dep_dots_full[-1][0, 0], bbox(self.single_unit_cell)[0][1]]
        # p3 = [bbox(self.col_cell)[0][0], bbox(self.single_unit_cell)[0][1]]
        p4 = [bbox(self.col_cell)[0][0], p1[1]]

        # lowest left of zz bars
        zz_bar_ll = [
            p2[0]
            - zz_num_excess_dummy_bars_each_side * self.zz_bar_pitch
            + self.zz_bar_pitch / 2
            + self.zz_bar_gap / 2
            + self.zz_bar_offset_w,
            p2[1] - self.collection_margin_top - self.zz_len_upstream,
        ]

        # lowest left of bmp bars
        bmp_bar_ll = [
            p2[0]
            + zz_collection_width
            - bmp_num_excess_dummy_bars_each_side * self.bmp_bar_pitch
            + self.side_length_w
            - 3.0 * self.gap_w
            + self.bmp_bar_offset_w,
            p1[1],
        ]

        # zz-ds window: consisting of two windows: top (within fluidic ch) and
        # low (outside of fluidic ch)
        # large window: union of top and low
        zz_ds_p1 = p1
        zz_ds_p2 = [p1[0] + zz_collection_width, zz_bar_ll[1]]
        self.zz_ds_box_points = [zz_ds_p1, zz_ds_p2]
        w_large = db.Region(self.TDBU * db.DBox(*zz_ds_p1, *zz_ds_p2))

        # top window
        zz_ds_top_p1 = [
            p1[0],
            p1[1] + self.zz_len_downstream_bottom,
        ]

        # -----------
        # via center
        # -----------
        self.via_center = [
            p4[0],
            zz_ds_top_p1[1] + self.via_dia_outer_ring / 2.0,
        ]
        # -----------
        if self.zz_ds_top_win__topright_tip_width_large is None:
            self.zz_ds_top_win__topright_tip_width_large = 1.0 * self.pitch_w
        if self.zz_ds_top_win__topright_tip_width_small is None:
            self.zz_ds_top_win__topright_tip_width_small = 0.5 * self.pitch_w

        zz_ds_top_p2 = [
            self.via_center[0] + self.via_dia_outer_ring / 2.0,
            self.via_center[1],
        ]
        zz_ds_top_p3 = [
            p1[0]
            + zz_collection_width
            - self.zz_ds_top_win__topright_tip_width_large,
            p1[1]
            + self.zz_len_downstream
            - self.zz_len_downstream_init_extension,
        ]
        zz_ds_top_p4 = [
            p1[0]
            + zz_collection_width
            - self.zz_ds_top_win__topright_tip_width_small,
            p1[1]
            + self.zz_len_downstream
            - self.zz_len_downstream_init_extension,
        ]
        zz_ds_top_p5 = [
            p1[0]
            + zz_collection_width
            - self.zz_ds_top_win__topright_tip_width_small,
            p1[1] + self.zz_len_downstream,
        ]
        zz_ds_top_p6 = [zz_ds_top_p1[0], zz_ds_top_p5[1]]
        zz_ds_top_points = [
            zz_ds_top_p1,
            zz_ds_top_p2,
            zz_ds_top_p3,
            zz_ds_top_p4,
            zz_ds_top_p5,
            zz_ds_top_p6,
        ]

        if zz_ds_top_p6[1] != zz_bar_ll[1]:
            print(f"zz_ds_top_p6: {zz_ds_top_p6} & zz_bar_ll: {zz_bar_ll}")
        assert np.isclose(
            zz_ds_top_p6[1], zz_bar_ll[1], atol=1e-5, rtol=1e-8
        ), f"""zz_ds_top_p6[1]={zz_ds_top_p6[1]} not sufficiently close to
zz_bar_ll[1]={zz_bar_ll[1]}"""

        # ------------------------------------
        # adding zz bars
        # ------------------------------------
        collection_unit = self.layout.create_cell("collection_unit")
        bar_tip_height = self.pitch_a
        zz_bar = polygon(
            [
                [0, 0],
                [self.zz_bar_dim[0], 0],
                [self.zz_bar_dim[0], self.zz_bar_dim[1] - bar_tip_height],
                [self.zz_bar_dim[0] / 2, self.zz_bar_dim[1]],
                [0, self.zz_bar_dim[1] - bar_tip_height],
            ]
        )
        zz_bar = db.Region(self.TDBU * zz_bar)

        collection_unit.shapes(l1).insert(
            zz_bar, db.DTrans(db.DVector(*zz_bar_ll))
        )

        # array of zz bars
        generic_array(
            layout=self.layout,
            cell_src=collection_unit,
            cell_target=collection,
            pitch=[
                self.zz_bar_pitch,
                1,
            ],  # set pitch[1] equal to length[1] --> only 1 item in y-dir
            # a larger array is created to allow offset. The excess will be
            # clipped in the next step.
            length=[
                zz_collection_width
                + 2.0 * zz_num_excess_dummy_bars_each_side * self.zz_bar_pitch,
                1,
            ],
        )
        # clipping bars out of boundary
        clip_box = db.DBox(*p1, p1[0] + zz_collection_width, p2[1])
        clip_box = db.Region(self.TDBU * clip_box)
        region = db.Region(collection.begin_shapes_rec(l1))
        region = region & clip_box
        collection.clear()
        collection.shapes(l1).insert(region)

        # ------------------------------------
        # adding bmp bars
        # ------------------------------------
        collection_unit = self.layout.create_cell("collection_unit_bmp")
        tmp_cell_to_clip = self.layout.create_cell("tmp_cell_to_clip")
        bar_tip_height = self.pitch_a
        bmp_bar = polygon(
            [
                [0, 0],
                [self.bmp_bar_dim[0], 0],
                [self.bmp_bar_dim[0], self.bmp_bar_dim[1] - bar_tip_height],
                [self.bmp_bar_dim[0] / 2, self.bmp_bar_dim[1]],
                [0, self.bmp_bar_dim[1] - bar_tip_height],
            ]
        )
        bmp_bar = db.Region(self.TDBU * bmp_bar)

        collection_unit.shapes(l1).insert(
            bmp_bar, db.DTrans(db.DVector(*bmp_bar_ll))
        )

        # array of bmp bars
        generic_array(
            layout=self.layout,
            cell_src=collection_unit,
            cell_target=tmp_cell_to_clip,
            pitch=[
                self.bmp_bar_pitch,
                1,
            ],  # set pitch[1] equal to length[1] --> only 1 item in y-dir
            length=[
                bmp_collection_width
                + 2.0
                * bmp_num_excess_dummy_bars_each_side
                * self.bmp_bar_pitch,
                1,
            ],
        )

        # clipping bars out of boundary
        clip_box = db.DBox(
            p1[0] + zz_collection_width,
            p1[1],
            p1[0] + self.collection_core_width_tot,
            p2[1],
        )
        clip_box = db.Region(self.TDBU * clip_box)
        region = db.Region(tmp_cell_to_clip.begin_shapes_rec(l1))
        region = region & clip_box
        tmp_cell_to_clip.clear()
        collection.shapes(l1).insert(region)

        if self.opt_mirror:
            region = db.Region(collection.begin_shapes_rec(l1))
            dx_trans = 2.0 * self.x_mirror
            this_trans_vec = db.DVector(dx_trans / self.layout.dbu, 0.0)
            this_transf = db.DTrans(db.DTrans.M90, this_trans_vec)
            region += region.transformed(this_transf)
            collection.clear()
            collection.shapes(l1).insert(region)

        # ------------------------------------
        # adding collection sidewalls
        # ------------------------------------
        if self.sidewall_width > 0:
            collection.shapes(l1).insert(collection_left_sidewall)

            # right sidewall by mirroring the left one
            if self.opt_mirror:
                dx_trans = 2.0 * self.x_mirror
                collection.shapes(l1).insert(
                    collection_left_sidewall,
                    db.DTrans(db.DTrans.M90, dx_trans, 0),
                )
            else:
                ll_collection_sidewall_right = [
                    # bbox(self.single_unit_cell)[1][0]-self.sidewall_width,
                    self.acc_dots_full[-1][0, 0],
                    bbox(collection_left_sidewall)[0][1],
                ]
                rr_collection_sidewall_right = [
                    bbox(self.single_unit_cell)[1][0],
                    bbox(collection_left_sidewall)[1][1],
                ]

                collection_right_sidewall = db.Region(
                    self.TDBU
                    * db.DBox(
                        *ll_collection_sidewall_right,
                        *rr_collection_sidewall_right,
                    )
                )
                collection.shapes(l1).insert(collection_right_sidewall)

        # ------------------------------------
        # adding collection zig-zag window
        # ------------------------------------
        via = circle(
            lx=self.via_dia_outer_ring,
            ly=self.via_dia_outer_ring,
            num_points=32,
            dbu=self.layout.dbu,
        )
        tmp_cell = self.layout.create_cell("via")
        tmp_cell.shapes(l1).insert(via, db.DTrans(db.DVector(*self.via_center)))
        via = db.Region(tmp_cell.begin_shapes_rec(l1))

        # half via
        half_via = via & w_large

        # top window
        w_top = db.Region(self.TDBU * polygon(zz_ds_top_points))
        w_top += half_via

        # lower window
        w_low = w_large - w_top

        # decoration features!
        collection_entity_dim = self.collection_entity_dim
        collection_entity_pitch_out = self.collection_entity_pitch_out
        collection_entity_pitch_in = self.collection_entity_pitch_in

        if collection_entity_dim is None:
            collection_entity_dim = (self.pitch_w / 2.0, self.pitch_w / 2.0)
        if collection_entity_pitch_out is None:
            collection_entity_pitch_out = (
                1.5 * self.pitch_w,
                1.5 * self.pitch_w,
            )
        if collection_entity_pitch_in is None:
            collection_entity_pitch_in = (4 * self.pitch_w, 4 * self.pitch_w)

        decor_entity = db.Region(
            self.TDBU * db.DBox(0, 0, *collection_entity_dim)
        )

        this_trans = db.DTrans(
            db.DVector(
                (p1[0] + self.pitch_w) / self.layout.dbu,
                (p1[1] + self.pitch_w) / self.layout.dbu,
            )
        )

        decor_entity.transform(this_trans)
        decor_cell = self.layout.create_cell("decor")
        tmp_cell = self.layout.create_cell("tmp")
        decor_cell.shapes(l1).insert(decor_entity)
        generic_array(
            layout=self.layout,
            cell_src=decor_cell,
            cell_target=tmp_cell,
            pitch=collection_entity_pitch_out,
            length=[
                zz_collection_width,
                self.zz_len_downstream - self.zz_len_downstream_init_extension,
            ],
        )
        decor_out = db.Region(tmp_cell.begin_shapes_rec(l1))

        tmp_cell = self.layout.create_cell("tmp2")
        generic_array(
            layout=self.layout,
            cell_src=decor_cell,
            cell_target=tmp_cell,
            pitch=collection_entity_pitch_in,
            length=[zz_collection_width, self.zz_len_downstream],
        )
        decor_in = db.Region(tmp_cell.begin_shapes_rec(l1))

        # modifying lower window
        w_low -= decor_out

        # modifying upper window
        # w_top=(w_top&decor_in)-via #for not having entities within via area
        w_top = w_top & decor_in

        # mirroring entities
        if self.opt_mirror:
            dx_trans = 2.0 * self.x_mirror
            this_trans_vec = db.DVector(dx_trans / self.layout.dbu, 0.0)
            this_transf = db.DTrans(db.DTrans.M90, this_trans_vec)
            w_large += w_large.transformed(this_transf)
            w_low += w_low.transformed(this_transf)
            w_top += w_top.transformed(this_transf)

        # emptying the large window region
        region = db.Region(collection.begin_shapes_rec(l1))
        region -= w_large
        collection.clear()
        collection.shapes(l1).insert(region)

        # adding upper window
        collection.shapes(l1).insert(w_top)

        # adding lower window
        collection.shapes(l1).insert(w_low)

        # clipping out of boundary entities
        clip_box = db.DBox(
            *p4, p4[0] + 2 * (self.x_mirror - p4[0]), bbox(collection)[1][1]
        )
        clip_box = db.Region(self.TDBU * clip_box)
        region = db.Region(collection.begin_shapes_rec(l1))
        region = region & clip_box
        collection.clear()
        collection.shapes(l1).insert(region)

        self.prune(
            [
                "collection_unit",
                "collection_unit_bmp",
                "tmp",
                "tmp2",
                "tmp_cell_to_clip",
                "via",
            ]
        )

        # ------------------------------------------------------------
        # adding via layer
        # ------------------------------------------------------------
        # via_layer=self.layout.layer('via_layer')
        via_layer = self.layout.layer(*self.layer_2)
        self.l2 = via_layer

        via_cell = self.layout.create_cell("VIA")
        collection_tot.insert(
            db.DCellInstArray(via_cell.cell_index(), db.DTrans())
        )

        reg_via = db.Region(
            self.TDBU
            * db.DPolygon.ellipse(
                db.DBox(
                    self.via_center[0] - self.via_dia / 2.0,
                    self.via_center[1]
                    - self.via_dia / 2.0
                    - (self.via_dia_outer_ring - self.via_dia) / 2.0,
                    self.via_center[0] + self.via_dia / 2.0,
                    self.via_center[1]
                    + self.via_dia / 2.0
                    - (self.via_dia_outer_ring - self.via_dia) / 2.0,
                ),
                64,
            )
        )
        reg_half_via = reg_via - db.Region(
            self.TDBU
            * db.DBox(
                self.via_center[0] - self.via_dia / 2.0,
                self.via_center[1]
                - self.via_dia / 2.0
                - (self.via_dia_outer_ring - self.via_dia) / 2.0,
                self.via_center[0],
                self.via_center[1]
                + self.via_dia / 2.0
                - (self.via_dia_outer_ring - self.via_dia) / 2.0,
            )
        )

        # mirroring entities
        if self.opt_mirror:
            dx_trans = 2.0 * self.x_mirror
            this_trans_vec = db.DVector(dx_trans / self.layout.dbu, 0.0)
            this_transf = db.DTrans(db.DTrans.M90, this_trans_vec)
            reg_half_via += reg_half_via.transformed(this_transf)

        # inserting via region(s) in via cell
        via_cell.shapes(via_layer).insert(reg_half_via)

        return collection_tot

    def _smoothen_dep_sidewall(self, col_cell, l1):
        """Smoothen sep sidewall at downstreammost of column by inserting
        extra appropriate shapes.
        Currently, it is applicable only when ``dep_sidewall_theme=0``.

        .. note::
            The extra shapes are inserted in the cell `smooth_col_cell`, which
            itself is inside `col_cell` rather than `single_unit_cell`.
        """

        flag_smooth_col_cell = False  # to be examined more later
        smooth_col_cell = None

        if self.dep_sidewall_theme == 0:
            smooth_col_cell = self.layout.create_cell("Smoothing_col")
            flag_smooth_col_cell = True
            col_cell.insert(db.DCellInstArray(smooth_col_cell, db.DTrans()))

            p1 = [
                self.dep_dots_full[-1][-2, 0],
                self.dep_dots_full[-1][0, 1] - self.pitch_a / 2,
            ]
            p2 = [p1[0], self.dep_dots_full[-1][0, 1]]
            p3 = self.dep_dots_full[-1][0].tolist()
            p4 = [p3[0], p1[1]]
            add_to_smooth = db.Region(self.TDBU * polygon([p1, p2, p3, p4]))
            smooth_col_cell.shapes(l1).insert(add_to_smooth)

        # mirroring smooth_col_cell
        if flag_smooth_col_cell:
            if self.opt_mirror:
                this_mirror = self.x_mirror
            else:
                this_mirror = (
                    self.dep_dots_full[-1][0, 0] + self.acc_dots_full[-1][0, 0]
                ) / 2
            dx_trans = 2.0 * this_mirror
            smooth_col_cell.shapes(l1).insert(
                add_to_smooth, db.DTrans(db.DTrans.M90, dx_trans, 0)
            )

        self.smooth_col_cell = smooth_col_cell

    def _add_collection_sideway(
        self,
    ):
        """Make a sideway collection component with opening on right and/or
        left sides."""

        collection = self.layout.create_cell("collection_sideway")
        collection_tot = self.layout.create_cell("collection_sideway_tot")
        self.collection_sideway_tot = collection_tot
        self.collection_sideway = collection

        collection_tot.insert(
            db.DCellInstArray(collection.cell_index(), db.DTrans())
        )

        # ------------------------------------------------
        sidewall_width = self.sidewall_width
        if sidewall_width is None:
            sidewall_width = 0

        bb = bbox(self.layout)
        grating_area_ll = [
            bb[0][0] + sidewall_width,
            bb[0][1] - self.collection_sideway_width,
        ]
        grating_area_dims = [
            bb[1][0] - bb[0][0] - 2 * sidewall_width,
            self.collection_sideway_width,
        ]
        grating_pitch = [self.pitch_w, self.pitch_a]

        bar = self._get_core_entity_region()
        # bar_offset=[0, self.pitch_a/2.]
        bar_offset = [
            self.dep_dots_full[-1][0, 0]
            - grating_area_ll[0]
            - self.pitch_w / 2.0,
            self.pitch_a / 2.0,
        ]

        # --- config opening(s) -- sidewall_width_lst = [left sidewall width,
        # right sidewall width]
        sidewall_width_lst = [sidewall_width, sidewall_width]
        if self.opt_collection_sideway_left_side:
            sidewall_width_lst[0] = 0.0
        if self.opt_collection_sideway_right_side:
            sidewall_width_lst[1] = 0.0

        collection, _ = grating_with_sidewall(
            # collection = grating_with_sidewall(
            layout=self.layout,
            layer=self.l1,
            grating_pitch=grating_pitch,
            grating_area_dims=grating_area_dims,
            bar=bar,
            grating_area_ll=grating_area_ll,
            cell_target=collection,
            bar_offset=bar_offset,
            num_extra_bar_column=0,
            sidewall_width=sidewall_width_lst,
            opt_clip=True,
            grating_cell_name="grating_sw",
            unit_grating_cell_name="unit_grating_sw",
            margin_top=0,
            block_width=[0, 0],
            # cell decorator params
        )

        return collection_tot

    def _add_collection_simple(
        self,
    ):
        """Make a simple collection component."""

        collection = self.layout.create_cell("collection")
        collection_tot = self.layout.create_cell("collection_tot")
        self.collection_tot = collection_tot
        self.collection = collection

        collection_tot.insert(
            db.DCellInstArray(collection.cell_index(), db.DTrans())
        )

        sidewall_width = self.sidewall_width
        if sidewall_width is None:
            sidewall_width = 0

        bb = bbox(self.layout.top_cells()[0])
        grating_area_ll = [
            bb[0][0] + sidewall_width,
            bb[0][1]
            - self.collection_margin_top
            - self.collection_offset_a
            - self.collection_bar_dims[1],
        ]
        grating_area_dims = bb[1][0] - bb[0][0] - 2 * sidewall_width

        num_extra_bar_column = 4

        collection, _ = grating_with_sidewall(
            # collection = grating_with_sidewall(
            layout=self.layout,
            layer=self.l1,
            grating_pitch=self.collection_bar_pitch,
            grating_area_dims=grating_area_dims,  # area betweensidewalls
            bar_dims=self.collection_bar_dims,
            bar=None,  # A `db.Region` object as the bar entity
            cell_target=collection,  # target cell for grating with sidewall
            grating_area_ll=grating_area_ll,
            bar_offset=[self.collection_offset_w, self.collection_offset_a],
            sidewall_width=sidewall_width,  # sidewall width
            num_extra_bar_column=num_extra_bar_column,
            opt_clip=True,  # whether to clip bars outside of grating area
            margin_top=self.collection_margin_top,
        )

        return collection_tot

    def get_length(
        self,
    ):
        """Returns the length of one **full** 1D array of core.DLD"""

        return self.num_unit * self.pitch_a * self.Np

    def _get_num_parallel_core_dld_1D_array(
        self,
    ):
        """Returns the number of 1D arrays of core.DLD (count of **full**
        functional DLD units) used in this block."""

        return DLD.get_num_parallel_core_dld_1D_array(
            array_counts=self.array_counts,
            opt_mirror_before_array=self.opt_mirror_before_array,
            opt_mirror=self.opt_mirror,
        )

    def _get_flow_rate(
        self,
        delta_p=1e5,
    ):
        """Returns volumetric flow rate of block.DLD"""

        vfr = DLD.get_flow_rate(
            fluid_mu=self.fluid_mu,
            Nw=self.Nw,
            length=self.get_length(),
            height=self.height,
            side_length_w=self.side_length_w,
            side_length_a=self.side_length_a,
            pitch_w=self.pitch_w,
            pitch_a=self.pitch_a,
            delta_p=delta_p,
            num_parallel_unit=self.get_num_parallel_core_dld_1D_array(),
        )

        return vfr

    # ------------------------------------------------------------------------
    # Static methods
    # ------------------------------------------------------------------------

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
        # considerations
        height=None,
        num_unit=None,
        num_unit_extra=None,
        num_unit_extra_nondim=None,
        # constraints
        range_Np=None,
        range_Nw=None,
        range_width=None,
        range_length=None,
        # volumetric flow rate (vfr)
        min_vfr_per_bar=None,
        min_vfr_ul_per_min_per_bar=None,
        min_vfr_ml_per_hr_per_bar=None,
        fluid_mu=None,
        num_parallel_unit=None,
        # Die area (mm square)
        max_die_area_mmsq=None,
        # gap over critical dia.
        min_gap_over_dc=None,
        # constraint Off mode
        turn_off_constraints=None,
    ):
        """Returns a set of geometrical configurations for a DLD system
        subject to a set of constraints.

        .. note::
            Currently, the function applys **Pass/Fail** tests to a set of
            given constraints.
            This can be revised in the future for a number of sets of
            geometrical configurations with the highest quality scores to be
            returned.

        Returns
        -------
        dict
            Geometrical configurations.
        """

        # --- default params
        if turn_off_constraints is None:
            turn_off_constraints = False
        if num_parallel_unit is None:
            num_parallel_unit = 1

        # --------------------------------------------------------------------
        # Constraints
        #
        # Note:
        #   - We do not set any constraint on minimum allowed volumetric flow
        # rate as it
        # is highly application-dependent. An explicit value can be passed by
        # user though.
        #
        #   - The specified ranges have been tried to be reasonably wide
        # to cover most applications spanning from parallelized nano-dld
        # systems, wherein footprint of each **full** dld block is small, to
        # traditional dld systems with relatively large footprints.
        # Regardless, these constraints can be explicitly provided by user as
        # needed.
        #
        #   - The constraints of Np and Nw ranges are relaxed for the case
        # that those params are provided explicitly.
        # --------------------------------------------------------------------
        _range_Np = [8, 50]
        _range_Nw = [int(8), int(1.0e5)]
        _range_width = [50, 1.0e4]
        _range_length = [500, 4.0e4]
        _num_unit_extra = None  # by default, the nondim form is preferred.
        _num_unit_extra_nondim = 0.1
        _fluid_mu = 1e-3

        # considerations
        num_unit_extra = DLD._get_val_of_constraint(
            num_unit_extra, _num_unit_extra
        )
        num_unit_extra_nondim = DLD._get_val_of_constraint(
            num_unit_extra_nondim, _num_unit_extra_nondim
        )
        fluid_mu = DLD._get_val_of_constraint(fluid_mu, _fluid_mu)
        # constraints
        range_Np = DLD._get_val_of_constraint(range_Np, _range_Np)
        range_Nw = DLD._get_val_of_constraint(range_Nw, _range_Nw)
        range_width = DLD._get_val_of_constraint(range_width, _range_width)
        range_length = DLD._get_val_of_constraint(range_length, _range_length)
        # volumetric flow rate
        min_vfr_per_bar = DLD.convert_vfr_to_SI_unit(
            min_vfr_per_bar,
            min_vfr_ul_per_min_per_bar,
            min_vfr_ml_per_hr_per_bar,
        )

        # --- In case of explicitly provided params
        # Np: 1. from passed ``Np`` (below), 2. from passed ``range_Np``
        # (above), 3. from built-in ``range_Np`` (above)
        if Np is not None:
            range_Np = [Np, Np]

        # ----------------------------------------------------------------
        # Explore param space
        # aiming at maximizing Np (minimizing clogging risk)
        # -> scan in descending direction
        # ----------------------------------------------------------------
        for this_Np in range(int(range_Np[1]), int(range_Np[0]) - 1, -1):

            # --- geometrical attributes
            _dict_to_unpack = core_DLD.get_geom_config_auto(
                Np=this_Np,
                d_c=d_c,
                width=width,
                Nw=Nw,
                gap_w=gap_w,
                gap_a=gap_a,
                pitch_w=pitch_w,
                pitch_a=pitch_a,
                height=height,
            )
            this_gap_w = _dict_to_unpack.pop("gap_w")
            this_gap_a = _dict_to_unpack.pop("gap_a")
            this_pitch_w = _dict_to_unpack.pop("pitch_w")
            this_pitch_a = _dict_to_unpack.pop("pitch_a")
            this_height = _dict_to_unpack.pop("height")
            this_side_length_w = _dict_to_unpack.pop("side_length_w")
            this_side_length_a = _dict_to_unpack.pop("side_length_a")

            # --- constraint: gap over critical dia.
            if min_gap_over_dc is not None:
                this_d_c = core_DLD.get_dc(
                    Np=this_Np,
                    gap_w=this_gap_w,
                    pitch_w=this_pitch_w,
                    pitch_a=this_pitch_a,
                )

                # --- Not meeting the constraint criterion
                if this_gap_w / this_d_c < min_gap_over_dc:
                    continue

            # ----------------------------------------------------------------
            # Nw: number of fluidic lanes/columns
            #
            # Minimize Nw for the given Np subject to constraints and
            # considerations.
            # ----------------------------------------------------------------

            # Nw: 1. from passed ``width`` (below), 2. from passed ``Nw``
            # (below), 3. from passed ``range_Nw`` (above), 4. from built-in
            # ``range_Nw`` (above)
            if width is not None:
                if Nw is not None:
                    if Nw != np.ceil(width / this_pitch_w):
                        raise ValueError(
                            f"""
Both ``Nw`` and ``width`` are provided, and are inconsistent:
Nw={Nw} and width={width}.
The latter requires Nw of {int(np.ceil(width/this_pitch_w))}
in presence of pitch_w: {this_pitch_w}"""
                        )
                tmp_Nw = int(np.ceil(width / this_pitch_w))
                range_Nw = [tmp_Nw, tmp_Nw]

            if Nw is not None:
                range_Nw = [Nw, Nw]

            this_Nw = DLD.get_Nw(
                Np=this_Np,
                pitch_a=this_pitch_a,
                pitch_w=this_pitch_w,
                range_Nw=range_Nw,
                range_length=range_length,
                range_width=range_width,
                num_unit=num_unit,
                num_unit_extra=num_unit_extra,
                num_unit_extra_nondim=num_unit_extra_nondim,
                # volumetric flow rate
                min_vfr_per_bar=min_vfr_per_bar,
                fluid_mu=fluid_mu,
                height=this_height,
                side_length_w=this_side_length_w,
                side_length_a=this_side_length_a,
                num_parallel_unit=num_parallel_unit,
                # Die area (mm square)
                max_die_area_mmsq=max_die_area_mmsq,
                # constraint Off mode
                turn_off_constraints=turn_off_constraints,
            )

            if this_Nw is not None:
                # --- params to update after auto config execution
                dict_return = {}
                dict_return["Np"] = this_Np
                dict_return["Nw"] = this_Nw
                dict_return["gap_w"] = this_gap_w
                dict_return["gap_a"] = this_gap_a
                dict_return["pitch_w"] = this_pitch_w
                dict_return["pitch_a"] = this_pitch_a
                dict_return["height"] = this_height
                dict_return["num_unit_extra"] = num_unit_extra
                dict_return["num_unit_extra_nondim"] = num_unit_extra_nondim
                dict_return["fluid_mu"] = fluid_mu

                return dict_return

        msg = f"""Not able to find appropriate Np and Nw subject to these
constraints and considerations:
range_Np: {range_Np}
range_Nw:{range_Nw}
range_width:{range_width}
range_length:{range_length}
num_unit_extra:{num_unit_extra}
num_unit_extra_nondim:{num_unit_extra_nondim}
min_vfr_per_bar:{min_vfr_per_bar}
max_die_area_mmsq:{max_die_area_mmsq}
min_gap_over_dc: {min_gap_over_dc}.

There are a few remedies:
1. Use ``turn_off_constraints=True``
2. Adjust the geometrical constraints ranges according to your requirements,
    e.g., ``range_width=[0, 1e6]``, ``range_length=[0, 1e6]``, etc.
3. In the case of using a partial DLD., e.g., ``num_unit=2``, you can ensure
    the constraints are applied to **full** DLD system by using
    ``get_geom_config_auto_use_auto_num_unit=True``.
4. In the case of using a performance constraint, e.g., ``min_vfr_per_bar``,
    ``max_die_area_mmsq``, or ``min_gap_over_dc``, you may adjust the
    constraint by lowering down the flow rate constraint, increasing the
    maximum allowed die area, and/or decreasing the minimum allowed gap over
    critical diameter threshold."""

        raise ValueError(msg)

    @staticmethod
    def get_Nw(
        Np,
        pitch_a,
        pitch_w,
        # constraints
        range_Nw,
        range_length,
        range_width,
        num_unit=None,
        num_unit_extra=None,
        num_unit_extra_nondim=None,
        # volumetric flow rate
        min_vfr_per_bar=None,
        min_vfr_ul_per_min_per_bar=None,
        min_vfr_ml_per_hr_per_bar=None,
        fluid_mu=1e-3,
        height=None,
        side_length_w=None,
        side_length_a=None,
        num_parallel_unit=1,
        # Die area (mm square)
        max_die_area_mmsq=None,
        # constraint Off mode
        turn_off_constraints=False,
    ):
        """Returns a (minimized) Nw for a given configuration subject to a
        set of constraints.

        Parameters
        ----------
        Np : int
            periodicity
        pitch_a : float
            axial pitch
        pitch_w : float
            lateral pitch
        range_Nw : list
            Min and Max allowed Nw.
        range_length : list
            Min and Max allowed length of DLD system
        range_width : list
            Min and Max allowed width of system.
        num_unit : int, optional
            Number of units, by default None
        num_unit_extra : int, optional
            Number of additional units to be considered for full DLD system,
            by default None
        num_unit_extra_nondim : float, optional
            Number of additional units to be considered for full DLD system
            nondimensionalized by Nw, by default None
        min_vfr_per_bar : float, optional
            Min allowed throughput, `i.e.`, volumetric flow rate, in unit of
            :math:`m^3/sec/bar`, by default None
        min_vfr_ul_per_min_per_bar : float, optional
            Min allowed throughput, `i.e.`, volumetric flow rate, in unit of
            :math:`\\mu L/min/bar`, by default None
        min_vfr_ml_per_hr_per_bar : float, optional
            Min allowed throughput, `i.e.`, volumetric flow rate, in unit of
            :math:`mL/hr/bar`, by default None
        fluid_mu : float, optional
            Fluid dynamic viscosity with a unit of :math:`Pa.sec`, relevant if
            throughput constraint is applied, by default 1e-3
        height : float, optional
            Height of channel, relevant if throughput constraint is applied,
            by default None
        side_length_w : float, optional
            Lateral sidelength of pillars, relevant if throughput constraint
            is applied, by default None
        side_length_a : float, optional
            Axial sidelength of pillars, relevant if throughput constraint is
            applied, by default None
        turn_off_constraints : bool, optional
            Whether to turn off the constraints, by default False

        Returns
        -------
        float, or NoneType
            Found Nw for the configs, otherwise None.
        """

        # ---------------------------------------
        # Constraints-OFF mode
        # ---------------------------------------
        if turn_off_constraints:
            return int(range_Nw[0])

        # volumetric flow rate
        min_vfr_per_bar = DLD.convert_vfr_to_SI_unit(
            min_vfr_per_bar,
            min_vfr_ul_per_min_per_bar,
            min_vfr_ml_per_hr_per_bar,
        )

        for Nw in range(int(range_Nw[0]), int(range_Nw[1]) + 1):
            unit_width = float(Nw * pitch_w)
            sys_length, _ = DLD.get_full_length(
                Np=Np,
                Nw=Nw,
                num_unit=num_unit,
                pitch_a=pitch_a,
                num_unit_extra=num_unit_extra,
                num_unit_extra_nondim=num_unit_extra_nondim,
            )

            # already too long channel --> larger Nw is not an option
            if range_length[1] < sys_length or range_width[1] < unit_width:
                break

            if (
                range_length[0] <= sys_length <= range_length[1]
                and range_width[0] <= unit_width <= range_width[1]
            ):
                # --- check other constraints & considerations, e.g.,
                # throughput.
                _pass_all_tests = True

                # constraint: flow rate
                if min_vfr_per_bar is not None:
                    vfr_per_bar = DLD.get_flow_rate(
                        fluid_mu=fluid_mu,
                        Nw=Nw,
                        length=sys_length,
                        height=height,
                        side_length_w=side_length_w,
                        side_length_a=side_length_a,
                        pitch_w=pitch_w,
                        pitch_a=pitch_a,
                        delta_p=1e5,
                        num_parallel_unit=num_parallel_unit,
                    )

                    if vfr_per_bar < min_vfr_per_bar:
                        _pass_all_tests = False

                # constraint: die area
                if max_die_area_mmsq is not None:
                    die_area_mmsq = (
                        DLD.estimate_die_area(
                            Nw=Nw,
                            pitch_w=pitch_w,
                            sys_length=sys_length,
                            num_parallel_unit=num_parallel_unit,
                        )
                        * 1e-12
                    )

                    # convert to mm-sq unit
                    die_area_mmsq *= 1.0e6

                    if die_area_mmsq > max_die_area_mmsq:
                        _pass_all_tests = False
                # ------------------------------------------------------------

                if _pass_all_tests:
                    return Nw

        return None

    @staticmethod
    def estimate_die_area(
        Nw,
        pitch_w,
        sys_length,
        num_parallel_unit=1,
    ):
        """Returns an estimate of die area.

        .. note::
            - Only the area occupied by DLD pillars is considered.
            - Length params are in micron unit.
        """

        return Nw * pitch_w * sys_length * num_parallel_unit

    @staticmethod
    def get_flow_rate(
        fluid_mu,
        Nw,
        length,
        height,
        side_length_w,
        side_length_a,
        pitch_w,
        pitch_a,
        delta_p=1e5,
        num_parallel_unit=1,
    ):
        """Returns volumetric flow rate of a DLD system consisting of a 1D
        array of core.DLD.

        .. note::
            - input length params have the micron unit.
        """
        # Note that length unit need to be converted from micron to meter
        # before passign to function to calculate resistance.

        resist = resist_dld(
            mu=fluid_mu,
            Nw=Nw,
            length=length * 1e-6,
            height=height * 1e-6,
            diameter=(side_length_w + side_length_a) / 2.0 * 1e-6,
            pitch_w=pitch_w * 1e-6,
            pitch_a=pitch_a * 1e-6,
        )

        vfr = delta_p / resist

        # taking into account the number of parallel **same** units.
        vfr *= num_parallel_unit

        return float(vfr)

    @staticmethod
    def convert_vfr_to_SI_unit(SI=None, ul_per_min=None, ml_per_hr=None):
        # volumetric flow rate
        if SI is None:
            if ul_per_min is not None:
                SI = ul_per_min * 1e-9 / 60.0
            elif ml_per_hr is not None:
                SI = ml_per_hr * 1e-6 / 3600.0

        return SI

    @staticmethod
    def _get_val_of_constraint(val, val_ref):
        """Setting a given constraint to appropriate values according to a
        reference val (``val_ref``) in case the given constraint is None or
        has None component(s)."""

        # processing a range in the form of [min, max]
        if type(val_ref) in [list, tuple]:
            if val is None:
                val = val_ref
            else:
                val = list(val)  # to support tuple arg as well
                for ind_dir in range(2):
                    if val[ind_dir] is None:
                        val[ind_dir] = val_ref[ind_dir]

        # processing a scalar
        elif type(val_ref) in [int, float, type(None)]:
            if val is None:
                val = val_ref

        else:
            raise TypeError(f"Invalid type of ``val_ref``: {type(val_ref)}.")

        return val

    @staticmethod
    def get_full_length(
        Np,
        Nw,
        pitch_a,
        num_unit=None,
        num_unit_extra=None,
        num_unit_extra_nondim=None,
    ):
        """Returns ``length`` and ``num_unit`` as a tuple of
        (``length``, ``num_unit``) for a **full** 1D DLD array.

        .. note::
            ``num_unit_extra`` and ``num_unit_extra_nondim`` are applicable
            only when ``num_unit`` is None or not provided.
        """

        unit_length = float(Np * pitch_a)
        if num_unit is None:
            num_unit = int(Nw)

            if num_unit_extra is not None:
                num_unit += int(num_unit_extra)
            elif num_unit_extra_nondim is not None:
                num_unit = int(np.ceil(Nw * (1 + num_unit_extra_nondim)))

        sys_length = unit_length * num_unit

        return sys_length, num_unit

    @staticmethod
    def get_num_parallel_core_dld_1D_array(
        array_counts=[1, 1],
        opt_mirror_before_array=[False, False],
        opt_mirror=False,
    ):
        """Returns the number of 1D arrays of core.DLD (count of **full**
        functional DLD units)."""

        num = array_counts[0] * array_counts[1]

        # doubling in case of mirroring core.DLD before arraying
        for ind_dir in range(2):
            if opt_mirror_before_array[ind_dir]:
                num *= 2

        # doubling in case of mirrored design
        if opt_mirror:
            num *= 2.0

        return int(num)

    @staticmethod
    def get_multi_io_element(
        config,
        bb,
        config_default=None,
    ):
        """Make a Multi-IO element.

        Some examples of ``config_multi_inlet``:

        **A:**

        .. highlight:: python
        .. code-block:: python

            config_multi_inlet={
                'lst_config':{
                    'bar_dims':[3, 100],
                    'grating_pitch':10,
                    'sidewall_width':[5, 5],
                    },
                'num_branch':4,
                'lst_config_extension':{
                    'bar_len':200,
                    'margin_top':0,
                    'margin_down':10,
                    },
                }

        **B:**

        .. highlight:: python
        .. code-block:: python

            config_multi_inlet={
                'grating_pitch':20,
                'bar_dims':[5, 200],
                'sidewall_width':[5, 5],
                'num_branch':4,
                'lst_config_extension':{
                    'bar_len':200,
                    'margin_top':0,
                    'margin_down':10,
                    },
                }

        **Branches with different widths:**
        The width of projection of branch cross section (including its
        sidewalls) on horizontal axis can be adjusted by ``width_nondim``.

        .. highlight:: python
        .. code-block:: python

            config_multi_inlet={
                'grating_pitch':20,
                'bar_dims':[5, 200],
                'sidewall_width':[5, 5],
                'width_nondim':[0.1, 0.1, 0.8],
                'lst_config_extension':{
                    'bar_len':200,
                    'margin_top':0,
                    'margin_down':10,
                    },
                }


        **Heterogeneous configs of branches:**

        .. highlight:: python
        .. code-block:: python

            config_multi_inlet={
                'lst_config':[
                    {
                    'grating_pitch':20,
                    'bar_dims':[5, 200],
                    'sidewall_width':[5, 5],
                    },
                    {
                    'grating_pitch':10,
                    'bar_dims':[5, 200],
                    'sidewall_width':[5, 5],
                    },
                    ],
                'width_nondim':[0.1, 0.9],
                'lst_config_extension':{
                    'bar_len':200,
                    'margin_top':0,
                    'margin_down':10,
                    },
                }
        """

        # default params
        if config_default is None:
            config_default = {}

        # --- extract params from given ``config_multi_inlet``
        _config_type = type(config)
        width_nondim = None
        if config is None:
            num_branch = 1
            lst_config = None
        elif _config_type is dict:
            # --- pop any param that should not be a key of
            # ``lst_config_extension``
            lst_config = config.pop("lst_config", None)
            num_branch = config.pop("num_branch", None)
            width_nondim = config.pop("width_nondim", None)
            opt_extension = config.pop("opt_extension", None)
            lst_config_extension = config.pop("lst_config_extension", None)

            # case B (see docstring): only valid keys of ``lst_config``
            # remaining
            if lst_config is None:
                lst_config = config
            # case A (see docstring)
            else:
                if type(lst_config) not in [dict, list, tuple]:
                    raise TypeError(
                        f"""A (list of) dict is expected for ``lst_config``,
but a {type(lst_config)} is given."""
                    )
        else:
            raise TypeError(
                f"Invalid type of ``config_multi_inlet``: {_config_type}"
            )

        # --- sanity check
        if type(lst_config) in [list, tuple]:
            if num_branch is not None and num_branch != len(lst_config):
                raise ValueError(
                    f"""Inconsistent values for ``num_branch``: {num_branch}
and count of items in ``lst_config`` {len(lst_config)}"""
                )
            else:
                num_branch = len(lst_config)
        else:
            assert (
                type(lst_config) is dict
            ), f"""A (list of) dict is expected for ``lst_config``, but a
{type(lst_config)} is given."""

        if width_nondim is not None:
            if type(width_nondim) not in [list, tuple]:
                raise TypeError(
                    f"""A list/tuple is expected for ``width_nondim``, while a
{type(width_nondim)} is given."""
                )
        if num_branch is not None and width_nondim is not None:
            if num_branch != len(width_nondim):
                raise ValueError(
                    f"""Inconsistent values for ``num_branch``: {num_branch}
and count of items in ``width_nondim``:{len(width_nondim)}"""
                )

        # --- set ``num_branch``
        if num_branch is None and width_nondim is not None:
            num_branch = len(width_nondim)
        elif num_branch is None and width_nondim is None:
            if type(lst_config) is dict:
                num_branch = 1
            else:
                num_branch = len(lst_config)

        # --- set ``width_nondim``
        if width_nondim is None:
            width_nondim = [1.0 / num_branch for _ in range(num_branch)]
        if sum(width_nondim) != 1.0:
            raise ValueError(
                f"""Sum of ``width_nondim`` values is expected to be 1, while
sum of {width_nondim} is {sum(width_nondim)}"""
            )
        # -------------------------------------------------------------

        # set lst_config as needed
        if lst_config is None:
            lst_config = [{} for _ in range(num_branch)]
        elif type(lst_config) is dict:
            _lst_config = copy.deepcopy(lst_config)
            lst_config = [copy.deepcopy(_lst_config) for _ in range(num_branch)]

        # set lst_config_extension as needed
        if lst_config_extension is None:
            lst_config_extension = [{} for _ in range(num_branch)]
        elif type(lst_config_extension) is dict:
            _lst_config_extension = copy.deepcopy(lst_config_extension)
            lst_config_extension = [
                copy.deepcopy(_lst_config_extension) for _ in range(num_branch)
            ]

        # --- default config
        sidewall_width_leftmost = config_default.pop(
            "sidewall_width_leftmost", 100
        )
        sidewall_width_rightmost = config_default.pop(
            "sidewall_width_rightmost", 100
        )
        sidewall_width = config_default.pop("sidewall_width", 100)
        bar_dims = config_default.pop("bar_dims", [10, 3000])
        grating_pitch = config_default.pop("pitch", 30)
        for sn_config in range(num_branch):
            this_rot = Multi_IO.infer_rot(
                sn_config, num_branch, max_tot_opening_angle=150
            )
            if num_branch == 1:
                this_sidewall_width = [
                    sidewall_width_leftmost,
                    sidewall_width_rightmost,
                ]
            elif sn_config == 0:
                this_sidewall_width = [sidewall_width_leftmost, sidewall_width]
            elif sn_config == num_branch - 1:
                this_sidewall_width = [sidewall_width, sidewall_width_rightmost]
            else:
                this_sidewall_width = [sidewall_width, sidewall_width]
            # cross sectoin of tilted branch is narrower than its
            # desired projection to horizontal axis
            this_sidewall_width[0] *= np.cos(this_rot * np.pi / 180.0)
            this_sidewall_width[1] *= np.cos(this_rot * np.pi / 180.0)

            this_config_default = {
                "bar_dims": bar_dims,
                "grating_pitch": grating_pitch,
                "sidewall_width": this_sidewall_width,
                "rot": this_rot,
            }

            # merge and override any given config into default
            lst_config[sn_config] = merge_two_dicts(
                this_config_default, lst_config[sn_config]
            )

        # infer ``grating_area_dim`` for each branch if not provided
        # explicitly

        # bbox
        box_width = bb[1][0] - bb[0][0]

        for sn_config in range(num_branch):
            if "grating_area_dim" not in lst_config[sn_config]:
                this_rot = lst_config[sn_config]["rot"]
                this_sw = lst_config[sn_config]["sidewall_width"]
                _this_cos = np.cos(this_rot * np.pi / 180)
                #
                this_width = width_nondim[sn_config] * box_width
                this_grating_area_dim = (
                    this_width - (this_sw[0] + this_sw[1]) / _this_cos
                )
                this_grating_area_dim *= _this_cos
                lst_config[sn_config][
                    "grating_area_dim"
                ] = this_grating_area_dim

        # --- default config extension
        if opt_extension is None:
            opt_extension = True
        if opt_extension:
            # default config
            for sn_config in range(num_branch):
                config_extension_default = {
                    "bar_len": 100,
                    "margin_top": 0,
                    "margin_down": 0,
                }

                # merge and override any given config into default
                lst_config_extension[sn_config] = merge_two_dicts(
                    config_extension_default, lst_config_extension[sn_config]
                )

        # build
        config = {
            "lst_config": lst_config,
            "opt_extension": opt_extension,
            "lst_config_extension": lst_config_extension,
            #
            "opt_allow_sidewalls_merge": False,
        }
        io = Multi_IO(**config)

        return io
