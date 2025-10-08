# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


"""DLD-based sytem | Theme: Multistage"""

import pprint

import numpy as np

from mnflow.mfda.cad.components.element import Element
from mnflow.mfda.cad.dld.theme.block import DLD as block_DLD
from mnflow.mfda.cad.utils.common import merge_two_dicts
from mnflow.mfda.cad.utils.inspections import bbox


class DLD(Element):
    """A DLD system with a multistage theme."""

    # --- list of datatypes not valid for inference of number of stages
    invalid_types_for_num_stage_inference = [list, tuple, np.ndarray, dict]

    # ------------------------------------------------------------------------
    # attributes that can be of type of array/list/dict
    #
    # What are different about them?
    #   - they cannot be used to infer number of stages
    #   - they are assigned to all stages uniformly if available as key in
    # ``config``.
    #   In case you want to apply them heterogeneously to different stages,
    # included them
    #   as key in ``config_stages``.
    # ------------------------------------------------------------------------
    keys_in_config_that_always_applied_homogeneously = [
        "core_shape",
        "dot_offset",
        "array_counts",
        "array_spacing",
        "opt_mirror_before_array",
        "spacing_between_mirrors_before_array",
        "mirror_before_array_around_negative_edge",
        "padding_width",
        "layer_1",
        "layer_2",
        #
        "acc_top_gap_deviation_nondim",
        "dep_top_gap_deviation_nondim",
    ]

    def __init__(
        self,
        # Overall config
        num_stage=None,
        opt_multi_inlet=None,
        opt_filter=None,
        opt_preload=None,
        opt_collection=None,
        opt_collection_with_via=None,
        offset=None,
        # Multi_inlet
        config_multi_inlet=None,
        # Homogeneous configs of stages
        config=None,
        # Heterogeneously configs of stages
        config_stages=None,
        # Internal config
        verbose=None,
        opt_process_upon_init=None,
        opt_write_upon_init=None,
        opt_save_image=None,
        opt_enable_infer_width=None,
        opt_enable_infer_sidewall_width=None,
        top_cell_name=None,
        *args,
        **kwargs,
    ):
        """
        **Constructor**

        Parameters
        ----------

        **Overall config**

        num_stage : int, optional
            Number of stages; it can also be inferred automatically if other
            provided params are sufficient, by default None
        opt_multi_inlet : bool, optional
            Whether to include a multi-inlet upstream of system, can be
            configured to serve as a single-inlet as well, by default None
        opt_filter : bool, optional
            Whether to include a filter in upstream of the overall structure,
            by default None
        opt_preload : bool, optional
            Whether to include a preload in upstream of the overall structure,
            by default None
        opt_collection : bool, optional
            Whether to include a collection component in downstream of the
            overall structure, by default None
        opt_collection_with_via : bool, optional
            Whether the collection component has via, by default None
        offset : list/tuple, optional
            Offset of stage when snapping to upstream neighboring stage, by
            default None

        `Multi_inlet`

        config_multi_inlet : dict, optional
            Config of multi-inlet component, by default None

        **Homogeneous configs of stages**

        config : dict, optional
            Mainly for configurations to be applied to all stages
            homogeneously; yet, list of values is also supported for many
            params (keys of dict) denoting that the param needs to be applied
            to all stages heterogeneously according to order of value in list,
            `e.g.`, ``'d_c':[5, 2]`` would be a valid key-value of dict for a
            two-stage system, wherein the upstreammost stage is supposed to
            have a critical diameter of :math:`5~\\mu m`, appended by a stage
            with critical diameter of :math:`2~\\mu m`, by default None.

            Note:
                - This param is added solely for convenience of user; any\
                configurations for each stage can be passed explicitly using\
                ``config_stages``. The ``config``, however, can make it more\
                convenient to assign a set of similar configs to all stages\
                instead of writing them separately for each stage.
                - Homogeneous assignment of a param to stage(s) is done only\
                when the param is NOT available in corresponding stage(s) of\
                ``config_stages``.

        **Heterogeneously configs of stages**

        config_stages : list, optional
            List of dict, wherein each dict contains configs of one stage, by
            default None

        **Internal config**

        verbose : bool, optional
            verbose, by default None
        opt_process_upon_init : bool, optional
            Whether to invoke the ``process`` method from inside the
            constructor to design the system, by default True
        opt_write_upon_init : bool, optional
            Whether to invoke the ``write`` method from inside the constructor
            to write the GDS/DXF layout file, by default None
        opt_save_image : bool, optional
            Whether to invoke the ``save_image`` method from inside the
            constructor to save layout as png file(s), by default None
        opt_enable_infer_width : bool, optional
            Whether to enable automatic inference of stages widths, enables
            inference when ``Nw`` and ``width`` are not provided for a stage.
            by default None
        opt_enable_infer_sidewall_width : bool, optional
            Whether to enable automatic inference of stages sidewall widths,
            enables inference when ``sidewall_width`` is not provided for a
            stage, by default None
        top_cell_name : str
            Name of top cell to be created as needed.
        """

        # --- Constructors
        lst_param_Element = Element.__init__.__code__.co_varnames

        # --- Parent: Element
        _kwargs_Element = {}
        for key in lst_param_Element:
            if key in kwargs:
                _kwargs_Element[key] = kwargs.pop(key)
        Element.__init__(self, *args, **_kwargs_Element)

        # --- sanity check
        if len(kwargs) > 0:
            raise ValueError(f"Invalid parameter(s): {[key for key in kwargs]}")
        #####################

        # --- default params
        if opt_multi_inlet is None:
            opt_multi_inlet = False
        if opt_filter is None:
            opt_filter = False
        if opt_preload is None:
            opt_preload = False
        if opt_collection is None:
            opt_collection = False
        if opt_collection_with_via is None:
            opt_collection_with_via = False
        if verbose is None:
            verbose = True
        if opt_process_upon_init is None:
            opt_process_upon_init = True
        if opt_write_upon_init is None:
            opt_write_upon_init = True
        if opt_save_image is None:
            opt_save_image = False
        if opt_enable_infer_width is None:
            opt_enable_infer_width = True
        if opt_enable_infer_sidewall_width is None:
            opt_enable_infer_sidewall_width = True
        if top_cell_name is None:
            top_cell_name = "Multistage"

        # --------------------------------------------------------------------
        # default configs
        # --------------------------------------------------------------------
        config_default = {
            "boundary_treatment": [None, "pow_2", "pow_3", "pow", "3d"][2],
            "opt_save_image": False,
            "opt_write_upon_init": False,
            "turn_off_constraints": True,
            "dep_sidewall_theme": 1,
            "verbose": verbose,
            "top_cell_name": "Block",
        }

        # --- merge passed homogen configs into default ones
        config = merge_two_dicts(config_default, config)

        # --- self attributes
        lst_param_to_set = DLD.__init__.__code__.co_varnames[
            1 : DLD.__init__.__code__.co_argcount
        ]
        lcl = locals()
        for _sn_key, key in enumerate(lst_param_to_set):
            setattr(self, key, lcl[key])

        # --- prep config
        DLD._prep_config(self)

        # --- Process
        if opt_process_upon_init:
            DLD.process(
                self,
                opt_write_upon_init=opt_write_upon_init,
                opt_save_image=opt_save_image,
            )

            # --- verbose
            if self.verbose:
                print("-" * 40)
                print(self)
                print("-" * 40)
                info_dic = DLD.get_die_info(
                    self,
                )
                pprint.pprint(info_dic)

    def get_die_info(self):
        """Returning the die information."""

        # parent class
        out_dict = super().get_die_info()
        area = out_dict["area"] * 1.0e-12
        area_mmsq = area * 1.0e6
        out_dict["die area (mm-sq)"] = area_mmsq

        return out_dict

    def _prep_config(
        self,
    ):

        config = self.config
        config_stages = self.config_stages

        # --------------------------------------------------------------------
        # Infer number of stages
        # --------------------------------------------------------------------
        if self.num_stage is None:
            # exclude keys for size inference
            _dict_to_use_to_infer_num_stages = {
                key: value
                for key, value in config.items()
                if key
                not in DLD.keys_in_config_that_always_applied_homogeneously
            }
            self.num_stage = DLD.infer_count_stage(
                *_dict_to_use_to_infer_num_stages.values(),
                config_stages,
            )

        # --- saity check
        if config_stages is not None:
            if len(config_stages) != self.num_stage:
                raise ValueError(
                    f"""Count of stages was inferred to be {self.num_stage},
which is different from length of ``config_stages``: {len(config_stages)}"""
                )
        for key, val in _dict_to_use_to_infer_num_stages.items():
            if type(val) in [
                list,
                tuple,
            ]:
                if len(val) != self.num_stage:
                    raise ValueError(
                        f"""Count of stages was inferred to be
{self.num_stage}, which is different from length of config.{key}: {len(val)}"""
                    )

        # sanity check: overall config params
        if self.offset is not None:
            if np.array(self.offset).ndim != 2:
                raise ValueError(
                    f"""Offset is expected to be a list of lists (ndim of 2),
but its ndim is {np.array(self.offset).ndim}"""
                )
            if len(self.offset) != self.num_stage - 1:
                raise ValueError(
                    f"""Count of stages was inferred to be {self.num_stage}.
Length of offset is expected to be {self.num_stage-1}, which is different from
 given length of offset: {len(self.offset)}"""
                )

        # --------------------------------------------------------------------
        # set config_stages to empty if not given explicitly
        # --------------------------------------------------------------------
        if config_stages is None:
            self.config_stages = [{} for i in range(self.num_stage)]
            config_stages = self.config_stages

        # --------------------------------------------------------------------
        # Prep list of dict of configs to be merged into main
        # ``config_stages`` later
        #
        # Note:
        #   - Only keys not available in ``config_stages`` for a given stage
        # are considered when building ``config_stages_from_config``.
        # Therefore, when merging ``config_stages_from_config`` into
        # ``config_stages``, available key-values in the latter will be
        # preserved.
        # --------------------------------------------------------------------
        config_stages_from_config = [{} for i in range(self.num_stage)]
        self.config_stages_from_config = config_stages_from_config
        for key, val in config.items():

            # Homogeneous assignment
            if (
                type(val) not in DLD.invalid_types_for_num_stage_inference
                or key in DLD.keys_in_config_that_always_applied_homogeneously
            ):
                for sn_stage in range(self.num_stage):
                    if key not in config_stages[sn_stage]:
                        config_stages_from_config[sn_stage][key] = val

            # Heterogeneous assignment
            elif type(val) in DLD.invalid_types_for_num_stage_inference:
                for sn_stage, item in enumerate(val):
                    if key not in config_stages[sn_stage]:
                        config_stages_from_config[sn_stage][key] = item

            else:
                raise TypeError(f"Invalid type of config.{key}: {type(val)}")

        # --------------------------------------------------------------------
        # Infer width (only for stages that ``width`` and ``Nw`` are not
        # provided)
        # --------------------------------------------------------------------
        if self.opt_enable_infer_width:
            DLD.infer_width(
                config_stages,
                config_stages_from_config,
            )

        # --------------------------------------------------------------------
        # Infer sidewall width (only for stages that ``sidewall_width` is not
        # provided)
        # --------------------------------------------------------------------
        if self.opt_enable_infer_sidewall_width:
            DLD.infer_sidewall_width(
                config_stages,
                config_stages_from_config,
            )

        # --- up-/downstream- config
        if self.opt_preload:
            config_stages_from_config[0]["opt_preload"] = True
        if self.opt_filter:
            config_stages_from_config[0]["opt_filter"] = True
        if self.opt_multi_inlet:
            config_stages_from_config[0]["opt_multi_inlet"] = True
            config_stages_from_config[0][
                "config_multi_inlet"
            ] = self.config_multi_inlet
        if self.opt_collection:
            config_stages_from_config[-1]["opt_collection"] = True
        if self.opt_collection_with_via:
            config_stages_from_config[-1]["opt_collection_with_via"] = True

    def process(self, *args, **kwargs):

        config_stages = self.config_stages
        config_stages_from_config = self.config_stages_from_config

        # --- prep param for each stage
        for sn_stage, stage_config in enumerate(config_stages):

            # get merge
            stage_config, _ = DLD.get_merged_config(
                config_default=stage_config,
                config=config_stages_from_config[sn_stage],
            )

            # internal configs
            if sn_stage == 0 or self.offset is None:
                this_offset = None
            else:
                this_offset = self.offset[sn_stage - 1]

            # add stage
            self.add(
                element=block_DLD(**stage_config),
                snap_direction="bottom",
                offset=this_offset,
                target_cell_name=self.top_cell_name,
            )

        # --- after all logics
        Element.process(
            self,
            *args,
            **kwargs,
        )

        return self.layout

    def __repr__(self):

        msg = "multistage.DLD__stages:"

        for sn_elem, elem in enumerate(self.elements):
            msg += f"\n\n{sn_elem}:\n{elem.__repr__()}"

        return msg

    # ------------------------------------------------------------------------
    # Static methods
    # ------------------------------------------------------------------------

    @staticmethod
    def infer_count_stage(*arg):
        """Infer count of stages from provided arguments. It scans args and
        returns the max length of list/tuple it finds. Otherwise, it returns
        1."""

        size = 1
        for param in arg:
            if type(param) in [
                list,
                tuple,
            ]:
                if len(param) > size:
                    size = len(param)

        return size

    @staticmethod
    def infer_width(
        config_stages,
        config_stages_from_config,
    ):
        """Infer width of stages from provided arguments. It finds the widest
        stage and extract the channel width and sidewall width.

        Note:
            ``config_stages_from_config`` is updated in-place in case
            inference is done.
        """

        # find stage with widest inlet
        sn_stage_widest, width_inlet_max, lst_element, lst_bb = (
            DLD.find_widest_stage_inlet(
                config_stages,
                config_stages_from_config,
            )
        )

        # --- updating list of dicts of config in-place
        num_stage = len(config_stages)
        for sn_stage in range(num_stage):

            # update 'width' in ``config_stages_from_config`` dict only if no
            # specific requirement is avaialable wrt. width of stage
            if not (
                "Nw" in config_stages_from_config[sn_stage]
                or "Nw" in config_stages[sn_stage]
                or "width" in config_stages_from_config[sn_stage]
                or "width" in config_stages[sn_stage]
            ):

                # add inferred width to config
                config_stages_from_config[sn_stage]["width"] = width_inlet_max

    @staticmethod
    def infer_sidewall_width(
        config_stages,
        config_stages_from_config,
    ):
        """Infer sidewall width of stages from provided arguments. It aims at
        adjusting sidewall width of stages so the outermost edge of sidewalls
        line up well.

        Note:
            ``config_stages_from_config`` is updated in-place in case
            inference is done.
        """

        # find stage with widest inlet
        sn_stage_widest, width_inlet_max, lst_element, lst_bb = (
            DLD.find_widest_stage_box(
                config_stages,
                config_stages_from_config,
            )
        )

        # widest stage including sidewall
        width_max_inc_sidewall = (
            lst_bb[sn_stage_widest][1][0] - lst_bb[sn_stage_widest][0][0]
        )

        # --- updating list of dicts of config in-place
        num_stage = len(config_stages)
        for sn_stage in range(num_stage):

            # update 'sidewall_width' in ``config_stages_from_config`` dict
            # only if no specific requirement is avaialable wrt. sidewall
            # width of stage
            if not (
                "sidewall_width" in config_stages_from_config[sn_stage]
                or "sidewall_width" in config_stages[sn_stage]
            ):

                # current width of stage including sidewall
                width_inc_sidewall = (
                    lst_bb[sn_stage][1][0] - lst_bb[sn_stage][0][0]
                )

                # diff wrt. widest stage
                diff_sidewall_width = (
                    width_max_inc_sidewall - width_inc_sidewall
                )
                assert (
                    diff_sidewall_width >= 0
                ), f"""``diff_sidewall_width`` is expected to be non-negative
but is {diff_sidewall_width}"""

                # add inferred sidewall_width to config
                config_stages_from_config[sn_stage]["sidewall_width"] = (
                    lst_element[sn_stage].sidewall_width
                    + diff_sidewall_width / 2.0
                )

    @staticmethod
    def find_widest_stage_inlet(
        config_stages,
        config_stages_from_config,
    ):
        """Finds the stage with widest inlet.

        Note:
            Width of inlet of a given stage: ``Nw*pitch_w``.
        """

        # --- count of stages
        num_stage = len(config_stages)

        sn_stage_widest = None
        width_inlet_max = 0
        lst_element = []
        lst_bb = []
        for sn_stage in range(num_stage):

            stage_config, _ = DLD.get_merged_config(
                config_default=config_stages[sn_stage],
                config=config_stages_from_config[sn_stage],
            )
            stage_config["verbose"] = False

            _element = block_DLD(**stage_config)
            lst_element.append(_element)
            lst_bb.append(bbox(_element.layout))

            this_width = stage_config["Nw"] * stage_config["pitch_w"]
            if this_width >= width_inlet_max:
                width_inlet_max = this_width
                sn_stage_widest = sn_stage

        return sn_stage_widest, width_inlet_max, lst_element, lst_bb

    @staticmethod
    def find_widest_stage_box(
        config_stages,
        config_stages_from_config,
    ):
        """Finds the stage with widest bounding box."""

        # --- count of stages
        num_stage = len(config_stages)

        sn_stage_widest = None
        width_box_max = 0
        lst_element = []
        lst_bb = []
        for sn_stage in range(num_stage):

            stage_config, _ = DLD.get_merged_config(
                config_default=config_stages[sn_stage],
                config=config_stages_from_config[sn_stage],
            )
            stage_config["verbose"] = False

            _element = block_DLD(**stage_config)
            lst_element.append(_element)
            lst_bb.append(bbox(_element.layout))

            # this bounding box: lst_bb[-1]
            this_width = lst_bb[-1][1][0] - lst_bb[-1][0][0]
            if this_width >= width_box_max:
                width_box_max = this_width
                sn_stage_widest = sn_stage

        return sn_stage_widest, width_box_max, lst_element, lst_bb

    @staticmethod
    def get_merged_config(config_default, config):
        """Merges (with override) ``config`` into ``config_default`` and
        returns merged ``config`` and ``config_auto`` containing configs
        determined automatically for core.DLD and block.DLD."""

        # merge dicts
        config = merge_two_dicts(config_default, config)

        # Ref for inspect: https://docs.python.org/3/library/inspect.html
        lst_valid_param = block_DLD.get_geom_config_auto.__code__.co_varnames[
            : block_DLD.get_geom_config_auto.__code__.co_argcount
        ]
        kwargs_to_pass = {key: config.get(key) for key in lst_valid_param}
        config_auto = block_DLD.get_geom_config_auto(**kwargs_to_pass)

        # merge ``config_auto`` into given config
        config = merge_two_dicts(config, config_auto)

        return config, config_auto
