# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


"""DLD-based sytem | Theme: Condenser-and-Sorter"""

import pprint

from mnflow.mfda.cad.components.element import Element
from mnflow.mfda.cad.dld.theme.multistage import DLD as DLD_Multistage


class DLD(DLD_Multistage):
    """A DLD system with a Condenser-and-Sorter theme."""

    def __init__(
        self,
        # internal config
        opt_collection_sideway=None,
        verbose=None,
        opt_process_upon_init=None,
        opt_write_upon_init=None,
        opt_save_image=None,
        top_cell_name=None,
        #
        *args,
        **kwargs,
    ):
        """
        **Constructor**

        Parameters
        ----------

        **Internal config**

        opt_collection_sideway : bool
            Whether to include sideway collection for ***sorters***, by
            default None
        verbose : bool, optional
            verbose, by default None
        opt_process_upon_init : bool, optional
            Whether to invoke the ``process`` method from inside the
            constructor to design the system, by default True
        opt_write_upon_init : bool, optional
            Whether to invoke the ``write`` method from inside the
            constructor to write the GDS/DXF layout file, by default None
        opt_save_image : bool, optional
            Whether to invoke the ``save_image`` method from inside the
            constructor to save layout as png file(s), by default None
        top_cell_name : str
            Name of top cell to be created as needed.
        """

        # --- default params
        if opt_collection_sideway is None:
            opt_collection_sideway = True
        if verbose is None:
            verbose = True
        if opt_process_upon_init is None:
            opt_process_upon_init = True
        if opt_write_upon_init is None:
            opt_write_upon_init = True
        if opt_save_image is None:
            opt_save_image = False
        if top_cell_name is None:
            top_cell_name = "Condenser-and-Sorter"

        # --- Constructors
        lst_param_Element = list(Element.__init__.__code__.co_varnames)
        lst_param_DLD_Multistage = list(
            DLD_Multistage.__init__.__code__.co_varnames
        )

        # --- Parent: DLD_Multistage | config without building, i.e., without
        # invoking ``process`` method
        _kwargs_DLD_Multistage = {
            "opt_process_upon_init": False,
            "verbose": verbose,
        }
        for key in lst_param_DLD_Multistage + lst_param_Element:
            if key in kwargs:
                _kwargs_DLD_Multistage[key] = kwargs.pop(key)
        DLD_Multistage.__init__(self, *args, **_kwargs_DLD_Multistage)

        # --- sanity check
        if len(kwargs) > 0:
            raise ValueError(f"Invalid parameter(s): {[key for key in kwargs]}")
        #####################

        # --- self attributes
        lst_param_to_set = DLD.__init__.__code__.co_varnames[
            1 : DLD.__init__.__code__.co_argcount
        ]
        lcl = locals()
        for _sn_key, key in enumerate(lst_param_to_set):
            setattr(self, key, lcl[key])

        # --- prep config
        DLD._prep_config(self)

        # --- Process
        if opt_process_upon_init:
            DLD.process(
                self,
                opt_write_upon_init=opt_write_upon_init,
                opt_save_image=opt_save_image,
            )

            # --- verbose
            if self.verbose:
                print("-" * 40)
                print(self)
                print("-" * 40)
                info_dic = DLD.get_die_info(
                    self,
                )
                pprint.pprint(info_dic)

    def get_die_info(self):
        """Returning the die information."""

        # parent class
        out_dict = super().get_die_info()
        area = out_dict["area"] * 1.0e-12
        area_mmsq = area * 1.0e6
        out_dict["die area (mm-sq)"] = area_mmsq

        return out_dict

    def __repr__(self):

        msg_parent = DLD_Multistage.__repr__(
            self,
        )
        msg = "condenser_sorter.DLD:"
        msg += f"\n{msg_parent}"

        return msg

    def _prep_config(
        self,
    ):
        config_stages_from_config = self.config_stages_from_config

        # --------------------------------------------------------------------
        # Ensure sorters (stages #2 and beyond) are mirrored
        #
        # Note:
        #   We only modify ``config_stages_from_config`` and not
        #   ``config_stages``, which has a higher priority. Therefore, if for
        #   whatever reason user wants to go with configs different from our
        #   standard ones adjusted below, they should be able to do so by
        #   including config of stages in ``config_stages`` explicitly.
        # --------------------------------------------------------------------

        # --- sideway collections
        if self.opt_collection_sideway:
            for sn_stage, stage_config in enumerate(config_stages_from_config):
                stage_config["opt_collection_sideway_left_side"] = sn_stage > 0

        # --- iterate on configs of sorters
        for sn_stage, stage_config in enumerate(config_stages_from_config[1:]):
            stage_config["opt_mirror_y"] = True

            # mirror collection sideway
            (
                opt_collection_sideway_left_side,
                opt_collection_sideway_right_side,
            ) = (False, False)
            if stage_config.get("opt_collection_sideway_left_side"):
                opt_collection_sideway_right_side = True

            if stage_config.get("opt_collection_sideway_right_side"):
                opt_collection_sideway_left_side = True

            # no action needed if both sides are with or without collection
            # sideway
            if (
                opt_collection_sideway_left_side
                is not opt_collection_sideway_right_side
            ):
                if opt_collection_sideway_left_side:
                    stage_config["opt_collection_sideway_left_side"] = True
                    stage_config["opt_collection_sideway_right_side"] = False
                if opt_collection_sideway_right_side:
                    stage_config["opt_collection_sideway_right_side"] = True
                    stage_config["opt_collection_sideway_left_side"] = False
