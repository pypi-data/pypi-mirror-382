# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


from mnflow.mfda.cad.utils.shapes import generic_shape


# ----------------------------------------------------------------------------
# Profile generators for acc. sidewall
# ----------------------------------------------------------------------------
def get_sidewall_acc_00(
    acc_dots_full,
    sidewall_width,
):
    """To be used as default."""

    # axial pitch: delta_y between adjacent boundary entities
    pitch_a = acc_dots_full[-1][1, 1] - acc_dots_full[-1][0, 1]

    lst_points = []

    # half-pitch below downstreammost entity
    lst_points.append(
        [acc_dots_full[-1][0, 0], acc_dots_full[-1][0, 1] - pitch_a / 2.0]
    )

    # center of boundary entities
    for this_point in acc_dots_full[-1]:
        lst_points.append(this_point.tolist())

    # upstreammost row
    lst_points.append([acc_dots_full[-1][0, 0], acc_dots_full[-1][-1, 1]])
    lst_points.append(
        [acc_dots_full[-1][0, 0], acc_dots_full[-1][-1, 1] + pitch_a / 2.0]
    )
    lst_points.append(
        [
            max(acc_dots_full[-1][0, 0], acc_dots_full[-1][-1, 0])
            + sidewall_width,
            acc_dots_full[-1][-1, 1] + pitch_a / 2.0,
        ]
    )

    # right side of first point
    lst_points.append(
        [
            max(acc_dots_full[-1][0, 0], acc_dots_full[-1][-1, 0])
            + sidewall_width,
            acc_dots_full[-1][0, 1] - pitch_a / 2.0,
        ]
    )

    reg = generic_shape(lst_points, dbu=1e-3)

    return reg, lst_points


def get_sidewall_acc_01(
    acc_dots_full,
    sidewall_width,
):

    # axial pitch: delta_y between adjacent boundary entities
    pitch_a = acc_dots_full[-1][1, 1] - acc_dots_full[-1][0, 1]

    p1 = [acc_dots_full[-1][0, 0], acc_dots_full[-1][0, 1] - pitch_a / 2.0]
    p2 = acc_dots_full[-1][0].tolist()

    p3 = acc_dots_full[-1][-1].tolist()

    p4 = [acc_dots_full[-1][0, 0], p3[1]]
    p5 = [acc_dots_full[-1][0, 0], p3[1] + pitch_a / 2.0]

    p6 = [
        max(acc_dots_full[-1][0, 0], acc_dots_full[-1][-1, 0]) + sidewall_width,
        p3[1] + pitch_a / 2.0,
    ]

    p7 = [p6[0], p1[1]]

    lst_points = [
        p1,
        p2,
        p3,
        p4,
        p5,
        p6,
        p7,
    ]

    reg = generic_shape(lst_points, dbu=1e-3)

    return reg, lst_points


# ----------------------------------------------------------------------------
# Profile generators for dep. sidewall
# ----------------------------------------------------------------------------
def get_dep_sidewall_00(
    dep_dots_full,
    sidewall_width,
):
    """To be used as default."""
    # axial pitch: delta_y between adjacent boundary entities
    pitch_a = dep_dots_full[-1][1, 1] - dep_dots_full[-1][0, 1]

    lst_points = []

    # --- downstream
    # first point: x from entity on upstreammost row, y: half-pitch below
    # entity on downstreammost row
    lst_points.append(
        [dep_dots_full[-1][-2, 0], dep_dots_full[-1][0, 1] - pitch_a / 2.0]
    )
    lst_points.append([dep_dots_full[-1][-2, 0], dep_dots_full[-1][0, 1]])

    # center of boundary entities -- Note: last entity to be discarded as that
    # is the downstreammost entity of upstream neighbor (see core.DLD for more
    # detail).
    for this_point in dep_dots_full[-1][:-1]:
        lst_points.append(this_point.tolist())

    # --- upstream
    lst_points.append(
        [dep_dots_full[-1][-2, 0], dep_dots_full[-1][-2, 1] + pitch_a / 2.0]
    )
    lst_points.append(
        [
            dep_dots_full[-1][-2, 0] - sidewall_width,
            dep_dots_full[-1][-2, 1] + pitch_a / 2.0,
        ]
    )

    # --- back to downstream, left side of first point
    lst_points.append(
        [
            dep_dots_full[-1][-2, 0] - sidewall_width,
            dep_dots_full[-1][0, 1] - pitch_a / 2.0,
        ]
    )

    reg = generic_shape(lst_points, dbu=1e-3)

    return reg, lst_points


def get_dep_sidewall_01(
    dep_dots_full,
    sidewall_width,
):

    # axial pitch: delta_y between adjacent boundary entities
    pitch_a = dep_dots_full[-1][1, 1] - dep_dots_full[-1][0, 1]

    lst_points = []

    # x-coord of intersection of two lines
    # 1. line connecting topmost entity to downstreammost entity of upstream
    # neighboring unit
    # 2. horizontal line downstream of unit
    dep_interface_x_avg = (
        dep_dots_full[-1][-2, 0] + dep_dots_full[-1][0, 0]
    ) / 2.0

    # --- downstream
    # first point: intersection of two lines mentioned above
    lst_points.append(
        [dep_interface_x_avg, dep_dots_full[-1][0, 1] - pitch_a / 2.0]
    )

    # center of boundary entities -- Note: last entity to be discarded as that
    # is the downstreammost entity of upstream neighbor (see core.DLD for more
    # detail).
    for this_point in dep_dots_full[-1][:-1]:
        lst_points.append(this_point.tolist())

    # --- upstream
    lst_points.append(
        [dep_interface_x_avg, dep_dots_full[-1][-1, 1] - pitch_a / 2.0]
    )
    lst_points.append(
        [
            dep_dots_full[-1][-2, 0] - sidewall_width,
            dep_dots_full[-1][-1, 1] - pitch_a / 2.0,
        ]
    )

    # --- back to downstream left side of first point
    lst_points.append(
        [
            dep_dots_full[-1][-2, 0] - sidewall_width,
            dep_dots_full[-1][0, 1] - pitch_a / 2.0,
        ]
    )

    reg = generic_shape(lst_points, dbu=1e-3)

    return reg, lst_points


# --------------------------------------------------------------------
# list of availble profile generators for sidewall
# --------------------------------------------------------------------
lst_get_sidewall_acc = [
    get_sidewall_acc_00,
    get_sidewall_acc_01,
]

lst_get_sidewall_dep = [
    get_dep_sidewall_00,
    get_dep_sidewall_01,
]
