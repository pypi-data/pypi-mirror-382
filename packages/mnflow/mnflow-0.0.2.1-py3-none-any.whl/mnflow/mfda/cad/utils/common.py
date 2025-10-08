# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import copy
import os

import numpy as np

# ----------------------------------------------------------------------------
# common utils
# ----------------------------------------------------------------------------


def get_fname(fname_w_path, n=3):
    """
    gets a file/folder name and returns the same if does not exist.
    Otherwise, appends an `n`-digit identifier at the end of the name and
    returns the result.

    Parameters
    ----------
    fname_w_path : string
        (Path-included) Name of file/folder.
    n : int
        Number of digits of identifier to create a unique name in case
        file/folder already exists, by default 3
    """
    filename, extension = os.path.splitext(fname_w_path)
    counter = 0
    res = fname_w_path
    while os.path.exists(res):
        res = filename + "_" + f"{counter:0{n}d}" + extension
        counter += 1
    return res


def dist(p1, p2):
    """
    Gets two points and return their Euclidean distance.
    """
    p1 = np.array(p1).copy()
    p2 = np.array(p2).copy()
    assert (
        p1.shape == p2.shape
    ), f"""The provided points are not of the same shape:
{p1.shape} & {p2.shape}"""

    val = 0
    for sn in range(len(p1)):
        val += (p2[sn] - p1[sn]) ** 2
    val = np.sqrt(val)
    return val


def resist_channel(length, width, height, mu):
    """Resistance of a channel with rectangular cross section

    Parameters
    ----------
    length : float
        Length of channel
    width : float
        Width of channel
    height : float
        Height of channel
    mu : float
        Viscosity of fluid

    Returns
    -------
    float
        Resistance of channel
    """
    height, width = min(width, height), max(width, height)

    num_terms = 30
    fac = 0.0
    for sn_term in range(num_terms):
        n = 2.0 * sn_term + 1.0
        fac += (
            (1.0 / n**5.0)
            * (192.0 / np.pi**5.0)
            * height
            / width
            * np.tanh(n * np.pi * width / 2.0 / height)
        )
    fac = 1 - fac
    Resistance = 12.0 * mu * length / height**3 / width / fac

    return Resistance


def resist_dld(mu, Nw, length, height, diameter, pitch_w, pitch_a):
    """Get resistance of channel by using the model developed by Inglis et.
    al. [1]

    Ref.
    ----
    [1] https://doi.org/10.1007/s10404-020-2323-x
    """

    # fit params from paper
    a = 1.702
    b = 0.600
    c = 2.682
    d = 1.833

    D_over_W_valid_range = [0.3, 0.9]
    T_over_W_valid_range = [0.5, 4.5]

    # identifiers with same names as in paper
    T = height
    D = diameter
    W = pitch_w
    L = pitch_a

    D_over_W = D / W
    T_over_W = T / W

    if D_over_W < D_over_W_valid_range[0] or D_over_W > D_over_W_valid_range[1]:
        print(
            f"""(Resistance eval.) Warning:
D/W={D_over_W} while the valid range is {D_over_W_valid_range}"""
        )
    if T_over_W < T_over_W_valid_range[0] or T_over_W > T_over_W_valid_range[1]:
        print(
            f"""(Resistance eval.) Warning:
T/W={T_over_W} while the valid range is {T_over_W_valid_range}"""
        )

    # Resistance of one unit cell
    R_nondim = 1.0 + a * (b + np.tan(np.pi / 2.0 * D_over_W)) ** c * T_over_W**d
    R_ref = 12.0 * mu * L / W / T**3.0
    R = R_nondim * R_ref

    # Resistance of one fluidic lane
    nx = length / pitch_a
    R *= nx

    # Ressitance of Nw fluidic lanes
    R /= Nw

    return R


def vfr_SI_to_ul_per_min(vfr):
    """Convert volumetric flow rate from SI unit to micro-liter per min."""

    return vfr * 1e9 * 60.0


def vfr_SI_to_ml_per_hr(vfr):
    """Convert volumetric flow rate from SI unit to milli-liter per hour."""

    return vfr * 1e6 * 3600.0


def merge_two_dicts(
    dict_1,
    dict_2=None,
):
    """Merge two dictionaries: ``dict_2`` would override ``dict_1``."""

    dict_out = copy.deepcopy(dict_1)
    if dict_2 is not None:
        dict_out.update(dict_2)

    return dict_out


def first_not_none(lst):
    """Returns the index and value of first non-None item in a given list."""
    for index, val in enumerate(lst):
        if val is not None:
            return index, val

    # in case all elements are None
    return None, None


def last_not_none(lst):
    """Returns the index and value of last non-None item in a given list."""

    index, val = first_not_none(list(reversed(lst)))
    if index is not None:
        index = len(lst) - index - 1

    return index, val
