""" 
A module for drawing tools and functions.

"""
import numpy as np
from finesse.components import Mirror
from gtrace.beam import GaussianBeam
from gtrace.optcomp import Mirror as gMirror
from gtrace import optics
from gtrace.draw import draw, PolyLine, Circle, \
                        Line, Text, Arc, Rectangle, Canvas, Layer, \
                        Shape
from gtrace.optics import geometric
from .dxf2img import DXF2IMG


def drawDetectors(canvas, detector, gdict, layername):
    obj = gdict.get(detector)
    if type(obj) == Photodiode:
        for shape in drawPhotodiode(obj):
            canvas.add_shape(shape, layername)
    return

def drawAllDetectors(canvas, detectors, 
                     gdict: dict,
                     layername=None):
    for each_det in detectors:
        drawDetectors(canvas, each_det, 
                      gdict, layername)
    return

def checkGrid(gtrace_dict: dict):

    for name, comp in gtrace_dict.items():
        if type(comp).__name__ == 'Grid':
            return comp
    
    return None

def drawGrid(cnv: Canvas, grid: None, objects: dict):

    if grid != None:
        
        xbounds = grid.xlim
        ybounds = grid.ylim
        dyn_factor = max([float(xbounds[1])-float(xbounds[0]), 
                          float(ybounds[1])-float(ybounds[0])])
        xstep = grid.xstep if grid.xstep else dyn_factor/10
        ystep = grid.ystep if grid.ystep else dyn_factor/10

    else:

        max_x = 0
        min_x = 0
        max_y = 0
        min_y = 0
        i = 0
        for name, object in objects.items():
            
            if hasattr(object, 'HRcenter'):
                x, y = object.HRcenter
                offset = max([object.diameter, object.thickness])
                xs = [x-offset, x+offset]
                ys = [y -offset, y+offset]
            elif hasattr(object, 'x') and hasattr(object, 'y'):
                xs = object.x
                ys = object.y
                print(xs, ys)

            elif hasattr(object, 'point'):
                xs = [object.point[0]]
                ys = [object.point[1]]
            
            elif hasattr(object, 'center') and hasattr(object, 'radius'):
                xs = [object.center[0] + object.radius, 
                    object.center[0] - object.radius]
                ys = [object.center[1] + object.radius, 
                    object.center[1] - object.radius]
            else:
                xs = []
                ys = []

            for x in xs:
                if x > max_x:
                    max_x = x
                elif x < min_x:
                    min_x = x
            for y in ys:
                if y > max_y:
                    max_y = y
                elif y < min_y:
                    min_y = y
        
        dyn_factor = max([max_x-min_x, max_y-min_y])
        xstep = dyn_factor/10
        ystep = dyn_factor/10
        xbounds = [min_x*1.1, max_x*1.1]
        ybounds = [min_y*1.1, max_y*1.1]

    
    xnum = int(abs((xbounds[1]-xbounds[0])/xstep))+1
    ynum = int(abs((ybounds[1]-ybounds[0])/ystep))+1
    xticks = np.linspace(xbounds[0], xbounds[1], xnum, endpoint=True)
    yticks = np.linspace(ybounds[0],ybounds[1], ynum, endpoint=True)
    cnv.add_layer('grid', color = (255, 255, 255))

    xpos = xticks[0]
    start = (xpos, yticks[0])
    stop = (xpos, yticks[-1]*1.1)
    cnv.layers['grid'].add_shape(Line(start,stop, 
                                        thickness=dyn_factor/5000))
    label_pos = (start[0], start[1] - dyn_factor/100)
    label = Text(f"{xpos:.2f}", label_pos, height=dyn_factor/100)
    cnv.layers['grid'].add_shape(label)
    label_pos = (stop[0] - dyn_factor/25, stop[1])
    y_label = Text(f"y [m]", label_pos, height=dyn_factor/90)
    cnv.layers['grid'].add_shape(y_label)
    for i in range(1, len(xticks)):
        xpos = xticks[i]
        start = (xpos, yticks[0])
        stop = (xpos, yticks[-1])
        cnv.layers['grid'].add_shape(Line(start,stop, 
                                        thickness=dyn_factor/5000))
        label_pos = (start[0], start[1] - dyn_factor/80)
        label = Text(f"{xpos:.2f}", label_pos, height=dyn_factor/100)
        cnv.layers['grid'].add_shape(label)
    
    ypos = yticks[0]
    start = (xticks[0], ypos)
    stop = (xticks[-1]*1.1, ypos)
    cnv.layers['grid'].add_shape(Line(start,stop, 
                                        thickness=dyn_factor/5000))
    label_pos = (start[0] - dyn_factor/25, start[1])
    label = Text(f"{ypos:.2f}", label_pos, height=dyn_factor/100)
    cnv.layers['grid'].add_shape(label)
    label_pos = (stop[0], stop[1]  - dyn_factor/25)
    x_label = Text(f"x [m]", label_pos, height=dyn_factor/90)
    cnv.layers['grid'].add_shape(x_label)
    for j in range(1, len(yticks)):
        ypos = yticks[j]
        start = (xticks[0], ypos)
        stop = (xticks[-1], ypos)
        cnv.layers['grid'].add_shape(Line(start,stop, 
                                        thickness=dyn_factor/5000))
        label_pos = (start[0]- dyn_factor/24, start[1])
        label = Text(f"{ypos:.2f}", label_pos, height=dyn_factor/100)
        cnv.layers['grid'].add_shape(label)
    return

