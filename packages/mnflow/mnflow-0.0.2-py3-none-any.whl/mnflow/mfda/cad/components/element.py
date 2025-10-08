# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import pickle

import klayout.db as db
import numpy as np

from mnflow.mfda.cad.utils.inspections import bbox
from mnflow.mfda.cad.utils.operations import Direction
from mnflow.mfda.cad.utils.operations import snap_cell_to_cell
from mnflow.mfda.cad.utils.shapes import rectangle
from mnflow.mfda.cad.visual.vis_layout import save_all_images


class Element:
    """A CAD element to be used as parent for other CAD elements.

    To be done:
        - Feature: Construct Element from db.Cell
        - In method ``add``, create an element from ``cell_2`` and add to
        ``elements`` attr. In this way, this attr will consistently incude
        all the elements residing an instance of Element. For the self
        element, a deepcopy is probably needed.
    """

    # --- Unpicklable types
    LIST_TYPE_UNPICKLABLE = [
        db.Cell,
        db.Layout,
        db.Region,
    ]

    def __init__(
        self,
        layout=None,
        top_cell_name=None,
        fname_cad=None,
        rot_last=None,
        img_opt_dark_background=None,
        img_color_background=None,
        img_color_layer_1=None,
        img_dpu=None,
        img_core_fname=None,
        allow_large_overlay_image=None,
    ):
        """**Constructor.**

        Parameters
        ----------
        layout : db.Layout
            Layout.
        top_cell_name : str, optional
            The name of top cell of the layout. The default is 'TOP'.
        fname_cad : str, optional
            Filename for the GDS/DXF CAD file, e.g. 'myDLD.gds' or 'dld.dxf',
            by default './mycad.gds'
        rot_last : float, optional
            Rotational angle (deg) to be applied to layout at the end, by
            default None
        img_opt_dark_background : bool, optional
            Whether to use dark background when preparing ayout image file(s),
            by default False
        img_color_background : int, optional
            Hexadecimal color code, by default None
        img_color_layer_1 : int, optional
            Hexadecimal color code, by default None
        img_dpu : int, optional
            `Dot-per-micron` to adjust the resolution of layout image file(s),
            by default 1
        img_core_fname : str, optional
            A core filename without extension to be used for saving layout
            image file(s), by default 'layout'
        allow_large_overlay_image : bool, optional
            Whether or not to allow large overlay image to be prepared, by
            default False
        """

        # --- default params
        if layout is None:
            layout = db.Layout()
            layout.dbu = 1e-3
        if top_cell_name is None:
            top_cell_name = "TOP"
        if fname_cad is None:
            fname_cad = "./mycad.gds"
        if img_opt_dark_background is None:
            img_opt_dark_background = False
        if img_dpu is None:
            img_dpu = 1
        if img_core_fname is None:
            img_core_fname = "layout"
        if allow_large_overlay_image is None:
            allow_large_overlay_image = True

        # --- self attributes
        lst_param_to_set = Element.__init__.__code__.co_varnames[
            1 : Element.__init__.__code__.co_argcount
        ]
        lcl = locals()
        for _sn_key, key in enumerate(lst_param_to_set):
            setattr(self, key, lcl[key])

        # --- config
        self.elements = []
        self.already_processed = False

    def clip(
        self,
        cell=None,
        clip_nondim=None,
        clip_dim=None,
        layer=None,
        opt_clip_child_cells=None,
    ):
        """Clipping a cell.

        Parameters
        ----------
        cell : db.Cell, optional
            Cell to be clipped, first top cell to be used if not provided, by
            default None
        clip_nondim : dict, optional
            Dictionary with one or multiple keys among
            ['top', 'left', 'bottom', 'right'] specifying desired nondim. width
            of clip in each direction, by default None
        clip_dim : dict, optional
            Dictionary with one or multiple keys among
            ['top', 'left', 'bottom', 'right'] specifying desired width of clip
            in each direction, by default None
        layer : int, optional
            Layer on which clipping to be done, by default None
        opt_clip_child_cells : bool, optional
            Whether to recursively apply this method to each child cell
            individaully; if False, this method applies to all shapes for given
            ``cell`` and ``layer``, by default None
        """

        # --- default params
        if layer is None:
            layer = 0
        if opt_clip_child_cells is None:
            opt_clip_child_cells = False

        # --- default config
        if cell is None:
            cell = self.layout.top_cells()[0]

        # --- clip region ----
        if clip_nondim is not None:
            clip_dim = {}
            bb = bbox(cell)
            len_x = bb[1][0] - bb[0][0]
            len_y = bb[1][1] - bb[0][1]

            if "left" in clip_nondim:
                clip_dim["left"] = clip_nondim["left"] * len_x
            if "right" in clip_nondim:
                clip_dim["right"] = clip_nondim["right"] * len_x
            if "bottom" in clip_nondim:
                clip_dim["bottom"] = clip_nondim["bottom"] * len_y
            if "top" in clip_nondim:
                clip_dim["top"] = clip_nondim["top"] * len_y

        if clip_dim is not None:
            bb = np.array(bbox(cell))

            if "left" in clip_dim:
                bb[0][0] += clip_dim["left"]
            if "right" in clip_dim:
                bb[1][0] -= clip_dim["right"]
            if "bottom" in clip_dim:
                bb[0][1] += clip_dim["bottom"]
            if "top" in clip_dim:
                bb[1][1] -= clip_dim["top"]

            clip_box_pol = db.DPolygon(
                [
                    db.DPoint(*bb[0]),
                    db.DPoint(bb[1][0], bb[0][1]),
                    db.DPoint(*bb[1]),
                    db.DPoint(bb[0][0], bb[1][1]),
                ]
            )
            dbu = cell.layout().dbu
            TDBU = db.CplxTrans(dbu).inverted()
            clip_box_reg = db.Region(TDBU * clip_box_pol)

            # top-level child cells
            child_cells_index = [
                this_cell for this_cell in cell.each_child_cell()
            ]
            child_cells_names = [
                cell.layout().cell(this_cell_index).name
                for this_cell_index in child_cells_index
            ]

            # clip child cells individually
            if len(child_cells_index) > 0 and opt_clip_child_cells:
                for cell_index in child_cells_index:
                    cell = self.layout.cell(cell_index)

                    # clip shapes
                    region = db.Region(cell.begin_shapes_rec(layer))
                    region = region & clip_box_reg
                    cell.clear()
                    cell.shapes(layer).insert(region)

                    self.clip(
                        cell=cell,
                        clip_nondim=clip_nondim,
                        clip_dim=clip_dim,
                        layer=layer,
                        opt_clip_child_cells=opt_clip_child_cells,
                    )
            else:
                region = db.Region(cell.begin_shapes_rec(layer))
                region = region & clip_box_reg
                cell.clear()
                top_child_cell = cell.layout().create_cell(
                    f"Clipped_{cell.name}"
                )
                cell.insert(db.DCellInstArray(top_child_cell, db.DTrans()))
                top_child_cell.shapes(layer).insert(region)
                self.prune(child_cells_names)

    def transform(self, t):
        """A generic transformation."""
        self.layout.top_cell().transform(t)

    def mirror_x(
        self,
    ):
        """Mirror layout around x axis."""

        bb = bbox(self.layout.top_cell())
        del_y = bb[1][1] - bb[0][1] + 2.0 * bb[0][1]
        t1 = db.DCplxTrans(1, 0, True, 0, del_y)
        self.layout.top_cell().transform(t1)

    def mirror_y(
        self,
    ):
        """Mirror layout around y axis."""

        bb = bbox(self.layout.top_cell())
        del_x = bb[1][0] - bb[0][0] + 2.0 * bb[0][0]
        t1 = db.DTrans(db.DTrans.M90, del_x, 0)
        self.layout.top_cell().transform(t1)

    def rotate(self, angle_deg):
        """Rotate layout

        Parameters
        ----------
        angle : float
            Angle of rotation (deg.).
        """

        t1 = db.DCplxTrans(1, angle_deg, False, 0, 0)
        self.layout.top_cell().transform(t1)

    def prune(self, cell_name=None, cell_index=None, cell=None):
        """Prune cells.

        Parameters
        ----------
        cell_name : str, list, tuple, optional
            Cell name or a list of cells names, by default None
        cell_index : int, list, tuple, optional
            Cell index or a list of it, by default None
        cell : db.Cell, optional
            Cell or a list of it, by default None
        """

        # --- to support one and multiple cells
        if cell_name is not None and type(cell_name) not in [list, tuple]:
            cell_name = [cell_name]

        if cell_index is not None and type(cell_index) not in [list, tuple]:
            cell_index = [cell_index]

        if cell is not None and type(cell) not in [list, tuple]:
            cell = [cell]

        # --- prune
        if cell_name is not None:
            for this_cell_name in cell_name:
                self.layout.prune_cell(
                    self.layout.cell_by_name(this_cell_name), -1
                )

        if cell_index is not None:
            for this_cell_index in cell_index:
                self.layout.prune_cell(this_cell_index, -1)

        if cell is not None:
            for this_cell in cell:
                self.layout.prune_cell(this_cell.cell_index(), -1)

    def set_ll(self, target_ll=None):
        """Setting the lower left coordinates of system."""

        if target_ll is not None:
            bb = bbox(self.layout.top_cell())
            t1 = db.DTrans(
                db.DVector(target_ll[0] - bb[0][0], target_ll[1] - bb[0][1])
            )

            # placing the die on the target lower left coordinates
            self.layout.top_cell().transform(t1)
        else:
            print(
                "No change is applied in `set_ll` method as `target_ll` is\n\
                None."
            )

    def report(self, fname):
        """Prepare a report file from dictionary of attributes."""

        with open(fname, "w") as fout:
            for attr in self.__dict__.keys():
                if type(getattr(self, attr)) in Element.LIST_TYPE_UNPICKLABLE:
                    print(attr, "\t is discarded from the report.")
                    pass
                else:
                    fout.write(f"{attr}\t{getattr(self, attr)}\n")

    def write(self, fname=None):
        """Write the layout file in gds/dxf format."""

        if fname is None:
            fname = self.fname_cad

        self.layout.write(fname)

    def get_die_info(self):
        """Returning the die information:
        bbox, lx, ly, area
        """

        lst_top_cells = self.layout.top_cells()
        out_dict = {"count of top cells": len(lst_top_cells)}

        if len(lst_top_cells) > 0:
            bb = bbox(lst_top_cells[0])
            lx = bb[1][0] - bb[0][0]
            ly = bb[1][1] - bb[0][1]
            area = lx * ly

            out_dict = {
                "bb": bb,
                "lx": lx,
                "ly": ly,
                "area": area,
            }

        return out_dict

    def save(self, fname):
        """Pickle the object."""

        print(
            """
NOTE:
    When saving (pickling) object, some attributes cannot be
    pickled and are set as None including:
    - klayout-related data types, e.g. layout, cell, layer, etc.
    - callback functions
    - other cells or elements added/snapped to the original
    layout/element. This is currently a significant limitation
    as it does not allow proper pickling for derivitive classes.

    More info:
    https://www.klayout.de/forum/discussion/2216/pickle-pya-x-objects

    The klayout-related attributes can be rebuilt using the ``process``
    method after loading the pickled object, but if you have used
    callback functions to add features/polygons/regions to the
    design, they will be missing unless you define the same callback
    functions and assign corresponding attributes to the callback
    functions after loading the pickled object, followed by
    running the ``process`` method at the end.

    An ``already_processed`` flag is set to False when saving object to
    signal the requirement of invoking ``process`` methon upon loading a
    pickle file.
    """
        )

        for attr in self.__dict__.keys():
            if type(getattr(self, attr)) in Element.LIST_TYPE_UNPICKLABLE:
                setattr(self, attr, None)
                print(attr, "\t is set to None in pickling object.")

        self.already_processed = False
        pickle.dump(self, open(fname, "wb"))

    def load(self, fname):
        """Load and return object from a pickle file.

        Child classes need to have an appropriate ``process`` method.
        """

        obj = pickle.load(open(fname, "rb"))

        if not self.already_processed:
            obj.process()

        return obj

    def add(
        self,
        element=None,
        snap_direction=None,
        p1=None,
        p2=None,
        cell_1=None,
        cell_2=None,
        target_cell=None,
        target_cell_name=None,
        copy_cell_1=None,
        offset=None,
    ):
        """Add/Snap an element or a cell from another layout to a cell
        of layout of this element.

        Parameters
        ----------
        element : Element, optional
            Element to be snapped to ``cell_1``, by default None
        snap_direction : int, or string
            Direction/Orientation of snap
        p1 : tuple, list
            Snap point from cell #1
        p2 : tuple, list
            Snap point from cell #2 to snap on ``p1`` after displacing
            ``cell_2``
        cell_1 : db.Cell, optional
            First cell, by default None, i.e., (first) top cell of current
            element.
        cell_2 : db.Cell, optional
            Cell to be snapped to ``cell_1``, by default None
        target_cell : db.Cell, optional
            Target cell hosting snapped cells, by default None
        target_cell_name : str
            Name of target cell to be created as needed.
        copy_cell_1 : bool, optional
            Whether to copy the first cell inside the `target_cell`, by
            default True
        offset : list, optional
            Offset to be applied after snap, by default None
        """

        # --- default params
        if snap_direction is None:
            snap_direction = "bottom"
        if offset is None:
            offset = [0, 0]
        if copy_cell_1 is None:
            copy_cell_1 = False
        if target_cell_name is None:
            target_cell_name = "Add_TOP"

        # --- vlaidity of params
        if cell_2 is not None and element is not None:
            raise ValueError(
                "Only one of `cell_2` and `element` can be provided."
            )
        if cell_2 is None and element is None:
            raise ValueError(
                "At least one of `cell_2` and `element` needs to be provided."
            )

        # -----------------------------------------------------------------
        # config default
        # -----------------------------------------------------------------

        if cell_2 is None:
            elem_top_cells = element.layout.top_cells()
            if len(elem_top_cells) > 0:
                cell_2 = element.layout.top_cells()[0]
            else:
                cell_2 = self.layout.create_cell("Top2")

        # config cell_1 & self (first element)
        flag_empty_layout = False
        if cell_1 is None:
            top_cells = self.layout.top_cells()
            if len(top_cells) > 0:
                cell_1 = self.layout.top_cells()[0]
            else:
                flag_empty_layout = True

        # config target cell
        if target_cell is None:
            target_cell = cell_1
        # -----------------------------------------------------------------

        if (
            flag_empty_layout
        ):  # layout is empty: create a cell and copy cell_2 into it
            top_cell = self.layout.create_cell(target_cell_name)
            cell_1 = self.layout.create_cell(cell_2.name)
            top_cell.insert(db.DCellInstArray(cell_1, db.DTrans()))
            if target_cell is None:
                target_cell = cell_1
            target_cell.copy_tree(cell_2)

        # layout not empty: snap cell_2 onto cell_1 and copy into target cell
        else:
            snap_cell_to_cell(
                cell_1=cell_1,
                cell_2=cell_2,
                snap_direction=snap_direction,
                target_cell=target_cell,
                copy_cell_1=copy_cell_1,
                offset=offset,
            )

        # --- add element to list of elements
        if element is not None:
            self.elements.append(element)

    def add_pad(
        self,
        width,
        snap_direction,
        layer=0,
    ):
        """Add a pad to layout. Available options for direction of attachment
        is similar to those in ``add`` method."""

        lst_bottom = Direction.lst_bottom
        lst_right = Direction.lst_right
        lst_top = Direction.lst_top
        lst_left = Direction.lst_left

        layout = self.layout
        pad_cell = layout.create_cell("pad")
        rect_cell = layout.create_cell("pad_rect")
        pad_cell.insert(db.DCellInstArray(rect_cell, db.DTrans()))
        bb = bbox(layout)

        length = [None, None]
        if snap_direction in lst_bottom + lst_top:
            length[0] = bb[1][0] - bb[0][0]
        elif snap_direction in lst_left + lst_right:
            length[1] = bb[1][1] - bb[0][1]
        else:
            raise ValueError(
                f"Invalid value for ``snap_direction``: {snap_direction}"
            )

        for ind_dir in range(2):
            if length[ind_dir] is None:
                length[ind_dir] = width

        rect = rectangle(*length, dbu=1e-3)
        rect_cell.shapes(layer).insert(rect)
        self.add(cell_2=pad_cell, snap_direction=snap_direction)
        self.prune(cell=pad_cell)

    def process(self, *args, **kwargs):
        """A method attribute to be overriden in child classes."""

        # --- unpack params
        opt_write_upon_init = kwargs.get("opt_write_upon_init")
        opt_save_image = kwargs.get("opt_save_image")

        # --- after all logics

        # Any potential post process transformations
        if self.rot_last is not None:
            self.rotate(self.rot_last)

        # flag
        self.already_processed = True

        # write
        if opt_write_upon_init:
            self.write()

            # -------------------------
            # Save layout images (png)
            # -------------------------
            if opt_save_image:
                self.save_image()

    def save_image(
        self,
        fname_cad=None,
        img_opt_dark_background=None,
        img_color_layer_1=None,
        img_color_background=None,
        img_dpu=None,
        img_core_fname=None,
        allow_large_overlay_image=None,
    ):
        """Save image (png) files from layout."""

        # --- default config

        if img_opt_dark_background is None:
            img_opt_dark_background = self.img_opt_dark_background

        if img_color_layer_1 is None:
            img_color_layer_1 = self.img_color_layer_1

        if img_color_background is None:
            img_color_background = self.img_color_background

        if img_dpu is None:
            img_dpu = self.img_dpu

        if fname_cad is None:
            fname_cad = self.fname_cad

        if img_core_fname is None:
            img_core_fname = self.img_core_fname

        if allow_large_overlay_image is None:
            allow_large_overlay_image = self.allow_large_overlay_image
        # ---------------------------------------------

        img_color_layer_2 = [0x0000CC, 0x3498DB][1]  # layer 2: vias
        if img_opt_dark_background:
            if img_color_layer_1 is None:
                img_color_layer_1 = 0xFFFFFF
            if img_color_background is None:
                img_color_background = 0x000000
            opaque_alpha_level = 250
            opt_mask_low_vals = True
        else:
            if img_color_layer_1 is None:
                img_color_layer_1 = 0x000000
            # For some reason 0xffffff creates a yellowish color instead of
            # white, but '#ffffff' creates a correct white color
            if img_color_background is None:
                img_color_background = "#ffffff"
            opaque_alpha_level = 250
            opt_mask_low_vals = False

        save_all_images(
            img_fname_1=f"{img_core_fname}_layer_1.png",
            img_fname_2=f"{img_core_fname}_layer_2.png",
            img_fname_overlay=f"{img_core_fname}_overlay.png",
            dpu=img_dpu,
            fname_cad=fname_cad,
            opt_show_overlay=True,
            color_layer_1=img_color_layer_1,
            color_layer_2=img_color_layer_2,
            color_background=img_color_background,
            opaque_alpha_level=opaque_alpha_level,
            opt_mask_low_vals=opt_mask_low_vals,
            allow_large_overlay_image=allow_large_overlay_image,
        )
