# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


# To replicate the docstring of the decorated function into the final wrapped
# object
from functools import wraps

import klayout.db as db
import numpy as np

from mnflow.mfda.cad.utils.inspections import bbox

# ----------------------------------------------------------------------------
# decorators
# ----------------------------------------------------------------------------


def transform_region_decorator(
    func,
):
    """
    decorating a function that returns a `region` by transforming the produced
    region based on the passed arguments like:
        `ll` (lower left coordinates after other transformations),
        `rot` (rotation angle),
        `scale` (sacling factor),
        etc.

    Note:
        The naming of kwargs to be checked again later. Those that are poped
        will not be accessible by the region-maker function. If those keys are
        needed by the function, they need to be distinguished by distinct key
        names. One of the keys that may have this issue is `ll`.
    """

    @wraps(func)
    def wrapper(*args_wrapper, **kwargs_wrapper):
        reg_ll = kwargs_wrapper.pop("reg_ll", None)
        rot = kwargs_wrapper.pop("rot", 0)
        scale = kwargs_wrapper.pop("scale", 1)
        mirror_x = kwargs_wrapper.pop("mirror_x", False)
        # target len_x before any clip -- currently not supporting anisotropic
        # scale.
        target_len_x = kwargs_wrapper.pop("target_len_x", None)
        # clip
        clip_nondim = kwargs_wrapper.pop("clip_nondim", None)
        clip_dim = kwargs_wrapper.pop("clip_dim", None)
        verbose = kwargs_wrapper.pop("verbose", False)
        if "dbu" not in kwargs_wrapper:
            raise ValueError(
                """``dbu`` is a required for ``transform_region_decorator``
decorator."""
            )
        dbu = kwargs_wrapper.get("dbu")

        # --- call main function
        reg = func(*args_wrapper, **kwargs_wrapper)

        # --------------------------------------
        # configuring the produced region
        # --------------------------------------

        # --- target len_x (1. override any given value for ``scale``, 2. not
        # supporting anisotropic scaling)
        bb = bbox(reg)
        if target_len_x is not None:
            scale = target_len_x / (bb[1][0] - bb[0][0])

        # --- scale, rotation, and mirror transformations
        t1 = db.ICplxTrans(scale, rot, mirror_x, 0, 0)
        if verbose:
            print("t1: ", t1)
        reg.transform(t1)

        bb = bbox(reg)
        if verbose:
            print("bb1: ", bb)

        # --- clip region ----
        if clip_nondim is not None:
            clip_dim = {}
            bb = bbox(reg)
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
            bb = np.array(bbox(reg))

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
            TDBU = db.CplxTrans(dbu).inverted()
            clip_box_reg = db.Region(TDBU * clip_box_pol)

            reg &= clip_box_reg

        # --- translation to target ll
        trans = [0, 0]
        if reg_ll is not None:
            for ind_dir in range(2):
                trans[ind_dir] = (reg_ll[ind_dir] - bb[0][ind_dir]) / dbu

        t2 = db.ICplxTrans(1, 0, False, *trans)
        if verbose:
            print("t2: ", t2)
        reg.transform(t2)

        # --- verbose
        bb = bbox(reg)
        if verbose:
            print("bb2: ", bb)

        return reg

    return wrapper


