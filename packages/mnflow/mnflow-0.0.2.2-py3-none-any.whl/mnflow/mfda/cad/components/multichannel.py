# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import copy

import numpy as np

from mnflow.mfda.cad.components.element import Element
from mnflow.mfda.cad.components.utils import get_parallel_multichannels
from mnflow.mfda.cad.utils.common import merge_two_dicts

"""
When developing a new Element child class:

    - Each Element child class should:
        - create an empty layout (done by parent class: ``Element``)
        - create components (of type of **db.Cell** or ``Element``) using util
        functions or class methods
        - add components to host element using ``add`` method and appropriate
        param: 'cell_2' if component type is **db.Cell**; 'element' if
        component type is ``Element``)

    - When using already-developed Element classes inside Element classes you
    are developing:
        - do NOT pass 'layout' arg to already-developed Element classes; as
        mentioned above, each element creates an empty layout and lay out
        components on it.
        - use ``add`` method with 'element' param to copy an instance of
        already-developed Element into your element's layout.

    - The drawback is that any changes to an element after it is added to a
    system by ``add`` method will not be reflected properly as the
    corresponding db.Cell has been copied using ``copy_tree`` rather than being
    instantiated using ``db.DCellInstArray`` as the cell_1 and cell_2 are from
    two different layers.

In the case of using util functions outside of element, if you want to insert
resulted objects directly into a layout, refer to the example(s) provided at
the top of ``mnflow.mfda.dld.cad.components.utils``.
"""


class Multichannel(Element):
    """An array of parallel channels between two sidewalls"""

    def __init__(
        self,
        # Channels
        bar_dims,
        grating_pitch,
        grating_area_dim,
        sidewall_width,
        # CAD
        layer=None,
        cell_target_name=None,
        multichannel_cell_name=None,
        unit_grating_cell_name=None,
        # Detailed config
        bar_offset=None,
        grating_area_ll=None,
        margin_top=None,
        block_width=None,
        # Misc.
        top_cell_name=None,
        *args,
        **kwargs,
    ):
        """
        **Constructor**

        Note:
            - Cell decorator params, _e.g._, 'rot', 'scale', 'clip_dim', etc.,
            can be included in ``kwargs``.

        Parameters
        ----------

        **Channels**
        bar_dims : list or tuple
            Dimensions of rectangular (2 components) or trapezoidal
            (3 components) bar if provided. None for the case of explicitly
            passing an item to be arrayed.
        grating_pitch : float
            Pitch of array.
        grating_area_dim : float
            Dimension of area confined between sidewalls to be covered.
        sidewall_width : float, list, tuple
            Sidewalls width; in the case of a scalar, both sidewalls will have
            a same width; in the case of a list/tuple of two components, the
            first referst to left wall, and the second item to the right.

        **CAD**
        layer : int
            Layer of interest, by default None
        cell_target_name : str
            Name of target cell if ``cell_target`` is not given.
        multichannel_cell_name : str
            Name of multichannel cell
        unit_grating_cell_name : str
            Name of unit of grating cell

        **Detailed config**
        bar_offset : list or tuple
            Offset of bar in each direction, by default None
        grating_area_ll : tuple or list
            Lower left coordinates of grating area (lower right corner of left
            sidewall), by default None
        margin_top : float
            Margin on top of grating area between sidewalls, by default None
        block_width : list or tuple
            Distance from left (first component) and right (second component)
            sidewalls to be blocked, by default None

        **Misc.**
        top_cell_name : str
            Name of top cell to be created as needed.
        """

        # --- default config
        if top_cell_name is None:
            top_cell_name = "Multichannel"

        # --- Parent
        lst_param_Element = Element.__init__.__code__.co_varnames
        _kwargs_Element = {}
        for key in lst_param_Element:
            if key in kwargs:
                _kwargs_Element[key] = kwargs.pop(key)
        Element.__init__(self, *args, **_kwargs_Element)

        # --- self attributes
        lst_param_to_set = Multichannel.__init__.__code__.co_varnames[
            1 : Multichannel.__init__.__code__.co_argcount
        ]
        lcl = locals()
        for _sn_key, key in enumerate(lst_param_to_set):
            setattr(self, key, lcl[key])

        # --- process
        self.process(
            *args,
            **kwargs,
        )

    def process(
        self,
        *args,
        **kwargs,
    ):

        # build
        io_cell, _ = get_parallel_multichannels(
            bar_dims=self.bar_dims,
            grating_pitch=self.grating_pitch,
            grating_area_dim=self.grating_area_dim,
            sidewall_width=self.sidewall_width,
            # CAD
            layer=self.layer,
            cell_target_name=self.cell_target_name,
            multichannel_cell_name=self.multichannel_cell_name,
            unit_grating_cell_name=self.unit_grating_cell_name,
            # Misc.
            bar_offset=self.bar_offset,
            grating_area_ll=self.grating_area_ll,
            margin_top=self.margin_top,
            block_width=self.block_width,
            *args,
            **kwargs,
        )

        self.add(cell_2=io_cell, target_cell_name=self.top_cell_name)

        # --- after all logics
        Element.process(
            self,
        )