def drawAllShapes(cnv, shapes_to_plot):

    for each in shapes_to_plot:
        cnv.add_layer(each.name, color=each.color)
        cnv.add_shape(each, each.name)
    return

def make_shapes_list(gtrace_dict: dict) -> list:
    list_of_shapes = []
    shape_types = [PolyLine, Circle, Line, Text, Arc, Rectangle]
    for key, obj in gtrace_dict.items():
        if type(obj) in shape_types:
            list_of_shapes.append(obj)
        elif type(obj) == RotatedRect:
            for shape in drawRotatedRect(obj):
                list_of_shapes.append(shape)
        elif type(obj) == Hexagon:
            list_of_shapes.append(obj.draw())
        else:
            continue

    return list_of_shapes

def make_optics_list(gtrace_dict: dict, skip_optics = []) -> list:
    list_of_optics = []
    for key, obj in gtrace_dict.items():
        if type(obj) != gMirror:
            continue
        else:
            if key in skip_optics:
                continue
            else:
                list_of_optics.append(obj)
    return list_of_optics

def make_cavities_dict(finesse_cavs: dict, skip_optics = []) -> dict:

    cavs_to_plot = {}
    for key, value in finesse_cavs.items():
        add_to_cavs = True
        for optic in skip_optics:
            optic_in_comp = []
            for comp in value[1]:
                if optic in comp.name:
                    optic_in_comp.append(True)
                else:
                    optic_in_comp.append(False)
            if any(optic_in_comp):
                add_to_cavs = False
        #     print(key, optic, optic_in_comp)
        # print(key, add_to_cavs)
        if add_to_cavs:
            cavs_to_plot[key] = value



    return cavs_to_plot

def drawLaser(canvas, laserbeam, laser_width = .1, laser_length = .2, layer=None):

    plVect = optics.geometric.vector_rotation_2D(laserbeam.dirVect, np.pi/2)

    p1 = laserbeam.pos + plVect * laser_width/2
    p2 = p1 - plVect * laser_width

    p3 = p2 - laserbeam.dirVect * (laser_length)
    p4 = p1 - laserbeam.dirVect * (laser_length)

    canvas.add_shape(draw.Line(p2,p3), layername=layer)
    canvas.add_shape(draw.Line(p4,p1), layername=layer)
    canvas.add_shape(draw.Line(p1,p2), layername=layer)
    canvas.add_shape(draw.Line(p3,p4), layername=layer)

    center = (p1+p2+p3+p4)/4.
    height = laser_length/10.
    width = height*len(laserbeam.name)
    center = center + np.array([-width/2, -height/2])
    canvas.add_shape(draw.Text(text=laserbeam.name, point=center,height=height,
                               rotation=(laserbeam.dirAngle*1.0)%np.pi/2),
                    layername="text")
    
    return

