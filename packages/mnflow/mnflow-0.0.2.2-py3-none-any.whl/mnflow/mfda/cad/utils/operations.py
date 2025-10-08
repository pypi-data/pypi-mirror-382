# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import klayout.db as db
import numpy as np

from mnflow.mfda.cad.utils.decorators import transform_cell_decorator
from mnflow.mfda.cad.utils.inspections import bbox
from mnflow.mfda.cad.utils.inspections import get_cell_by_name

# ----------------------------------------------------------------------------
# operation utils
# ----------------------------------------------------------------------------


@transform_cell_decorator
def generic_array(
    layout,
    cell_src,
    pitch,
    length,
    trans=[0, 0],
    cell_target=None,
    _epsilon_length=1e-6,
):
    """Creates a generic array from `cell_src` to be inserted in `cell_target`.

    Note:
        See example from klayout for more information:
        https://www.klayout.org/klayout-pypi/examples/gratings_hierarchical/

    A common approach to use this function: providing the target cell as an
    argument

    .. highlight:: python
    .. code-block:: python

        ly=db.Layout()
        ly.dbu=1e-3
        l1=ly.layer(0, 1)

        top_cell=ly.create_cell('top')
        cell_src=ly.create_cell('ent')
        cell_src.shapes(l1).insert(circle(10, dbu=ly.dbu))

        generic_array(
            layout=ly,
            cell_src=cell_src,
            cell_target=top_cell,
            pitch=[30, 60],
            length=[200, 200],
            trans=[0,0],
            )


    An example usage of this function with catching the target cell without
    providing it as an argument:

    .. highlight:: python
    .. code-block:: python

        ly=db.Layout()
        ly.dbu=1e-3
        l1=ly.layer(0, 1)

        top_cell=ly.create_cell('top')
        cell_src=ly.create_cell('ent')
        cell_src.shapes(l1).insert(circle(10, dbu=ly.dbu))

        returned_cell=generic_array(
            layout=ly,
            cell_src=cell_src,
            pitch=[30, 60],
            length=[200, 200],
            trans=[0,0],
            )

        top_cell.insert(
            db.DCellInstArray(returned_cell.cell_index(), db.DTrans()))


    Parameters
    ----------
    layout : db.Layout
        Layout of interest.
    cell_src : db.Cell
        Cell to be arrayed.
    pitch : list or tuple
        Pitch of array.
    length : list or tuple
        Length of domain to be filled with array in each direction.
    trans : list or tuple
        Translation to be applied to `cell_src` before arraying. Default:
        [0, 0]
    cell_target : db.Cell or NoneType
        Target cell to host array of `cell_src`. Default: None (a cell is
        created inside the function).
    _epsilon_length : float, optional
        A small non-negative length to be added to to absolute value of
        ``length`` when calculating number of copies. It can resolve the
        problems that may arise when, for example, user calculates a length
        according to ``pitch``, e.g., ``5*pitch``, but the resulted value can
        be slightly smaller than what user really wants due to truncation
        error of data types.

    Returns
    -------
    db.Cell
        Target cell.
    """
    if cell_target is None:
        print(
            """
            Note:
                cell_target is not passed.
                A new cell is created and returned.
                Make sure you catch it!
            """
        )
        cell_target = layout.create_cell("GRATING")

    # ensure pitch and length have similar directions
    pitch = list(pitch)
    for dir in range(2):
        pitch[dir] = abs(pitch[dir])
        if length[dir] < 0:
            pitch[dir] *= -1
            # slightly enlarge the length to deal with potential inaccuracies
            # due to truncation error
            length[dir] -= _epsilon_length
        else:
            length[dir] += _epsilon_length

    # form displacement vectors and calc number of instances
    dx = db.DVector(pitch[0], 0)
    num_x = int(np.abs(np.floor(length[0] / pitch[0])))

    dy = db.DVector(0, pitch[1])
    num_y = int(np.abs(np.floor(length[1] / pitch[1])))

    # insert array if applicable
    if num_x > 0 and num_y > 0:
        cell_target.insert(
            db.DCellInstArray(
                cell_src.cell_index(),
                db.DTrans(db.DVector(*trans)),
                dx,
                dy,
                num_x,
                num_y,
            )
        )
    else:
        raise ValueError("generic array fails.")

    return cell_target


