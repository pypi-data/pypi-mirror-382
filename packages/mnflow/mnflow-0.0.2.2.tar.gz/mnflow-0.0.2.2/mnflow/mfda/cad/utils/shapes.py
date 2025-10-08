# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import klayout.db as db

from mnflow.mfda.cad.utils.decorators import polygon_to_region_decorator
from mnflow.mfda.cad.utils.decorators import transform_region_decorator


def polygon(lst):
    """Make a polygon from a list of coordinates."""

    src = ""
    for p in lst:
        src += f"db.DPoint({p[0]}, {p[1]}),"

    src = f"elem=db.DPolygon([{src}])"
    exec(src)
    return locals()["elem"]


@transform_region_decorator
@polygon_to_region_decorator
def generic_shape(lst):
    """Make a region from a list of coordinates."""

    pol = polygon(lst)
    return pol


@transform_region_decorator
@polygon_to_region_decorator
def circle(lx, ly=None, num_points=32):
    """Make a circle with bbox centered at (0,0)."""

    if ly is None:
        ly = lx

    pol = db.DPolygon.ellipse(
        db.DBox(-lx / 2, -ly / 2, lx / 2, ly / 2), num_points
    )

    return pol


@transform_region_decorator
@polygon_to_region_decorator
def triangle(length):
    """Make a triangle with sidelegth of ``length`` with bbox centered at
    (0,0)."""

    pol = db.DPolygon(
        [
            db.DPoint(-length / 2, -length * 0.2887),
            db.DPoint(length / 2, -length * 0.2887),
            db.DPoint(0, length * 0.5774),
        ]
    )

    return pol


@transform_region_decorator
@polygon_to_region_decorator
def rectangle(lx, ly=None):
    """Make a rectangle with bbox centered at (0,0)."""

    if ly is None:
        ly = lx

    pol = db.DPolygon(
        [
            db.DPoint(-lx / 2, -ly / 2),
            db.DPoint(lx / 2, -ly / 2),
            db.DPoint(lx / 2, ly / 2),
            db.DPoint(-lx / 2, ly / 2),
        ]
    )

    return pol


@transform_region_decorator
@polygon_to_region_decorator
def box(ll, rr):
    """Make a box from lower-left (``ll``) and upper-right (``rr``)
    coordinates."""

    pol = db.DPolygon(
        [
            db.DPoint(*ll),
            db.DPoint(rr[0], ll[1]),
            db.DPoint(*rr),
            db.DPoint(ll[0], rr[1]),
        ]
    )

    return pol


@transform_region_decorator
@polygon_to_region_decorator
def trapezoid(lx1, ly=None, lx2=None):
    """Make a trapezoid with bbox centered at (0,0)."""

    if ly is None:
        ly = lx1
    if lx2 is None:
        lx2 = lx1

    pol = db.DPolygon(
        [
            db.DPoint(-lx1 / 2, -ly / 2),
            db.DPoint(lx1 / 2, -ly / 2),
            db.DPoint(lx2 / 2, ly / 2),
            db.DPoint(-lx2 / 2, ly / 2),
        ]
    )

    return pol


@transform_region_decorator
@polygon_to_region_decorator
def square(
    length,
):
    """Make a square with sidelegth of ``l`` with bbox centered at (0,0)."""
    pol = db.DPolygon(
        [
            db.DPoint(-length / 2, -length / 2),
            db.DPoint(length / 2, -length / 2),
            db.DPoint(length / 2, length / 2),
            db.DPoint(-length / 2, length / 2),
        ]
    )

    return pol


@transform_region_decorator
@polygon_to_region_decorator
def beam_l(lx, ly, t):
    """Make a L-beam with bbox centered at (0,0)."""

    beam = polygon(
        [
            (lx / 2, -ly / 2),
            (-lx / 2, -ly / 2),
            (-lx / 2, ly / 2),
            #
            (-lx / 2 + t, ly / 2),
            (-lx / 2 + t, -ly / 2 + t),
            (lx / 2, -ly / 2 + t),
        ]
    )
    return beam


@transform_region_decorator
@polygon_to_region_decorator
def beam_c(lx, ly, t):
    """Make a C-beam with bbox centered at (0,0)."""

    beam = polygon(
        [
            (lx / 2, -ly / 2),
            (-lx / 2, -ly / 2),
            (-lx / 2, ly / 2),
            (lx / 2, ly / 2),
            #
            (lx / 2, ly / 2 - t),
            (-lx / 2 + t, ly / 2 - t),
            (-lx / 2 + t, -ly / 2 + t),
            (lx / 2, -ly / 2 + t),
        ]
    )
    return beam


@transform_region_decorator
@polygon_to_region_decorator
def beam_t(lx, ly, t):
    """Make a T-beam with bbox centered at (0,0)."""

    beam = polygon(
        [
            (lx / 2, ly / 2),
            (-lx / 2, ly / 2),
            (-lx / 2, ly / 2 - t),
            (-t / 2, ly / 2 - t),
            (-t / 2, -ly / 2),
            #
            (t / 2, -ly / 2),
            (t / 2, ly / 2 - t),
            (lx / 2, ly / 2 - t),
        ]
    )
    return beam


@transform_region_decorator
@polygon_to_region_decorator
def beam_i(lx, ly, t):
    """Make an I-beam with bbox centered at (0,0)."""

    beam = polygon(
        [
            (lx / 2, ly / 2),
            (-lx / 2, ly / 2),
            (-lx / 2, ly / 2 - t),
            (-t / 2, ly / 2 - t),
            (-t / 2, -ly / 2 + t),
            (-lx / 2, -ly / 2 + t),
            (-lx / 2, -ly / 2),
            #
            (lx / 2, -ly / 2),
            (lx / 2, -ly / 2 + t),
            (t / 2, -ly / 2 + t),
            (t / 2, ly / 2 - t),
            (lx / 2, ly / 2 - t),
        ]
    )
    return beam