def getBeam(i, beam, mirror, path, prev_mirror, beamDict):
    # print(mirror[0].name, mirror[1], i, len(path))

    if mirror[1] == 'HR' and i+1 < len(path) and \
        path[i+1][0].name != mirror[0].name:
        beam = mirror[0].hitFromHR(beam, order=2, verbose=True)
        beamDict[f"{prev_mirror[0].name}to{mirror[0].name}"] = \
                    beam['input']
        # print(beam)
        beam = beam['r1']
        # print(beam.dirAngle)
        # print('prompt bounce of hr', mirror[0].name)
        i += 1

    elif mirror[1] == 'HR' and i+2 < len(path) and \
        path[i+1][0].name == mirror[0].name and \
        path[i+2][0].name != mirror[0].name    :
        # print('transmit thru hr', mirror[0].name)
        beam = mirror[0].hitFromHR(beam, order=2, verbose=True)
        # print(beam)
        # print(mirror[0].Trans_HR, mirror[0].Trans_AR)
        beamDict[f"{prev_mirror[0].name}to{mirror[0].name}"] = \
                    beam['input']
        beam = beam['t1']
        i += 2

    elif 'AR' in mirror[1]  and i+2 < len(path) and \
        path[i+1][0].name == mirror[0].name and \
        path[i+2][0].name != mirror[0].name    :
        # print('transmit thru ar', mirror[0].name)
        beam = mirror[0].hitFromAR(beam, order=2, verbose=True)
        beamDict[f"{prev_mirror[0].name}to{mirror[0].name}"] = \
                    beam['input']
        beamDict[f"thru{mirror[0].name}"] = \
                    beam['s1']
        beam = beam['t1']
        i += 2

    elif 'AR' in mirror[1]  and i+2 == len(path) and \
        path[i+1][0].name == mirror[0].name    :
        # print('transmit thru ar but return internal beam', mirror[0].name)
        beam = mirror[0].hitFromAR(beam, order=2, verbose=True)
        beamDict[f"{prev_mirror[0].name}to{mirror[0].name}"] = \
                    beam['input']
        beamDict[f"thru{mirror[0].name}"] = \
                    beam['s1']
        beam = beam['t1']
        i += 2

    elif 'AR' in mirror[1] and i+2 < len(path) and \
        path[i+1][0].name == mirror[0].name and \
        path[i+2][0].name == mirror[0].name    :
        # print('2nd bounce off ar', mirror[0].name)
        gmirror: gMirror = mirror[0]
        beam = gmirror.hitFromAR(beam, order=2, threshold=0,
                                 verbose=True)
        # for key, value in beam.items():
        #     print(key, value.dirAngle*180/np.pi,
        #           value.pos)
        beamDict[f"{prev_mirror[0].name}to{mirror[0].name}"] = \
                    beam['input']
        beamDict[f"thru{mirror[0].name}"] = \
                    beam['s1']
        beam = beam['r2']
        i += 3

    

    else:
        # print(beam.pos, beam.dirAngle)
        # # beam.propagate(46.9)
        # print(beam.pos, beam.dirAngle)
        beam = mirror[0].hitFromHR(beam, order=2,verbose=True)
        # print(prev_mirror[0].name, prev_mirror[1], )
        beamDict[f"{prev_mirror[0].name}to{mirror[0].name}"] = \
                    beam['input']
        beam = beam['r1']
        i += 1
    # print()
    return beam, i, beamDict