def reverse_tone(
    cell_src,
    layer,
    cell_target=None,
    cell_to_prune=[],
    cell_name_to_prune=[],
    clip_pad=None,
    cutout=None,
    verbose=False,
):
    """Reverses the tone of given cell(s) of layout.

    Parameters
    ----------
    cell_src : db.Cell, list, or tuple
        (list of) Source cell(s) the tone of which to be reversed.
    layer : int
        Layer of interest
    cell_target : list, or NonType, optional
        List of target cells.
    cell_to_prune : list or tuple, optional
        List of cells to be pruned, by default []
    cell_name_to_prune : list or tuple, optional
        List of names of cells to be pruned, by default []
    clip_pad : list, tuple, or NoneType, optional
        Dimensions of outward padding area around the bounding box of
        `cell_src`.
    cutout : list, tuple, or NoneType, optional
        Bounding box of area to be cut out; Dimensions are wrt. center of
        bbox of `cell_src`: [(dx_left, dy_bottom), (dx_right, dy_up)], by
        default None
    verbose : bool
        verbose, by default False

    Returns
    -------
    list
        List of target cells.
    """

    # ensure `cell_src` is a list or tuple
    if type(cell_src) not in [list, tuple]:
        cell_src = [cell_src]

    # config `cell_target` as needed
    if cell_target is None:
        print(
            """
              Note:
                  cell_target is not passed.
                  A new cell is created and returned.
                  Make sure you catch it!
              """
        )
        cell_target = []
        for sn, this_cell_src in enumerate(cell_src):
            cell_target.append(this_cell_src.layout().create_cell("REV"))

    elif type(cell_target) not in [list, tuple]:
        cell_target = [cell_target]

    # supporting multilayer operation -- NOT tested comprehensively yet.
    if type(layer) not in [tuple, list]:
        layer = [layer]

    for sn, this_cell_src in enumerate(cell_src):

        # Currently, clip box is defined based on the bounding box of whole
        # cell, independent of the constituent layers. This piece can be moved
        # to inside the following loop to define clip based on the bbox
        # related to each layer as needed.
        bb = bbox(this_cell_src)
        TDBU = db.CplxTrans(this_cell_src.layout().dbu).inverted()
        if clip_pad is None:
            clip = db.Region(TDBU * db.DBox(*bb[0], *bb[1]))
        else:
            clip = db.Region(
                TDBU
                * db.DBox(
                    bb[0][0] - clip_pad[0][0],
                    bb[0][1] - clip_pad[0][1],
                    bb[1][0] + clip_pad[1][0],
                    bb[1][1] + clip_pad[1][1],
                )
            )

        # currently, it is assumed that target and source cell lists are the
        # same, which should work for most practical applications.
        # As such, only layers that need to reverse are processed, and
        # the rest are not altered. In a general case that target cells may
        # not be the same as source cells, the unaltered cells need to be
        # copied to the target cells.
        for sn_layer in range(this_cell_src.layout().layers()):
            if sn_layer in layer:
                cell_target[sn].clear(sn_layer)

                region = db.Region(this_cell_src.begin_shapes_rec(sn_layer))
                region.merge()

                reg_to_be_inserted = clip - region
                if cutout is not None:
                    if cutout[sn_layer] is not None:
                        for this_cutout in cutout[sn_layer]:
                            reg_cutout = db.Region(
                                TDBU
                                * db.DBox(
                                    (bb[0][0] + bb[1][0]) / 2
                                    + this_cutout[0][0],
                                    (bb[0][1] + bb[1][1]) / 2
                                    + this_cutout[0][1],
                                    (bb[0][0] + bb[1][0]) / 2
                                    + this_cutout[1][0],
                                    (bb[0][1] + bb[1][1]) / 2
                                    + this_cutout[1][1],
                                )
                            )
                            reg_to_be_inserted -= reg_cutout
                cell_target[sn].shapes(sn_layer).insert(reg_to_be_inserted)

    for cell in cell_to_prune:
        cell.layout().prune_cell(cell.cell_index(), -1)

    for cell_name in cell_name_to_prune:
        if verbose:
            print("layout from cell_src[0] is considered for prunning cells.")
        try:
            lst_cell = get_cell_by_name(
                layout=cell_src[0].layout(),
                cell_name=cell_name,
            )
            for cell in lst_cell:
                cell_src[0].layout().prune_cell(cell.cell_index(), -1)
        except Exception as e:
            print(e)

    return cell_target