def transform_cell_decorator(
    func,
):
    """
    decorating a function that returns a `cell` by transforming the produced
    cell based on the passed arguments like:

        - `ll` (lower left coordinates after other transformations)
        - `rot` (rotation angle)
        - `scale` (sacling factor)
        - etc.

    Note:
        - Those that kwargs that are poped here will not be accessible by the
        cell-maker function. If those keys are needed by the function, they
        need to be distinguished by distinct key names. One of the keys that
        may have this issue is `ll`, so we use `cell_ll` here.
        - The decorator can be applied to functions returning a db.Cell or a
        list/tuple with a db.Cell as first item.
    """

    @wraps(func)
    def wrapper(*args_wrapper, **kwargs_wrapper):
        cell_ll = kwargs_wrapper.pop("cell_ll", None)
        rot = kwargs_wrapper.pop("rot", 0)
        scale = kwargs_wrapper.pop("scale", 1)
        mirror_x = kwargs_wrapper.pop("mirror_x", False)
        cell_reverse_tone = kwargs_wrapper.pop("cell_reverse_tone", False)
        if cell_reverse_tone:
            assert (
                "cell_reverse_tone_cell_layer" in kwargs_wrapper
            ), """``cell_reverse_tone_cell_layer`` is needed when providing
``cell_reverse_tone`` to ``transform_cell_decorator`` decorator"""

            cell_reverse_tone_cell_layer = kwargs_wrapper.pop(
                "cell_reverse_tone_cell_layer"
            )
            cell_reverse_tone_cell_to_prune = kwargs_wrapper.pop(
                "cell_reverse_tone_cell_to_prune", []
            )
            cell_reverse_tone_cell_name_to_prune = kwargs_wrapper.pop(
                "cell_reverse_tone_cell_name_to_prune", []
            )
        verbose = kwargs_wrapper.pop("verbose", False)
        # clip
        clip_nondim = kwargs_wrapper.pop("clip_nondim", None)
        clip_dim = kwargs_wrapper.pop("clip_dim", None)
        if clip_nondim is not None or clip_dim is not None:
            assert (
                "cell_clip_layer" in kwargs_wrapper
            ), """``cell_clip_layer`` is needed when providing ``clip_nondim``
or ``clip_dim`` to ``transform_cell_decorator`` decorator"""

            cell_clip_layer = kwargs_wrapper.pop("cell_clip_layer")

        # --- call main function
        _received = func(*args_wrapper, **kwargs_wrapper)

        # --- extract cell from received object
        if type(_received) is db.Cell:
            cell = _received
        elif type(_received) in [list, tuple]:
            cell = _received[0]
        else:
            raise TypeError(
                f"""``transform_cell_decorator`` seems to have been applied
to a function returning an invalid datatype of {type(_received)}, while it is
expected to be in [db.Cell, list, tuple]."""
            )

        # --- configuring the produced region
        t1 = db.DCplxTrans(scale, rot, mirror_x, 0, 0)
        if verbose:
            print("t1: ", t1)
        cell.transform(t1)

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

            # clip
            region = db.Region(cell.begin_shapes_rec(cell_clip_layer))
            region = region & clip_box_reg
            cell.clear()

            # --- create top-level child cells
            top_child_cell = cell.layout().create_cell(child_cells_names[0])
            cell.insert(db.DCellInstArray(top_child_cell, db.DTrans()))
            top_child_cell.shapes(cell_clip_layer).insert(region)

        # --- reverse tone
        if cell_reverse_tone:
            # import here to avoid circular dependencies
            from mnflow.mfda.cad.utils.operations import reverse_tone

            reverse_tone(
                cell_src=cell,
                layer=cell_reverse_tone_cell_layer,
                cell_target=cell,
                cell_to_prune=cell_reverse_tone_cell_to_prune,
                cell_name_to_prune=cell_reverse_tone_cell_name_to_prune,
                clip_pad=None,  # pad the bounding box clip outward
            )

        # --- setting ll only at the end
        bb = bbox(cell)
        if verbose:
            print("bb1: ", bb)

        trans = [0, 0]
        if cell_ll is not None:
            for ind_dir in range(2):
                trans[ind_dir] = cell_ll[ind_dir] - bb[0][ind_dir]

        t2 = db.DCplxTrans(1, 0, False, *trans)
        if verbose:
            print("t2: ", t2)
        cell.transform(t2)

        # --- verbose
        bb = bbox(cell)
        if verbose:
            print("bb2: ", bb)

        if type(_received) is db.Cell:
            return cell
        elif type(_received) in [list, tuple]:
            return cell, *_received[1:]

    return wrapper


def polygon_to_region_decorator(func):
    """
    decorating a function that returns a `polygon` so that it would
    return a `region` after decoration.
    """

    @wraps(func)
    def decorator_wrapper(*args_wrapper, **kwargs_wrapper):
        try:
            # dbu needs to be removed from kwargs before passing to `func`
            # --> `pop`
            dbu = kwargs_wrapper.pop("dbu")
        except KeyError:
            raise KeyError(
                """`dbu` is a Required Argument for decorator:
`polygon_to_region_decorator`"""
            )

        pol = func(*args_wrapper, **kwargs_wrapper)
        TDBU = db.CplxTrans(dbu).inverted()
        reg = db.Region(TDBU * pol)
        return reg

    return decorator_wrapper
