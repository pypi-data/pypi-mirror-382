# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


"""Test DLD"""

import numpy as np
from pytest import approx

from mnflow.mfda.cad.dld.theme.block import DLD as block_DLD


class Test_DLD:
    """A generic test class for DLD."""

    __test__ = False
    lst_test_var_core = [
        "Np",
        "Nw",
        "d_c",
        "gap_w",
        "pitch_w",
        "gap_a",
        "pitch_a",
        "height",
        "boundary_treatment",
    ]
    lst_test_var_block = [
        "num_unit",
        "opt_mirror",
        "array_counts",
        "opt_mirror_before_array",
    ]
    lst_test_var_die = [
        "bb",
    ]

    def __init__(
        self,
        dld,
        ground_truth,
    ):
        """
        **Constructor**
        """

        self.dld = dld
        self.ground_truth = ground_truth

        # --- different testsg
        self.test_core()
        self.test_block()
        self.test_die()

    def test_core(
        self,
    ):
        """Test at core-level."""

        for var in Test_DLD.lst_test_var_core:
            if var == "d_c":
                # a getter to be added for d_c in core.DLD to avoid this
                # if statement.
                val = self.dld.get_dc()
            else:
                val = getattr(self.dld, var)

            check = Test_DLD.compare(val, self.ground_truth[var])
            assert check, get_msg_fail(var, val, self.ground_truth[var])

    def test_block(
        self,
    ):
        """Test at block-level."""

        for var in Test_DLD.lst_test_var_block:
            val = getattr(self.dld, var)
            check = Test_DLD.compare(val, self.ground_truth[var])
            assert check, get_msg_fail(var, val, self.ground_truth[var])

    def test_die(
        self,
    ):
        """Test at die-level"""

        for var in Test_DLD.lst_test_var_die:
            if var == "bb":
                val = self.dld.get_die_info()["bb"]
            check = Test_DLD.compare(val, self.ground_truth[var])
            assert check, get_msg_fail(var, val, self.ground_truth[var])

    @staticmethod
    def compare(val, ground_truth, rel=1e-6, abs=1e-12):
        if type(ground_truth) in [str, int, bool]:
            return val == ground_truth
        elif type(ground_truth) in [float]:
            return val == approx(ground_truth, rel=rel, abs=abs)
        elif type(ground_truth) in [list, tuple] and type(val) in [list, tuple]:
            lst_check = []
            for sn_item, item in enumerate(val):
                lst_check.append(
                    Test_DLD.compare(val[sn_item], ground_truth[sn_item])
                )
            return np.all(lst_check)
        else:
            raise ValueError(
                f"""Invalid type of ``ground truth``
{ground_truth}: {type(ground_truth)}"""
            )


def get_block_DLD(*args, **kwargs):
    return block_DLD(*args, **kwargs)


def get_msg_fail(var, val, ground_truth):
    """Get a message for failed assert"""
    msg = f"""Check of variable {var} fails:
            {var}: {val}
            ground truth: {ground_truth}
            """

    return msg