def mirror_layout(
    layout,
    mirror_dir=[False, False],
    # if None, translation will be applied so that the bbox remains the same.
    # Specify trans=[0,0] if no trans needed.
    trans=None,
):
    """Mirror layout around x and/or y directions.

    Parameters
    ----------
    layout : db.Layout
        Layout of interest.
    mirror_dir : list, or tuple, optional
        Whether mirror around axis in this direction, by default
        [False, False]
    trans : list, tuple, or NoneType, optional
        Translation to be applied before mirroring; trans is applied only
        along the line normal to mirror axis; if None, translation will be
        applied so that the bbox remains the same. Specify trans=[0,0] if no
        trans is needed., by default None
    """

    bb = bbox(layout.top_cell())
    if trans is None:
        del_x = bb[1][0] - bb[0][0] + 2.0 * bb[0][0]
        del_y = bb[1][1] - bb[0][1] + 2.0 * bb[0][1]
        trans = (del_x, del_y)
    if mirror_dir[0]:
        t1 = db.DTrans(db.DTrans.M0, db.DVector(0, trans[1]))
        layout.top_cell().transform(t1)
    if mirror_dir[1]:
        t1 = db.DTrans(db.DTrans.M90, db.DVector(trans[0], 0))
        layout.top_cell().transform(t1)


# ----------------------------------------------------------------------------
# assembly operation utils
# ----------------------------------------------------------------------------


class Direction:
    """Valid identifiers to denote specific snap points/orientations. To be
    used for snap of cells/elements.

    Note:
        Some directions are valid in the context of having two bounding
        boxes. For example:

        'upper right 4': 2nd bbox being placed into 4th quadrant of coord
        system with origin on upper right of first bbox
    """

    # --- Single bbox
    # Main four directions
    lst_bottom = [0, "0", "bottom", "low", "down", "south"]
    lst_right = [1, "1", "right", "east"]
    lst_top = [2, "2", "top", "up", "north"]
    lst_left = [3, "3", "left", "west"]
    # Corners
    lst_lower_right = [4, "4", "lower right", "south east"]  # q1
    lst_upper_right = [5, "5", "upper right", "north east"]  # q4
    lst_upper_left = [6, "6", "upper left", "north west"]  # q3
    lst_lower_left = [7, "7", "lower left", "south west"]  # q2
    # --- Two bbox
    # 1nd quad
    lst_lower_right_1 = [10, "10", "lower right 1", "south east 1"]
    lst_upper_right_1 = [11, "11", "upper right 1", "north east 1"]
    lst_upper_left_1 = [12, "12", "upper left 1", "north west 1"]
    lst_lower_left_1 = [13, "13", "lower left 1", "south west 1"]
    # 2nd quad
    lst_lower_right_2 = [20, "20", "lower right 2", "south east 2"]
    lst_upper_right_2 = [21, "21", "upper right 2", "north east 2"]
    lst_upper_left_2 = [22, "22", "upper left 2", "north west 2"]
    lst_lower_left_2 = [23, "23", "lower left 2", "south west 2"]
    # 3rd quad
    lst_lower_right_3 = [30, "30", "lower right 3", "south east 3"]
    lst_upper_right_3 = [31, "31", "upper right 3", "north east 3"]
    lst_upper_left_3 = [32, "32", "upper left 3", "north west 3"]
    lst_lower_left_3 = [33, "33", "lower left 3", "south west 3"]
    # 4th quad
    lst_lower_right_4 = [40, "40", "lower right 4", "south east 4"]
    lst_upper_right_4 = [41, "41", "upper right 4", "north east 4"]
    lst_upper_left_4 = [42, "42", "upper left 4", "north west 4"]
    lst_lower_left_4 = [43, "43", "lower left 4", "south west 4"]

    def __init__(
        self,
    ):
        pass


