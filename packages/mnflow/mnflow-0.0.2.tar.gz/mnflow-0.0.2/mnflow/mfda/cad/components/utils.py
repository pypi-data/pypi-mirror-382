# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import klayout.db as db

from mnflow.mfda.cad.utils.decorators import transform_cell_decorator
from mnflow.mfda.cad.utils.inspections import bbox
from mnflow.mfda.cad.utils.operations import generic_array
from mnflow.mfda.cad.utils.shapes import polygon
from mnflow.mfda.cad.utils.shapes import rectangle
from mnflow.mfda.cad.utils.shapes import trapezoid

"""
While returning the resulted ``cell`` objects, some of the util functions
provide params of 'layout' and 'cell_target' enabling insertion of resulted
shapes and instances directly into the provided ``cell_target`` of the given
``layout``.

Here is an example:

.. highlight:: python
.. code-block:: python

    from mnflow.mfda.dld.cad.components.utils import get_parallel_multichannels
    from mnflow.mfda.dld.cad.utils.shapes import circle

    #--- create a layout with some entities
    ly=db.Layout()
    ly.dbu=1e-3
    l1=ly.layer(1, 0)
    top_cell=ly.create_cell('MY_TOP_CELL')
    top_cell.shapes(l1).insert(circle(2000, dbu=ly.dbu))

    #--- config of multichannels to be made
    config_multichannel = {
        'bar_dims':[5, 3000],
        'grating_pitch':30,
        'grating_area_dim':200,
        'sidewall_width':[100, 100],
        'rot':60,
    }

    #--- building and insertion of multichannels into top cell of layout
    get_parallel_multichannels(layout=ly, cell_target=top_cell,\
        **config_multichannel)
    ly.write('mytestfile.gds')
"""


# -----------------------------------------------------------------------------
# util functions for basic components
# -----------------------------------------------------------------------------


def path(points, width):
    """A path consisting of straight segments/lines passing through a list of
    points.

    Parameters
    -----------
    points : list or tuple
        Points forming the path.
    width : width of path

    Returns
    -------
    db.DPath
        db path.
    """
    src = ""
    for p in points:
        src += f"db.DPoint({p[0]}, {p[1]}),"

    src = f"elem=db.DPath([{src}], {width})"
    exec(src)
    return locals()["elem"]


def pad_light(
    layout,
    padding_entity_dim,
    pitch,
    length,
    ll,
    layer=None,
    cell_target=None,
    opt_reverse_tone=False,
):
    """
    Hierarchical padding features tilig a given area.
    The core feature for padding (unit tile) is a box with a hollow box inside
    of it.
    This is a light padding, as it is hierarchical and does not instantiate
    tiles individually. So, it should not increase the file size significantly.

    Parameters
    ----------
    layout : db.Layout
        Layout of interest.
    padding_entity_dim : list or tuple
        Dimensions of rectangular hollow unit inside each tile.
    pitch : list or tuple
        Pitch of array of tiles.
    length : list or tuple
        Length of domain in each direction to be filled with array
    ll : list or tuple
        Lower left point of bounding box.
    layer : int or NoneType
        Layer of interest on layout.
    cell_target : db.Cell or NoneType
        Target cell of interest.

    Returns
    -------
    db.Layout, db.Cell
        Layout and target cell after creating the array of tiles.
    """

    if layer is None:
        layer = layout.layer(1, 0)

    TDBU = db.CplxTrans(layout.dbu).inverted()
    box = db.Region(TDBU * db.DBox(0, 0, *pitch))
    to_be_cut = db.Region(
        TDBU
        * db.DBox(
            (pitch[0] - padding_entity_dim[0]) / 2.0,
            (pitch[1] - padding_entity_dim[1]) / 2.0,
            (pitch[0] + padding_entity_dim[0]) / 2.0,
            (pitch[1] + padding_entity_dim[1]) / 2.0,
        )
    )

    if opt_reverse_tone:
        entity = to_be_cut
    else:
        entity = box - to_be_cut

    tmp_cell = layout.create_cell("tmp_unit")
    tmp_cell.shapes(layer).insert(entity)

    cell_target = generic_array(
        layout=layout,
        cell_src=tmp_cell,
        pitch=pitch,
        length=length,
        trans=ll,
        cell_target=cell_target,
    )

    return layout, cell_target


