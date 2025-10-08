# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import klayout.db as db

# ----------------------------------------------------------------------------
# examination utils
# ----------------------------------------------------------------------------


def bbox(obj, dbu=0.001):
    """Get the bounding box.

    Parameters
    ----------
    obj : db.Cell or db.Region or db.Layout
        _description_
    dbu : float, optional
        unit used when using db, by default 0.001, i.e., 1 nm.

    Returns
    -------
    list
        [(lower left coordinates), (upper right coordinates)]
    """
    if type(obj) is db.Cell:
        lst_raw = (
            str(obj.dbbox()).strip("(").strip(")").replace(";", ",").split(",")
        )
        bb_lst = list(map(float, lst_raw))
    elif type(obj) is db.Region:
        lst_raw = (
            str(obj.bbox()).strip("(").strip(")").replace(";", ",").split(",")
        )
        bb_lst = list(map(float, lst_raw))
        for sn, item in enumerate(bb_lst):
            bb_lst[sn] *= dbu
    elif type(obj) is db.Layout:
        # if obj is a layout, its top cell is considered
        if len(obj.top_cells()) == 0:
            return None
        else:
            return bbox(obj.top_cells()[0], dbu)
    else:
        print(
            f"""obj can be only Cell, Region, or Layout. The obj type:
{type(obj)}"""
        )

    # at this point, obj is either a Cell, or a Region as a top cell is
    # considered for the case of Layout as mentioned above.
    assert type(obj) is db.Cell or type(obj) is db.Region

    bb = [
        (bb_lst[0], bb_lst[1]),
        (bb_lst[2], bb_lst[3]),
    ]

    return bb


def center(obj, dbu=0.001):
    """Get the center of bbox of object.

    Parameters
    ----------
    obj : db.Cell or db.Region or db.Layout
        Object to be inspected.
    dbu : float, optional
        unit used when using db, by default 0.001, i.e., 1 nm.

    Returns
    -------
    tuple
        (center coordinate.x, center coordinate.y)
    """

    bb = bbox(obj)
    center_coords = ((bb[0][0] + bb[1][0]) / 2.0, (bb[0][1] + bb[1][1]) / 2.0)

    return center_coords


# ----------------------------------------
# dev. utils
# ----------------------------------------
def get_valid_cell_index(
    layout,
    verbose=False,
):
    """Get a list of valid cell indices.

    Parameters
    ----------
    layout : db.Layout
        Layout of interest.
    verbose : bool, optional
        verbose, by default False

    Returns
    -------
    list
        list of valid cell indices
    """
    num_cell = layout.cells()
    lst_valid_cell_index = []
    for sn in range(num_cell):
        try:
            cell = layout.cell(sn)
            lst_valid_cell_index.append(cell.cell_index())
        except Exception as e:
            if verbose:
                print(e)
    return lst_valid_cell_index


def get_valid_cell(
    layout,
):
    """Get list of valid cells.

    Parameters
    ----------
    layout : db.Layout
        Layout of interest.

    Returns
    -------
    list
        list of valid cells
    """
    lst_valid_cell_index = get_valid_cell_index(layout)
    lst_valid_cell = []
    for index in lst_valid_cell_index:
        lst_valid_cell.append(layout.cell(index))
    return lst_valid_cell


def get_cell_by_name(
    layout,
    cell_name,
    strict=False,
):
    """Get cell by name.

    Parameters
    ----------
    layout : db.Layout
        Layout of interest.
    cell_name : string
        Cell name.
    strict : bool
        If true, only cells with the exact name are considered. Otherwise,
        cells with names starting with `cell_name+'$'` will be considered.

    Returns
    -------
    list
        List of cells with desired name.
    """
    lst_valid_cell = get_valid_cell(layout)
    lst_cell = []
    for cell in lst_valid_cell:
        if strict:
            if cell.name == cell_name:
                lst_cell.append(cell)
        else:
            if cell.name == cell_name or cell.name.startswith(cell_name + "$"):
                lst_cell.append(cell)
    return lst_cell