@transform_cell_decorator
def snap_cell_to_cell(
    cell_1,
    cell_2,
    snap_direction=None,
    p1=None,
    p2=None,
    target_cell=None,
    copy_cell_1=False,
    offset=None,
):
    """
    Snaps two cells to each other:
        - ``cell_2`` is transformed according to the configurations provided\
        by ``snap_direction`` or both ``p1`` and ``p2`` together with other\
        pertinent params so that ref point of ``cell_2`` snaps to that of\
        ``cell_1``.
        - ``cell_2`` is copied into ``target_cell``.
        - ``cell_1`` can be copied into ``target_cell`` if ``copy_cell_1`` is\
        True.
        - ``target_cell`` is returned at the end.

    Note:
        For full valid options of ``snap_direction`` see
        ``mnflow.mfda.dld.cad.utils.operations.Direction``

    Parameters
    ----------
    cell_1 : db.Cell
        First cell
    cell_2 : db.Cell
        Second cell
    snap_direction : int, or string
        Direction/Orientation of snapping.
    p1 : tuple, list
        Snap point from cell #1
    p2 : tuple, list
        Snap point from cell #2 to snap on ``p1`` after displacing ``cell_2``
    target_cell : db.Cell, optional
        Target cell, by default None
    copy_cell_1 : bool, optional
        Whether to copy the first cell inside the `target_cell`, by default
        False
    offset : list, optional
        Offset to be applied after snap, by default None

    Returns
    -------
    db.Cell
        Target cell.
    """

    # --- config default params
    if offset is None:
        offset = [0, 0]

    # --- validity of params
    if snap_direction is not None and (p1 is not None or p2 is not None):
        raise ValueError(
            f"""Providing ``snap_direction`` with any of ``p1`` and ``p2`` is
not allowed. Currently, ``snap_direction``: {snap_direction}, ``p1``:{p1}, and
``p2``:{p2}"""
        )

    if snap_direction is None and (p1 is None or p2 is None):
        raise ValueError(
            f"""Either ``snap_direction`` or  both ``p1`` and ``p2`` must be
provided. Currently, ``snap_direction``: {snap_direction}, ``p1``:{p1}, and
``p2``:{p2}"""
        )

    # --- default config
    if target_cell is None:
        target_cell = cell_1
    if copy_cell_1 and cell_1 != target_cell:
        target_cell.copy_tree(cell_1)

    # bbox of cells
    bb1 = bbox(cell_1)
    bb2 = bbox(cell_2)

    # -----------------------------------------------------
    # Various snap directions/orientations
    # -----------------------------------------------------

    # main four directions
    if snap_direction in Direction.lst_bottom:
        p1 = get_point_from_bbox(bb1, Direction.lst_bottom[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_top[0])

    elif snap_direction in Direction.lst_right:
        p1 = get_point_from_bbox(bb1, Direction.lst_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_left[0])

    elif snap_direction in Direction.lst_top:
        p1 = get_point_from_bbox(bb1, Direction.lst_top[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_bottom[0])

    elif snap_direction in Direction.lst_left:
        p1 = get_point_from_bbox(bb1, Direction.lst_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_right[0])

    # backward compatibility
    elif snap_direction in Direction.lst_lower_right:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_left[0])

    elif snap_direction in Direction.lst_upper_right:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_left[0])

    elif snap_direction in Direction.lst_upper_left:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_right[0])

    elif snap_direction in Direction.lst_lower_left:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_right[0])

    # quad 1
    elif snap_direction in Direction.lst_lower_right_1:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_left[0])

    elif snap_direction in Direction.lst_upper_right_1:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_left[0])

    elif snap_direction in Direction.lst_upper_left_1:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_left[0])

    elif snap_direction in Direction.lst_lower_left_1:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_left[0])

    # quad 2
    elif snap_direction in Direction.lst_lower_right_2:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_right[0])

    elif snap_direction in Direction.lst_upper_right_2:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_right[0])

    elif snap_direction in Direction.lst_upper_left_2:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_right[0])

    elif snap_direction in Direction.lst_lower_left_2:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_lower_right[0])

    # quad 3
    elif snap_direction in Direction.lst_lower_right_3:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_right[0])

    elif snap_direction in Direction.lst_upper_right_3:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_right[0])

    elif snap_direction in Direction.lst_upper_left_3:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_right[0])

    elif snap_direction in Direction.lst_lower_left_3:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_right[0])

    # quad 4
    elif snap_direction in Direction.lst_lower_right_4:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_left[0])

    elif snap_direction in Direction.lst_upper_right_4:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_right[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_left[0])

    elif snap_direction in Direction.lst_upper_left_4:
        p1 = get_point_from_bbox(bb1, Direction.lst_upper_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_left[0])

    elif snap_direction in Direction.lst_lower_left_4:
        p1 = get_point_from_bbox(bb1, Direction.lst_lower_left[0])
        p2 = get_point_from_bbox(bb2, Direction.lst_upper_left[0])

    # invalid
    else:
        raise ValueError(
            f"Not a valid value for ``snap_direction``: {snap_direction}"
        )

    # apply offset
    dx = p1[0] - p2[0] + offset[0]
    dy = p1[1] - p2[1] + offset[1]

    # --- old
    # t1 = db.DCplxTrans(1, 0, False, dx, dy)
    # if cell_2!=target_cell:
    #     target_cell.copy_tree(cell_2.transform(t1))

    # --- some
    if target_cell.layout() == cell_2.layout():
        target_cell.insert(db.DCellInstArray(cell_2, db.DTrans(dx, dy)))
    else:
        cell_2_host = target_cell.layout().create_cell(cell_2.name)
        cell_2_host.copy_tree(cell_2)
        target_cell.insert(db.DCellInstArray(cell_2_host, db.DTrans(dx, dy)))

    return target_cell, target_cell.layout()