# -----------------------------------------------------------------------------
# util functions for more complex components
# -----------------------------------------------------------------------------


@transform_cell_decorator
def grating(
    layout,
    layer,
    grating_pitch,
    grating_area_dims,
    bar_dims=None,
    bar=None,
    grating_bar_row_ll=[0, 0],
    cell_target=None,
    grating_cell_name="grating",
    unit_grating_cell_name="unit_grating",
):
    """Get a generic array/grating.

    Parameters
    ----------
    layout : db.Layout
        Layout of interest
    layer : int
        Layer of interest
    grating_pitch : list or tuple
        Pitch of array in each direction.
    grating_area_dims : list or tuple
        Dimensions of area to be covered in each direction.
    bar_dims : list or tuple or NoneType
        Dimensions of rectangular (2 components) or trapezoidal (3 components)
        bar if provided. None for the case of explicitly passing an item to be
        arrayed. Default: None.
    bar : db.Region or NoneType
        Region to be arrayed. If None, a rectangular/trapezoidal bar is
        considered from the corresponding dimensions: `bar_dims`. None by
        default.
    grating_bar_row_ll : tuple or list
        Lower left corner of bounding box. By default is [0, 0].
    cell_target : db.Cell or NoneType
        Target cell of interest. Default: None.
    grating_cell_name : string
        Grating cell name. Default: 'grating'.
    unit_grating_cell_name : string
        Unit grating cell name. Default: 'unit_grating'.

    Returns
    -------
    db.Cell
        Target cell.
    """

    # --- sanity check
    assert not (
        bar is None and bar_dims is None
    ), "Either `bar` or `bar_dims` needs to be provided."

    # target cell
    if cell_target is None:
        print(
            """
              Note:
                  cell_target is not passed.
                  A new cell is created and returned.
                  Make sure you catch it!
              """
        )
        cell_target = layout.create_cell(grating_cell_name)

    # bar
    if bar is None:
        if len(bar_dims) == 2:
            bar = rectangle(
                *bar_dims, reg_ll=grating_bar_row_ll, dbu=layout.dbu
            )
        elif len(bar_dims) == 3:
            bar = trapezoid(
                *bar_dims, reg_ll=grating_bar_row_ll, dbu=layout.dbu
            )
    else:
        t1 = db.DTrans(
            db.DVector(
                grating_bar_row_ll[0] / layout.dbu,
                grating_bar_row_ll[1] / layout.dbu,
            )
        )
        bar = bar.transformed(t1)

    # unit cell
    unit_cell = layout.create_cell(unit_grating_cell_name)
    unit_cell.shapes(layer).insert(bar, db.DTrans())
    # ------------------------------------------------------------------

    # array
    generic_array(
        layout=layout,
        cell_src=unit_cell,
        cell_target=cell_target,
        pitch=grating_pitch,
        length=grating_area_dims,
    )

    return cell_target