def get_seq_beams(cavity, cavity_path_comps,
                  gtrace_optics):
    eigenmode = cavity.qx
    # print(eigenmode.q)
    if eigenmode == None:
        raise AttributeError(f"Cavity {cavity.name} is unstable and has no eigenmode. \
                          gfactors {cavity.g}")
    else:
        eigenmode = eigenmode.q

    gtrace_path = []
    # print()
    # print(cavity.name)
    traversed = []
    breakout = False
    linear = False
    for i in range(1, len(cavity_path_comps)):
        if breakout:
            break
        comp = cavity_path_comps[i]
        
        if 'to' in comp.name: # skip spaces
            continue
        if ('substrate' in comp.name) :
            # in_AR_of = comp.name.split('_')[0]
            # print(comp.name)
            continue
        for goptic in gtrace_optics:
            if breakout:
                break
            if goptic.name == cavity_path_comps[i].name.split('_')[0]:
                
                side = cavity_path_comps[i].name.split('_')[1]
                if side == 'front' or side == 'HR':
                    side = 'HR'
                elif side == 'back':
                    side = 'AR'
                else:
                    side = side
                # print(goptic.name, traversed)
                name_side = goptic.name.split('_')[0] \
                                     + " " + side
                if not name_side in traversed:
                    gtrace_path.append([goptic, side, 
                                        type(cavity_path_comps[i])])
                    traversed.append(goptic.name.split('_')[0] \
                                     + " " + side)
                else:
                    linear = True
                    breakout = True
        

        # print(comp.name)
    i = -1
    for goptic in gtrace_optics:
        if goptic.name == cavity_path_comps[i].name.split('_')[0]:
            
            side = cavity_path_comps[i].name.split('_')[1]
            if side == 'front' or side == 'HR':
                side = 'HR'
            else:
                side = side
            # print(goptic.name, traversed)
            name_side = goptic.name.split('_')[0] \
                                    + " " + side
            if not name_side in traversed:
                gtrace_path.insert(0, [goptic, side, 
                                    type(cavity_path_comps[i])])
                traversed.insert(0, goptic.name.split('_')[0] \
                                    + " " + side)

    # print()
    # for each in gtrace_path:
        # print(each[0].name, each[1])
    if not linear:
        first_goptic, second_goptic = gtrace_path[-1], gtrace_path[0]
    
        start = first_goptic[0].HRcenter
        if second_goptic[1] == 'HR':
            second = second_goptic[0].HRcenter
        else:
            second = second_goptic[0].HRcenter - \
                        second_goptic[0].normVectHR * \
                        second_goptic[0].thickness
        dirVect = list(second - start)
            
        
    else:
        first_goptic: gMirror = gtrace_path[0][0]
        second_goptic: gMirror = gtrace_path[1][0]
        # print(first_goptic.name, second_goptic.name)
        # print(gtrace_path[0][1], gtrace_path[1][1])
        # second_goptic.normAngleAR
        start = first_goptic.HRcenter
        if gtrace_path[0][1] == 'HR':
            if first_goptic.aoi == 0 and \
                second_goptic.name != first_goptic.name:
                dirVect = list(first_goptic.normVectHR)
            elif first_goptic.aoi == 0 and \
                second_goptic.name == first_goptic.name:
                dirVect = list(-1*first_goptic.normVectHR)
                gtrace_path.insert(0, gtrace_path[0])
            else:
                first = first_goptic.HRcenter
                if gtrace_path[1][1] == 'HR':
                    second = second_goptic.HRcenter
                else:
                    second = second_goptic.HRcenter - \
                            second_goptic.normVectHR * \
                            second_goptic.thickness
                dirVect = list(second-first)

        else:
            if first_goptic.aoi == 0:
                dirVect = list(first_goptic.normVectAR)
            else:
                first = first_goptic.HRcenter
                if gtrace_path[1][1] == 'HR':
                    second = second_goptic.HRcenter
                else:
                    second = second_goptic.HRcenter - \
                            second_goptic.normVectHR * \
                            second_goptic.thickness
                dirVect = list(second-first)
        
        gtrace_path.pop(0)

    beamDict = {}
    beam = GaussianBeam(eigenmode,
                        pos=start,
                        dirVect=dirVect,
                        layer='main_beam')
    # print(beam.pos, beam.dirAngle)

    i = 0
    while i < len(gtrace_path):
        # print(i)

        prev_mirror = gtrace_path[i-1]
        mirror = gtrace_path[i]
        gmirror: gMirror = mirror[0]
        # print(gmirror.name, beam.dirAngle*180/np.pi)
        beam, i, beamDict = getBeam(i, beam, mirror, gtrace_path, 
                          prev_mirror, beamDict)
        
    return list(beamDict.values())