def get_point_from_bbox(
    bb,
    point,
):
    """Get a ref point coordinates according to a bounding box.

    ``point`` can refer to any of four main directional snap points, _e.g._,
    'bottom', 'right', 'top', 'left', or any of four corners. See
    ``mnflow.mfda.dld.cad.utils.operations.Direction`` for more detail.

    Parameters
    ----------
    bb : list, tuple
        Bounding box.
    point : _type_
        A valid value refering to any of four main directional snap points or
        corners as specified in
        ``mnflow.mfda.dld.cad.utils.operations.Direction``.

    Returns
    -------
    np.ndarray
        Coordinates of point.
    """

    if point in Direction.lst_bottom:
        coord = ((bb[0][0] + bb[1][0]) / 2, bb[0][1])

    elif point in Direction.lst_right:
        coord = (bb[1][0], (bb[0][1] + bb[1][1]) / 2)

    elif point in Direction.lst_top:
        coord = ((bb[0][0] + bb[1][0]) / 2, bb[1][1])

    elif point in Direction.lst_left:
        coord = (bb[0][0], (bb[0][1] + bb[1][1]) / 2)

    # corners
    elif point in Direction.lst_lower_right:
        coord = (bb[1][0], bb[0][1])

    elif point in Direction.lst_upper_right:
        coord = (bb[1][0], bb[1][1])

    elif point in Direction.lst_upper_left:
        coord = (bb[0][0], bb[1][1])

    elif point in Direction.lst_lower_left:
        coord = (bb[0][0], bb[0][1])

    # invalid
    else:
        raise ValueError(f"Invalid value for ``point``: {point}")

    return np.array(coord)