@transform_cell_decorator
def grating_with_sidewall(
    layout,
    layer,
    grating_pitch,
    grating_area_dims,
    bar_dims=None,
    bar=None,
    cell_target=None,
    grating_area_ll=None,
    bar_offset=None,
    num_extra_bar_column=None,
    sidewall_width=None,
    opt_clip=False,
    grating_cell_name=None,
    unit_grating_cell_name=None,
    margin_top=None,
    block_width=None,
):
    """Get a generic array/grating confined between two sidewalls.

    Parameters
    ----------
    layout : db.Layout
        Layout of interest
    layer : int
        Layer of interest
    grating_pitch : float, list or tuple
        Pitch of array in each direction, in case ``grating_pitch`` is a
        scalar, it is applied as pitch in horizontal direction (along the
        width of system); in this case, vertical pitch (y-axis) equals
        the bar length in y-direction.
    grating_area_dims : float, list or tuple
        Dimensions of area confined between sidewalls to be covered in each
        direction, in case ``grating_area_dims`` is a scalar, it denotes the
        width of grating area; in this case, height (y-axis) to be determined
        from the bar dimensions.
    bar_dims : list or tuple or NoneType
        Dimensions of rectangular (2 components) or trapezoidal (3 components)
        bar if provided. None for the case of explicitly passing an item to
        be arrayed. Default: None.
    bar : db.Region or NoneType
        Region to be arrayed. If None, a rectangular/trapezoidal bar is
        considered from the corresponding dimensions: `bar_dims`. None by
        default.
    grating_area_ll : tuple or list
        Lower left coordinates of grating area (lower right corner of left
        sidewall). By default is [0, 0].
    cell_target : db.Cell or NoneType
        Target cell of interest. Default: None.
    bar_offset : list or tuple
        Offset of bar in each direction. Default: [0, 0].
    num_extra_bar_column : int
        Additional columns of bar enabling slide of bars to tune geometry, by
        default 5.
    sidewall_width : float, list, tuple, optional
        Sidewalls width; in the case of a scalar, both sidewalls will have a
        same width; in the case of a list/tuple of two components, the first
        referst to left wall, and the second item to the right, by default 0.
    opt_clip : bool
        Whether to clip bars outside of grating area. Default: False.
    grating_cell_name : string
        Grating cell name. Default: 'grating'.
    unit_grating_cell_name : string
        Unit grating cell name. Default: 'unit_grating'.
    margin_top : float
        Margin on top of grating area between sidewalls. Default: 0.
    block_width : list or tuple
        Distance from left (first component) and right (second component)
        sidewalls to be blocked. Default: [0,0].

    Returns
    -------
    db.Cell, db.Layout
        Target cell and layout.

    **Note:**
        Not returning ``layout`` seems to cause destruction of ``cell_target``
        out of scope.
    """

    # --- default params
    if grating_area_ll is None:
        grating_area_ll = (0, 0)
    if bar_offset is None:
        bar_offset = (0, 0)
    if num_extra_bar_column is None:
        num_extra_bar_column = 0
    if sidewall_width is None:
        sidewall_width = 0.0
    if opt_clip is None:
        opt_clip = False
    if grating_cell_name is None:
        grating_cell_name = "grating"
    if unit_grating_cell_name is None:
        unit_grating_cell_name = "unit_grating"
    if margin_top is None:
        margin_top = 0.0
    if block_width is None:
        block_width = (0, 0)

    # --- sanity check
    assert not (
        bar is None and bar_dims is None
    ), "Either ``bar`` or ``bar_dims`` is required."

    # ---------------------------------------------------------
    # default config
    if bar_dims is None:
        bb = bbox(bar)
        bar_dims = [
            bb[1][0] - bb[0][0],
            bb[1][1] - bb[0][1],
        ]
    else:
        assert type(bar_dims) in [tuple, list]

    if type(grating_area_dims) not in [tuple, list]:
        grating_area_dims = [
            grating_area_dims,
            bar_dims[1] + bar_offset[1] + margin_top,
        ]
    if type(grating_pitch) not in [tuple, list]:
        grating_pitch = [
            grating_pitch,
            grating_area_dims[1],
        ]  # set pitch[1] equal to length[1] --> only 1 item in y-dir
        # grating_pitch = [grating_pitch, bar_dims[1]]

    if cell_target is None:
        print(
            """
            Note:
                ``cell_target`` is not passed.
                A new cell is created and returned.
                Make sure you catch it!
            """
        )
        cell_target = layout.create_cell("grating_w_sidewall")
    # ---------------------------------------------------------

    # --- creating cells
    cell_grating = layout.create_cell(grating_cell_name)
    cell_target.insert(
        db.DCellInstArray(cell_grating.cell_index(), db.DTrans())
    )

    # --- grating if needed
    _grating_required = True
    for ind_dir in range(2):
        if grating_area_dims[ind_dir] < grating_pitch[ind_dir]:
            _grating_required = False

    # grating if needed
    if _grating_required:
        grating(
            layout=layout,
            layer=layer,
            grating_pitch=grating_pitch,
            bar_dims=bar_dims,
            bar=bar,
            grating_bar_row_ll=[
                grating_area_ll[0]
                + bar_offset[0]
                - (num_extra_bar_column - 1) * grating_pitch[0] / 2,
                grating_area_ll[1] + bar_offset[1],
            ],
            grating_area_dims=[
                grating_area_dims[0] + num_extra_bar_column * grating_pitch[0],
                grating_area_dims[1],
            ],
            cell_target=cell_grating,
            grating_cell_name=grating_cell_name,
            unit_grating_cell_name=unit_grating_cell_name,
        )

    # ----------------------------------
    # block on left and right sides
    # ----------------------------------
    if block_width[0] > 0:
        block_bar_left = rectangle(
            block_width[0],
            grating_area_dims[1],
            reg_ll=grating_area_ll,
            dbu=layout.dbu,
        )
        cell_grating.shapes(layer).insert(block_bar_left)

    if block_width[1] > 0:
        block_bar_right = rectangle(
            block_width[1],
            grating_area_dims[1],
            reg_ll=[
                grating_area_ll[0] + grating_area_dims[0] - block_width[1],
                grating_area_ll[1],
            ],
            dbu=layout.dbu,
        )
        cell_grating.shapes(layer).insert(block_bar_right)

    # ------------------------------------
    # adding sidewalls
    # ------------------------------------

    # if ``sidewall_width`` is a scalar--> both sidewalls with the same width
    if sidewall_width is None:
        sidewall_width = 0.0
    if type(sidewall_width) not in [list, tuple]:
        sidewall_width = [sidewall_width, sidewall_width]
    if len(sidewall_width) != 2:
        raise ValueError(
            f"``sidewall_width`` is expected to be a scalar or a list/tuple\n\
            of the length of 2. Currently, it is {sidewall_width}"
        )

    # -------------------------------
    # clipping the bars
    # -------------------------------
    TDBU = db.CplxTrans(layout.dbu).inverted()
    t1 = db.DTrans(
        db.DVector(
            grating_area_ll[0] / layout.dbu,
            grating_area_ll[1] / layout.dbu,
        )
    )
    if opt_clip and _grating_required:
        clip_box = db.DBox(0, 0, *grating_area_dims)
        clip_box = db.Region(TDBU * clip_box)
        clip_box.transform(t1)
        region = db.Region(cell_grating.begin_shapes_rec(layer))
        region = region & clip_box
        cell_grating.clear()
        cell_grating.shapes(layer).insert(region)

        layout.prune_cell(layout.cell_by_name(unit_grating_cell_name), -1)

    # --- sidewalls
    sidewall_points = None

    # -----------------------------------------------------------------
    # left sidewall
    # -----------------------------------------------------------------
    if sidewall_width[0] > 0:
        """
        translation to `grating_area_ll`
        """

        sidewall_points = [
            [0, 0],
            [0, grating_area_dims[1]],
            [-sidewall_width[0], grating_area_dims[1]],
            [-sidewall_width[0], 0],
        ]

        reg_sidewall_left = db.Region(TDBU * polygon(sidewall_points))
        reg_sidewall_left = reg_sidewall_left.transformed(t1)

        cell_grating.shapes(layer).insert(reg_sidewall_left)

        # -----------------------------------------------------------------
        # right sidewall by mirroring the left one
        # -----------------------------------------------------------------
        if sidewall_width[1] == sidewall_width[0]:
            this_x_mirror = grating_area_ll[0] + grating_area_dims[0] / 2
            dx_trans = 2.0 * this_x_mirror
            cell_grating.shapes(layer).insert(
                reg_sidewall_left, db.DTrans(db.DTrans.M90, dx_trans, 0)
            )

    if sidewall_width[1] > 0 and sidewall_width[1] != sidewall_width[0]:

        sidewall_points = [
            [grating_area_dims[0], 0],
            [grating_area_dims[0], grating_area_dims[1]],
            [grating_area_dims[0] + sidewall_width[1], grating_area_dims[1]],
            [grating_area_dims[0] + sidewall_width[1], 0],
        ]

        reg_sidewall_right = db.Region(TDBU * polygon(sidewall_points))
        reg_sidewall_right = reg_sidewall_right.transformed(t1)

        cell_grating.shapes(layer).insert(reg_sidewall_right)

    return cell_target, layout