class Grid(Shape):

    def __init__(self, xlim, ylim, xstep = None, ystep = None):
        
        self.xlim = [float(xlim[0]), float(xlim[1])]
        self.ylim = [float(ylim[0]), float(ylim[1])]
        self.xstep = xstep
        self.ystep = ystep

        return
    
class RotatedRect(Shape):
    '''
    A rotated rectangle
    '''
    
    def __init__(self, point, width, height, name, color = (0, 0, 0),
                 thickness=0,
                 normAngle=0):
        '''
        = Arguments =
        point: lower left corner of the rectangle
        width:
        height:
        '''
        super(RotatedRect, self).__init__()
        self.point = point
        self.width = width
        self.height = height
        self.thickness = thickness
        self.normAngle = normAngle
        self.name = name
        self.color = color

def drawRotatedRect(optic):
    
    if type(optic) != RotatedRect:
        raise TypeError()

    angle = optic.normAngle * np.pi/180
    vect = np.array([np.cos(angle), np.sin(angle)])
    perp = geometric.vector_rotation_2D(vect, np.pi/2)

    p1 = optic.point + vect * optic.width/2 + perp*optic.height/2
    p2 = p1 - vect * optic.height

    p3 = p2 - perp * (optic.width)
    p4 = p1 - perp * (optic.width)

    line1 = Line(p2,p3)
    line1.name = optic.name+"1"
    line1.color = optic.color

    line2 = Line(p4,p1)
    line2.name = optic.name+"2"
    line2.color = optic.color

    line3 = Line(p1,p2)
    line3.name = optic.name+"3"
    line3.color = optic.color

    line4 = Line(p3,p4)
    line4.name = optic.name+"4"
    line4.color = optic.color

    return [line1, line2, line3, line4]

class Photodiode(Shape):

    def __init__(self, point, normAngle, width = None, name="PD", thickness=.1):
        
        self.point = np.array([float(point['X']), float(point['Y'])])
        self.normAngle = normAngle
        self.width = width
        self.name = name
        self.thickness = thickness

        return

def drawPhotodiode(optic):
    angle = optic.normAngle
    vect = np.array([np.cos(angle), np.sin(angle)])
    perp = geometric.vector_rotation_2D(vect, np.pi/2)
    perp_angle = np.arctan2(perp[1],perp[0])

    p1 = optic.point - perp * optic.width/2
    p2 = optic.point + perp * optic.width/2

    line = Line(p1, p2, thickness=0)
    arc = Arc(optic.point, optic.width/2*.9,
              perp_angle, perp_angle+np.pi)
    
    center = optic.point
    height = optic.width/(1.2*len(optic.name))
    width = height*len(optic.name)
    center = center + 1.3*height*np.array([np.cos(perp_angle+np.pi), np.sin(perp_angle+np.pi)])
    text = Text(text=optic.name, point=center,height=height, rotation=perp_angle)

    return line, arc, text

class Hexagon(Shape):

    def __init__(self, center, normAngle, radius = 1, thickness=0,
                 name = None, color=None):
        
        self.center = center
        self.normAngle = normAngle * np.pi/180
        self.radius = radius
        self.thickness = thickness
        self.name = name
        self.color = color

        return
      
    def draw(self, ):

        xs, ys = [], []
        angle = self.normAngle
        for i in range(6):
            p1 = np.array(self.center) + \
                 self.radius*np.array([np.cos(angle), np.sin(angle)])
            angle += np.pi/3
            xs.append(p1[0])
            ys.append(p1[1])
        
        p1 = np.array(self.center) + \
                self.radius*np.array([np.cos(angle), np.sin(angle)])
        xs.append(p1[0])
        ys.append(p1[1])

        shapes = PolyLine(xs, ys, self.thickness)

        shapes.name = self.name
        shapes.color = self.color
        
        return shapes
