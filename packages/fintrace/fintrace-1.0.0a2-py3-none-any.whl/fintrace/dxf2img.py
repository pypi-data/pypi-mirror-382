import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.properties import Properties, LayoutProperties
# import wx
import glob
import re

## Example
# convert = dxf2img.DXF2IMG()
# dxf2img.DXF2IMG.convert_dxf2img(convert, names=('file_name.dxf',))


class DXF2IMG(object):

    default_img_format = '.png'
    default_svg_format = '.svg'
    default_img_res = 300
    default_background = '#000000'
    def convert_dxf2img(self, names, img_format=default_img_format, img_res=default_img_res, background=default_background):
        for name in names:
            doc = ezdxf.readfile(name)
            msp = doc.modelspace()
            # Recommended: audit & repair DXF document before rendering
            auditor = doc.audit()
            # The auditor.errors attribute stores severe errors,
            # which *may* raise exceptions when rendering.
            if len(auditor.errors) != 0:
                raise Exception("The DXF document is damaged and can't be converted!")
            else :
                fig = plt.figure()
                ctx = RenderContext(doc)

                # Better control over the LayoutProperties used by the drawing frontend
                layout_properties = LayoutProperties.from_layout(msp)
                layout_properties.set_colors(bg=background)

                ax = fig.add_axes([0, 0, 1, 1])

                out = MatplotlibBackend(ax)

                Frontend(ctx, out).draw_layout(msp,layout_properties=layout_properties, finalize=True)

                img_name = re.findall("(\S+)\.",name)  # select the image name that is the same as the dxf file name
                first_param = ''.join(img_name) + img_format  #concatenate list and string
                fig.savefig(first_param, dpi=img_res)

    def convert_dxf2svg(self, names, svg_format=default_svg_format, img_res=default_img_res, background=default_background):
        for name in names:
            doc = ezdxf.readfile(name)
            msp = doc.modelspace()
            # Recommended: audit & repair DXF document before rendering
            auditor = doc.audit()
            # The auditor.errors attribute stores severe errors,
            # which *may* raise exceptions when rendering.
            if len(auditor.errors) != 0:
                raise Exception("The DXF document is damaged and can't be converted!")
            else :
                fig = plt.figure()
                ctx = RenderContext(doc)

                # Better control over the LayoutProperties used by the drawing frontend
                layout_properties = LayoutProperties.from_layout(msp)
                layout_properties.set_colors(bg=background)

                ax = fig.add_axes([0, 0, 1, 1])

                out = MatplotlibBackend(ax)

                Frontend(ctx, out).draw_layout(msp,layout_properties=layout_properties, finalize=True)

                img_name = re.findall("(\S+)\.",name)  # select the image name that is the same as the dxf file name
                first_param = ''.join(img_name) + svg_format  #concatenate list and string
                fig.savefig(first_param)