@transform_cell_decorator
def filter_with_sidewall(
    filter_pitch_entity,
    filter_len_nondim,
    filter_half_pitch_nondim,
    filter_area_ll,
    filter_area_dims,
    filter_core_entity,
    filter_core_entity_offset=[0, 0],
    filter_margin_top=0,
    num_extra_column=5,
    sidewall_width=0,
    opt_clip=False,
    block_width=[0, 0],
    layout=None,
    layer=None,
    cell_target=None,
    cell_target_name="filter_cell_tot",
    filter_cell_name="filter_cell",
    filter_row_unit_name="filter_row_unit",
    filter_unit_name="filter_unit",
    filter_col_unit_name="filter_col_unit",
    filter_col_unit2_name="filter_col_unit2",
):
    """Get a generic array/grating confined between two sidewalls.

    Parameters
    ----------
    filter_pitch_entity : float
        Pitch of entity array in each segment of filter.
    filter_len_nondim : int
        Length of filter non-dimensionalized by pitch of entity array segments.
    filter_half_pitch_nondim : int
        Half-pitch of serpentine filter non-dimensionalized by pitch of entity
        array segments.
    filter_area_ll : list or tuple
        Lower left coordinates of filter area excluding sidewalls.
    filter_area_dims : list or tuple
        Dimensions of filter area excluding sidewalls.
    filter_core_entity : db.Region
        Entity to be arrayed to form the filter.
    filter_core_entity_offset : list or tuple
        Offset of entities in each direction. Default: [0, 0].
    filter_margin_top : float
        Margin on top of filter area between sidewalls. Default: 0.
    num_extra_column : int
        Additional columns of entities enabling slide of entities to tune
        geometry. Default: 5.
    sidewall_width : float
        Sidewall width. Default: 0.
    opt_clip : bool
        Whether to clip bars outside of grating area. Default: False.
    block_width : list or tuple
        Distance from left (first component) and right (second component)
        sidewalls to be blocked. Default: [0,0].
    layout : db.Layout or NoneType
        Layout of interest. Default: None.
    layer : int or NoneTyep
        Layer of interest. Default: None.
    cell_target : db.Cell or NoneType
        Target cell of interest. Default: None.

    Returns
    -------
    db.Cell
        Target cell.
    """

    # --------------------------------------------------
    # hierarchy
    # --------------------------------------------------
    # The case of not providing any of `layout`, `layer` and `cell_target`
    # is not working
    if layout is None:
        if cell_target is None:
            layout = db.Layout()
            layout.dbu = 1e-3
        else:
            layout = cell_target.layout()
    if layer is None:
        layer = layout.layer(1, 0)
    elif type(layer) in [tuple, list]:
        layer = layout.layer(*layer)

    if cell_target is None:
        cell_target = layout.create_cell(cell_target_name)

    filter_cell = layout.create_cell(filter_cell_name)
    filter_row_unit = layout.create_cell(filter_row_unit_name)
    filter_unit = layout.create_cell(filter_unit_name)
    filter_col_unit = layout.create_cell(filter_col_unit_name)
    filter_col_unit2 = layout.create_cell(filter_col_unit2_name)

    cell_target.insert(db.DCellInstArray(filter_cell.cell_index(), db.DTrans()))
    # ------------------------------------------------------------

    TDBU = db.CplxTrans(layout.dbu).inverted()

    bb = bbox(filter_core_entity)
    filter_core_entity_dims = [
        bb[1][0] - bb[0][0],
        bb[1][1] - bb[0][1],
    ]

    filter_len = filter_len_nondim * filter_pitch_entity
    filter_half_pitch = filter_half_pitch_nondim * filter_pitch_entity

    if type(filter_area_dims) not in [tuple, list]:
        filter_area_dims = [
            filter_area_dims,
            filter_len
            + filter_core_entity_offset[1]
            + filter_margin_top
            + filter_core_entity_dims[1] / 2.0,
        ]

    # ll of lowerleftmost bar
    filter_ll = [
        filter_area_ll[0] + filter_core_entity_offset[0],
        filter_area_ll[1] + filter_core_entity_offset[1],
    ]

    """
    filter_row_unit
    """
    # entity to produce the lower tip
    filter_row_unit.shapes(layer).insert(
        filter_core_entity, db.DCplxTrans(1, 0, False, db.DVector(*filter_ll))
    )

    # entity to produce the upper tip
    filter_row_unit.shapes(layer).insert(
        filter_core_entity,
        db.DCplxTrans(
            1,
            0,
            False,
            db.DVector(
                filter_ll[0] + filter_half_pitch, filter_ll[1] + filter_len
            ),
        ),
    )

    # producing lower and upper tips simultaneously
    generic_array(
        layout=layout,
        cell_src=filter_row_unit,
        cell_target=filter_unit,
        pitch=[
            filter_pitch_entity,
            1,
        ],  # set pitch[1] equal to length[1] --> only 1 item in y-dir
        length=[filter_half_pitch, 1],
    )

    # ---------------
    # column of filter
    # ---------------
    # entity to produce the first vertical edge
    filter_col_unit.shapes(layer).insert(
        filter_core_entity,
        db.DCplxTrans(
            1,
            0,
            False,
            db.DVector(filter_ll[0] + filter_half_pitch, filter_ll[1]),
        ),
    )

    # producing the first vertical edge
    generic_array(
        layout=layout,
        cell_src=filter_col_unit,
        cell_target=filter_unit,
        pitch=[
            1,
            filter_pitch_entity,
        ],  # set pitch[0] equal to length[0] --> only 1 item in x-dir
        length=[1, filter_len],
    )

    # column 2
    # entity to produce the second vertical edge
    filter_col_unit2.shapes(layer).insert(
        filter_core_entity,
        db.DCplxTrans(
            1,
            0,
            False,
            db.DVector(
                filter_ll[0] + 2 * filter_half_pitch,
                filter_ll[1] + filter_pitch_entity,
            ),
        ),
    )

    # producing the second vertical edge
    generic_array(
        layout=layout,
        cell_src=filter_col_unit2,
        cell_target=filter_unit,
        pitch=[
            1,
            filter_pitch_entity,
        ],  # set pitch[0] equal to length[0] --> only 1 item in x-dir
        length=[1, filter_len],
    )

    # ---------------
    # copying row&col
    # ---------------
    generic_array(
        layout=layout,
        cell_src=filter_unit,
        cell_target=filter_cell,
        pitch=[
            2.0 * filter_half_pitch,
            1,
        ],  # set pitch[1] equal to length[1] --> only 1 item in y-dir
        length=[filter_area_dims[0] + num_extra_column * filter_half_pitch, 1],
    )

    # --------------------
    # centering the filter
    # --------------------
    trans_cell_center = db.DTrans(
        db.DVector(
            -num_extra_column * filter_half_pitch / 2,
            0,
        )
    )
    filter_cell.transform(trans_cell_center)

    # ------------------------------------
    # adding sidewalls
    # ------------------------------------
    sidewall_points = None
    if sidewall_width > 0:
        """
        translation to `filter_area_ll`
        """
        trans_reg = db.DTrans(
            db.DVector(
                filter_area_ll[0] / layout.dbu,
                filter_area_ll[1] / layout.dbu,
            )
        )

        if opt_clip:
            # -------------------------------
            # clipping the bars
            # -------------------------------
            clip_box = db.DBox(0, 0, *filter_area_dims)
            clip_box = db.Region(TDBU * clip_box)
            clip_box.transform(trans_reg)
            region = db.Region(filter_cell.begin_shapes_rec(layer))
            region = region & clip_box
            filter_cell.clear()
            filter_cell.shapes(layer).insert(region)

            layout.prune_cell(layout.cell_by_name(filter_unit_name), -1)
            # -------------------------------

        sidewall_points = [
            [0, 0],
            [0, filter_area_dims[1]],
            [-sidewall_width, filter_area_dims[1]],
            [-sidewall_width, 0],
        ]

        reg_sidewall_left = db.Region(TDBU * polygon(sidewall_points))
        reg_sidewall_left = reg_sidewall_left.transformed(trans_reg)

        filter_cell.shapes(layer).insert(reg_sidewall_left)

        # -----------------------------------------------------------------
        # right sidewall by mirroring the left one
        # -----------------------------------------------------------------
        this_x_mirror = filter_area_ll[0] + filter_area_dims[0] / 2
        dx_trans = 2.0 * this_x_mirror
        filter_cell.shapes(layer).insert(
            reg_sidewall_left, db.DTrans(db.DTrans.M90, dx_trans, 0)
        )

        # ----------------------------------
        # block on left and right sides
        # ----------------------------------
        if block_width[0] > 0:
            block_bar_left = rectangle(
                block_width[0],
                filter_area_dims[1],
                reg_ll=filter_area_ll,
                dbu=layout.dbu,
            )
            filter_cell.shapes(layer).insert(block_bar_left)

        if block_width[1] > 0:
            block_bar_right = rectangle(
                block_width[1],
                filter_area_dims[1],
                reg_ll=[
                    filter_area_ll[0] + filter_area_dims[0] - block_width[1],
                    filter_area_ll[1],
                ],
                dbu=layout.dbu,
            )
            filter_cell.shapes(layer).insert(block_bar_right)

    return cell_target