class Multi_IO(Element):
    """Multi-branch IO/Outlet."""

    def __init__(
        self,
        # Components
        lst_config,
        num_branch=None,
        # options
        opt_extension=None,
        lst_config_extension=None,
        # Misc.
        top_cell_name=None,
        opt_allow_sidewalls_merge=None,
        #
        *args,
        **kwargs,
    ):
        """
        **Constructor**

        Parameters
        ----------
        lst_config : dict, list
            A dict, or a list of dict, wherein each dict contains config of a
            single inlet/outlet branch; order of branches in the list is from
            left to rigth.
        num_branch : int, optional
            Number of branches in case a single dict of config is provided to
            be applied to all branches, by default None
        opt_extension : bool, optional
            Whether to include a vertical extension downstream of each branch,
            by default None
        lst_config_extension : dict, list, optional
            Config of extension component for one or multiple branches, by
            default None
        top_cell_name : str, optional
            Name of top cell, by default None
        opt_allow_sidewalls_merge : bool, optional
            Whether to apply a slight offset to a branch to merge its sidewall
            to that of its neighbor, which avoid creation of sharp corners at
            interface of branches without extension, by default None
        """

        # --- default params
        if opt_extension is None:
            opt_extension = False
        if top_cell_name is None:
            top_cell_name = "Multi_IO"
        if opt_allow_sidewalls_merge is None:
            opt_allow_sidewalls_merge = True

        # --- validity of params
        if type(lst_config) in [list, tuple]:
            if num_branch is not None and num_branch != len(lst_config):
                raise ValueError(
                    f"Inconsistent arguments; ``num_branch`` is {num_branch}\n\
                    while ``lst_config`` has {len(lst_config)} components."
                )
            num_branch = len(lst_config)
        elif num_branch is None:
            if type(lst_config) is dict:
                num_branch = 1
                lst_config = [lst_config]
            else:
                raise TypeError(
                    f"A list/tuple of dict is expected for ``lst_config``\n\
                    when ``num_branch`` is not provided. The provided\n\
                    datatype, however, is: {type(lst_config)}. If you want to\n\
                    use the same config for different branches (more than 1),\n\
                    explicitly provide its value using ``num_branch``."
                )
        elif type(lst_config) is not dict:
            raise TypeError(
                f"A dict is expected for ``lst_config`` when ``num_branch``\n\
                is provided. The provided datatype, however, is:\n\
                {type(lst_config)}."
            )
        # case of an integer for ``num_branch`` and a dict for``lst_config``
        else:
            _config = copy.deepcopy(lst_config)
            lst_config = [copy.deepcopy(_config) for sn in range(num_branch)]

        # set lst_config_extension
        if lst_config_extension is None:
            lst_config_extension = [{} for _ in range(num_branch)]
        elif type(lst_config_extension) is dict:
            _lst_config_extension = copy.deepcopy(lst_config_extension)
            lst_config_extension = [
                copy.deepcopy(_lst_config_extension) for _ in range(num_branch)
            ]
        elif type(lst_config_extension) not in [list, tuple]:
            raise TypeError(
                f"A (list of) dict is expected for ``lst_config_extension``,\n\
                while received a {type(lst_config_extension)}."
            )

        # --- Parent: Element
        lst_param_Element = Element.__init__.__code__.co_varnames
        _kwargs_Element = {}
        for key in lst_param_Element:
            if key in kwargs:
                _kwargs_Element[key] = kwargs.pop(key)
        Element.__init__(self, *args, **_kwargs_Element)

        # --- sanity check
        if len(kwargs) > 0:
            raise ValueError(
                f"Invalid parameter(s):\n\
                {[key for key in kwargs]}"
            )

        # --- self attr
        lst_param_to_set = Multi_IO.__init__.__code__.co_varnames[
            1 : Multi_IO.__init__.__code__.co_argcount
        ]
        lcl = locals()
        for _sn_key, key in enumerate(lst_param_to_set):
            setattr(self, key, lcl[key])

        # --------------------------------------------------------------------
        # 'bar_dims' of config is modified to enforce the desired value after
        # rotation and clip.
        # Therefore, keep a copy of orig config to be used later when calc
        # required offset for assembly.
        # --------------------------------------------------------------------
        self.lst_config_orig = copy.deepcopy(lst_config)

        # --- config IOs
        Multi_IO.config_IO(lst_config)

        # --- process
        self.process()

    def process(
        self,
    ):
        # --- vars from mutable self attr
        lst_config = self.lst_config
        lst_config_orig = self.lst_config_orig
        lst_config_extension = self.lst_config_extension

        # --- build IOs
        lst_element = []
        for sn_config, config in enumerate(lst_config):
            elem = Multichannel(**config)
            lst_element.append(elem)

        # --- assembly of IOs
        for sn_elem, elem in enumerate(lst_element):
            this_offset = [0, 0]

            # find object on my left if any
            if sn_elem > 0:

                # adjust offset to avoid creation of sharp corner at interface
                # between me and object on my left
                if self.opt_allow_sidewalls_merge:
                    this_offset = [
                        max(
                            -lst_config[sn_elem]["sidewall_width"][0]
                            / np.cos(lst_config[sn_elem]["rot"] * np.pi / 180),
                            -lst_config[sn_elem - 1]["sidewall_width"][1]
                            / np.cos(
                                lst_config[sn_elem - 1]["rot"] * np.pi / 180
                            ),
                        ),
                        0,
                    ]

                # if my rot is positive (ccw), adjust offset to snap to object
                # on my left
                if lst_config[sn_elem]["rot"] > 0:
                    this_offset[0] -= lst_config_orig[sn_elem]["bar_dims"][
                        1
                    ] * np.sin(lst_config[sn_elem]["rot"] * np.pi / 180)

                # if rot of object on my left is negative (cw), adjust offset
                # to snap to object on my left
                if lst_config[sn_elem - 1]["rot"] < 0:
                    _len_bar = lst_config_orig[sn_elem - 1]["bar_dims"][1]
                    _factor = float(
                        np.sin(lst_config[sn_elem - 1]["rot"] * np.pi / 180)
                    )
                    this_offset[0] -= abs(_len_bar * _factor)

            # --- extension
            if self.opt_extension:
                # pop any extra keys of config_extension that should not be
                # passed to downstream functions, e.g., Multichannel
                # constructor ...
                bar_len = lst_config_extension[sn_elem].pop("bar_len", 100)
                margin_top = lst_config_extension[sn_elem].pop(
                    "margin_top", 0.0
                )
                margin_down = lst_config_extension[sn_elem].pop(
                    "margin_down", 0.0
                )

                # --- to be consistent with upstream elem
                # remove any potential clip params
                config = lst_config[sn_elem]
                config.pop("clip_dim", None)
                config.pop("clip_nondim", None)
                config.pop("cell_clip_layer", None)
                # set snap direction
                this_snap_direction = (
                    "lower right 3" if config["rot"] >= 0 else "lower left 4"
                )
                # set config_extension
                sidewall_width = [
                    config["sidewall_width"][0]
                    / np.cos(config["rot"] * np.pi / 180),
                    config["sidewall_width"][1]
                    / np.cos(config["rot"] * np.pi / 180),
                ]
                grating_area_dim = config["grating_area_dim"] / np.cos(
                    config["rot"] * np.pi / 180
                )
                grating_pitch = config["grating_pitch"] / np.cos(
                    config["rot"] * np.pi / 180
                )
                bar_offset = config.pop("bar_offset", [0, 0])
                bar_offset[0] /= np.cos(config["rot"] * np.pi / 180)
                # bars of extension are not allowed to move vertically.
                # Use ``margin_down`` and ``margin_top`` instead
                bar_offset[1] = margin_down
                config_extension_default = {
                    "rot": 0,
                    "top_cell_name": f"extension_{sn_config}",
                    "sidewall_width": sidewall_width,
                    "grating_area_dim": grating_area_dim,
                    "grating_pitch": grating_pitch,
                    # can be from ``config_extension`` if provided
                    "bar_dims": [
                        config["bar_dims"][0]
                        / np.cos(config["rot"] * np.pi / 180),
                        bar_len,
                    ],
                    "margin_top": margin_top,
                    "bar_offset": bar_offset,
                }
                lst_config_extension[sn_elem] = merge_two_dicts(
                    config_extension_default, lst_config_extension[sn_elem]
                )
                config = merge_two_dicts(config, lst_config_extension[sn_elem])
                extension = Multichannel(**config)
                elem.add(
                    element=extension,
                    snap_direction=this_snap_direction,
                )

            self.add(
                element=elem,
                snap_direction="lower right",
                offset=this_offset,
                target_cell_name=self.top_cell_name,
            )

        # --- after all logics
        Element.process(
            self,
        )

    @staticmethod
    def config_IO(lst_config):
        """
        Note:
            Angles orientation --  positive: ccw
        """

        num_branch = len(lst_config)
        for sn_config, config in enumerate(lst_config):
            # angle
            if "rot" not in config:
                config["rot"] = Multi_IO.infer_rot(sn_config, num_branch)
            # sanity check
            if abs(config["rot"]) > 80:
                raise ValueError(
                    f"Too sharp angle for left component of io; rot:\n\
                    {config['rot']}"
                )
            # clip
            box_width = (
                config["sidewall_width"][0]
                + config["sidewall_width"][1]
                + config["grating_area_dim"]
            )
            delta_y = abs(box_width * np.sin(config["rot"] * np.pi / 180))
            config["clip_dim"] = {"bottom": delta_y, "top": delta_y}
            config["cell_clip_layer"] = 0
            # enforce desired length of channels after rotation and clip
            config["bar_dims"][1] += abs(
                box_width * np.tan(config["rot"] * np.pi / 180)
            )
            # top cell name
            if "top_cell_name" not in config:
                config["top_cell_name"] = f"IO_{sn_config}"

    @staticmethod
    def infer_rot(sn_config, num_branch, max_tot_opening_angle=150):

        tot_opening_angle = {
            2: 90,
            3: 90,
            4: 120,
            5: 120,
            6: 130,
        }

        if num_branch == 1:
            rot = 0
        elif num_branch in tot_opening_angle:
            rot = (1 / 2 - sn_config / (num_branch - 1)) * tot_opening_angle[
                num_branch
            ]
        else:
            rot = (1 / 2 - sn_config / (num_branch - 1)) * max_tot_opening_angle

        return rot
