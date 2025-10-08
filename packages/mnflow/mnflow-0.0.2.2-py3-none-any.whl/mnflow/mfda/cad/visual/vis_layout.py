# ----------------------------------------------------------------------------
# Copyright (c) 2024 Aryan Mehboudi
# Licensed under the GNU Affero General Public License v3 or later (AGPLv3+).
# You should have received a copy of the License along with the code. If not,
# see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


import klayout.db as db
import klayout.lay as lay
import numpy as np
from PIL import Image

from mnflow.mfda.cad.utils.inspections import bbox


def save_all_images(
    img_fname_1,
    img_fname_2,
    img_fname_overlay,
    dpu,  # dot per micron
    frac=1,
    dims=None,
    fname_cad=None,
    offset=(0, 0),
    # save each image individually
    color_layer_1=0xFFFFFF,
    color_layer_2=0x0000CC,
    color_background=0x000000,
    # overlay
    opaque_alpha_level=250,
    # whether to mask values lower than threshold (``opaque_alpha_level``) or
    # above that.
    opt_mask_low_vals=True,
    # opt
    opt_show_layer_1=False,
    opt_show_layer_2=False,
    opt_show_overlay=False,
    allow_large_overlay_image=False,
):
    """Save images of layout: layer 1 (fluidic channels), layer 2 (via), and
    overlay"""
    save_img(
        fname_cad=fname_cad,
        layer="1/0",
        color=color_layer_1,
        color_background=color_background,
        frac=frac,
        dpu=dpu,
        out_file=img_fname_1,
        dims=dims,
        offset=offset,
        opt_show=opt_show_layer_1,
    )
    save_img(
        fname_cad=fname_cad,
        layer="2/0",
        color=color_layer_2,
        color_background=color_background,
        frac=frac,
        dpu=dpu,
        out_file=img_fname_2,
        dims=dims,
        offset=offset,
        opt_show=opt_show_layer_2,
    )
    overlay_img(
        img_foreground=img_fname_1,
        img_background=img_fname_2,
        img_fname_overlay=img_fname_overlay,
        opaque_alpha_level=opaque_alpha_level,
        opt_mask_low_vals=opt_mask_low_vals,
        opt_show=opt_show_overlay,
        allow_large_overlay_image=allow_large_overlay_image,
    )


def overlay_img(
    img_foreground="./out_1.png",
    img_background="./out_2.png",
    img_fname_overlay="res.png",
    threshold_background_RGB=[100, 100, 100],
    opaque_alpha_level=250,
    opt_mask_low_vals=True,
    opt_show=False,
    allow_large_overlay_image=False,
):
    """Overlaying of two images.

    In this application, background is the layout of device (layer 1),
    and forground is the layout of vias (layer 2).

    background (to be read): img_background
    forground (to be read): img_foreground
    overlay (to be saved): img_fname_overlay
    """

    # adjust as needed to handle large images
    if allow_large_overlay_image:
        Image.MAX_IMAGE_PIXELS = int(1e9)

    # image
    # img_2 = cv2.imread(img_foreground)
    img_2 = np.array(Image.open(img_foreground))
    img_2rgba = np.dstack(
        (img_2, 255 * np.ones((img_2.shape[0], img_2.shape[1])))
    )

    # ------------------------------------------------------------
    # adj transparency:
    #   background to be set as fully transparent (alpha=1000)
    #   features to be set as partially transparent, e.g., alpha=100
    #
    # Our images have only two RGB values; the code
    # does not need to be complex. Only first channel is checked
    # to detect the background. If the first channel is smaller than
    # threshold, that pixel is assumed to be black (background).
    # ------------------------------------------------------------
    if opt_mask_low_vals:
        img_2rgba[img_2rgba[:, :, 0] <= threshold_background_RGB[0], 3] = 0
        img_2rgba[img_2rgba[:, :, 0] > threshold_background_RGB[0], 3] = (
            opaque_alpha_level
        )
    else:
        img_2rgba[img_2rgba[:, :, 0] >= threshold_background_RGB[0], 3] = 0
        img_2rgba[img_2rgba[:, :, 0] < threshold_background_RGB[0], 3] = (
            opaque_alpha_level
        )

    # Reading foreground image via pillow
    img_2_p = Image.fromarray(img_2rgba.astype(np.uint8), mode="RGBA")

    # Pasting foreground image in the background image via pillow
    img_1 = Image.open(img_background)
    img_1.paste(img_2_p, (0, 0), img_2_p)
    img_1.save(img_fname_overlay)

    if opt_show:
        img_1.show()


def save_img(
    fname_cad,
    layer="1/0",
    color=0xFFFFFF,
    color_background=0x000000,  # "#000000"
    frac=1,
    dpu=10,
    offset=(0, 0),
    dims=None,
    out_file=None,
    opt_show=False,
):
    """Save image from layout.

    Note:
        Refer to the following for more information:
            - https://www.klayout.de/forum/discussion/2246/clip-gds-to-image
            - https://www.klayout.de/forum/discussion/1711/\
                screenshot-with-all-the-layer-and-screenshot-only-one-layer
            - https://stackoverflow.com/questions/23201134/\
                transparent-argb-hex-value
    """

    layout = db.Layout()
    layout.read(fname_cad)
    bb = bbox(layout)
    lx = bb[1][0] - bb[0][0]
    ly = bb[1][1] - bb[0][1]

    if dims is None:
        w = frac * lx * dpu
        h = frac * ly * dpu
        x1 = bb[0][0] + (1 - frac) / 2 * lx
        y1 = bb[0][1] + (1 - frac) / 2 * ly
        x2 = bb[0][0] + (1 + frac) / 2 * lx
        y2 = bb[0][1] + (1 + frac) / 2 * ly
    else:
        w = dims[0] * dpu
        h = dims[1] * dpu
        x1 = bb[0][0] + offset[0]
        y1 = bb[0][1] + offset[1]
        x2 = x1 + dims[0]
        y2 = y1 + dims[1]

    lv = lay.LayoutView()
    lv.set_config("background-color", color_background)
    lv.set_config("grid-visible", "false")
    lv.set_config("grid-show-ruler", "false")
    lv.set_config("text-visible", "false")
    lv.load_layout(fname_cad, 0)
    lv.clear_layers()

    # establish one layer, solid fill
    lp = lay.LayerProperties()
    lp.source = layer
    lp.dither_pattern = 0
    lp.fill_color = color
    lp.frame_color = color
    lv.insert_layer(lv.begin_layers(), lp)

    lv.max_hier()

    # Important: event processing for delayed configuration events
    # Here: triggers refresh of the image properties
    lv.timer()

    if out_file is not None:
        lv.save_image_with_options(
            out_file,
            w,
            h,
            0,
            0,
            0,
            db.DBox(x1, y1, x2, y2),
            False,
        )

    # show image
    if opt_show:
        img = Image.open(out_file)
        img.show()