@transform_cell_decorator
def get_parallel_multichannels(
    # Channels
    bar_dims,
    grating_pitch,
    grating_area_dim,
    sidewall_width,
    # CAD
    layout=None,
    layer=None,
    cell_target=None,
    cell_target_name=None,
    multichannel_cell_name=None,
    unit_grating_cell_name=None,
    # Misc.
    bar_offset=None,
    grating_area_ll=None,
    margin_top=None,
    block_width=None,
):
    """Get an array of parallel channels between two sidewalls.

    Parameters
    ----------

    **Channels**
    bar_dims : list or tuple
        Dimensions of rectangular (2 components) or trapezoidal (3 components)
        bar if provided. None for the case of explicitly passing an item to be
        arrayed.
    grating_pitch : float
        Pitch of array.
    grating_area_dim : float
        Dimension of area confined between sidewalls to be covered.
    sidewall_width : float, list, tuple
        Sidewalls width; in the case of a scalar, both sidewalls will have a
        same width; in the case of a list/tuple of two components, the first
        referst to left wall, and the second item to the right.

    **CAD**
    layout : db.Layout
        Layout of interest, by default None
    layer : int
        Layer of interest, by default None
    cell_target : db.Cell
        Target cell of interest, by default None
    cell_target_name : str
        Name of target cell if ``cell_target`` is not given.
    multichannel_cell_name : str
        Name of multichannel cell
    unit_grating_cell_name : str
        Name of unit of grating cell

    **Misc.**
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

    Returns
    -------
    db.Cell, db.Layout
        Target cell and layout
    """

    # --- default params
    if layout is None:
        layout = db.Layout()
        layout.dbu = 1e-3
    if layer is None:
        layer = layout.layer(1, 0)
    elif type(layer) in [tuple, list]:
        layer = layout.layer(*layer)
    if cell_target_name is None:
        cell_target_name = "Multichannel_top"
    if multichannel_cell_name is None:
        multichannel_cell_name = "multichannel"
    if unit_grating_cell_name is None:
        unit_grating_cell_name = "unit_grating"
    if bar_offset is None:
        bar_offset = (0.0, 0.0)
    if grating_area_ll is None:
        grating_area_ll = (0.0, 0.0)
    if margin_top is None:
        margin_top = 0.0
    if block_width is None:
        block_width = (0.0, 0.0)

    # --- default config
    if cell_target is None:
        cell_target = layout.create_cell(cell_target_name)

    # --- create grating with sidewalls
    grating_with_sidewall(
        layout=layout,
        layer=layer,
        grating_pitch=grating_pitch,
        grating_area_dims=grating_area_dim,
        bar_dims=bar_dims,
        grating_area_ll=grating_area_ll,
        cell_target=cell_target,
        bar_offset=bar_offset,
        num_extra_bar_column=0,
        sidewall_width=sidewall_width,
        opt_clip=False,
        grating_cell_name=multichannel_cell_name,
        unit_grating_cell_name=unit_grating_cell_name,
        margin_top=margin_top,
        block_width=block_width,
    )

    return cell_target, layout
