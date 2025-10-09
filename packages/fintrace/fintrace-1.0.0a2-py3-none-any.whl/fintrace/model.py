"""
This module creates the Fintrace model, which inherits
all attributes and methods of a finesse model
while populating a dictionary with gtrace objects
for ray-tracing and rendering.
"""
import numpy as np
import matplotlib.pyplot as plt
import yaml, os, prettytable

from finesse import Model, init_plotting
from finesse.tracing.tools import propagate_beam_astig,  propagate_beam
from finesse.solutions import AstigmaticPropagationSolution
from finesse.gaussian import transform_beam_param, BeamParam, HGMode
from cosmicexplorer.finesse.components import Laser, Lens, ThickBeamsplitter, Gauss, ThickMirror
from gtrace.optcomp import Mirror as gMirror
from gtrace.beam import GaussianBeam
from gtrace.draw import Circle, PolyLine, Text, Arc, Line, Rectangle
from gtrace.nonsequential import non_seq_trace
from gtrace.draw.tools import drawAllOptics, drawAllBeams
from gtrace.draw import renderer
from gtrace.optics import gaussian as gauss
from .utils import pop_beamsplitter, pop_mirror, \
                    pop_laser, pop_cavity,\
                    pop_pd, pop_lens
from .drawing import *
from engineering_notation import EngNumber

class FintraceModel(Model):

    def __init__(self):

        self.gtrace_dict = {}
        self.laser_beam = None
        self.laser_width = None
        self.laser_length = None
        self.laser_gauss = None
        self.yamlfile = ""
        super().__init__()
        return
    
    def __str__(self):

        """Prints current model info.
        """

        col_names = {
            'Detectors': ["Name", "Position (m)", "Omega (Hz)"],
            'Cavities': ["Name", "finesse", "FSR [Hz]", 
                         "FWHM [Hz]", "Gouy (deg)", "stability-m", "Loss", 
                         "f_p [Hz]", "RTL[m]", "\N{GREEK SMALL LETTER tau} [s]",
                          "TMS [Hz]", "w0 [m]", 
                         "z0 [m]"],
            'Components': ["Name", "Position [m]", "AOI [deg]", "diameter [m]",
                           "T", "L", "R", "R_AR", "\N{GREEK SMALL LETTER THETA} [deg]", "n",
                           "RoC [m]", "RoC_AR [m]", "thickness [m]",
                           "wedgeAngle [deg]"],
            'Laser': ['Name', 'Position[m]', 'P [W]', 'q [m]', '\N{GREEK SMALL LETTER THETA} [deg]',
                      "\N{GREEK SMALL LETTER LAMDA} [m]"]
        }

        # Do Laser first
        laser_table = prettytable.PrettyTable(col_names['Laser'])
        for name, comp in self.gtrace_dict.items():
            if type(comp) == GaussianBeam:
                name = comp.name
                pwr = comp.P
                normAngle = comp.dirAngle*180/np.pi 
                pos = comp.pos
                qx, qy = comp.qx, comp.qy
                laser_table.add_row([
                    name,
                    f"[{pos[0]:.3f} {pos[1]:.3f}]",
                    pwr,
                    f"[{qx:.2e}, {qy:.2e}]",
                    f"{normAngle:.3f}",
                    f"{comp.wl:.3e}"
                ])


        # Do Components next
        comps_table = prettytable.PrettyTable(col_names['Components'])
        for name, comp in self.gtrace_dict.items():
            if type(comp) == gMirror:
                for each in self.components:
                    if len(each.name.split('_')) > 1:
                        is_fin_equiv = each.name.split('_')[0] == name \
                                    and ( each.name.split('_')[1] == 'HR' or \
                                    each.name.split('_')[1] == 'front' )
                    else:
                        is_fin_equiv = each.name.split('_')[0] == name 

                    if is_fin_equiv:
                        fin_comp = getattr(self, name)
                        alpha = f"{float(fin_comp.alpha.value):.2f}" \
                                if isinstance(fin_comp, ThickBeamsplitter) else 0
                        if hasattr(fin_comp, 'Rcx'):
                            Rc = f"[{float(fin_comp.Rcx):.2e}, {float(fin_comp.Rcy):.2e}]"
                        elif hasattr(fin_comp, 'Rc'):
                            Rc = f"[{float(fin_comp.Rc):.2e}, {float(fin_comp.Rc):.2e}]"
                        else:
                            Rc = "[inf, inf]"
                        
                        if hasattr(fin_comp, 'Rc_AR'):
                            if type(fin_comp.Rc_AR) == np.ndarray:
                                RcAR = f"[{float(fin_comp.Rc_AR[0]):.2e}, {float(fin_comp.Rc_AR[1]):.2e}]"
                            else:
                                RcAR = f"[{float(fin_comp.Rc_AR):.2e}, {float(fin_comp.Rc_AR):.2e}]"
                        else:
                            RcAR = "[inf, inf]"

                        normAngle = f"{comp.normAngleHR*180/np.pi:.2f}"
                        pos = f"[{comp.HRcenter[0]:.2f}, {comp.HRcenter[1]:.2f}]"
                        wedge = f"{comp.wedgeAngle*180/np.pi:.2f}"
                        L = float(fin_comp.L) if hasattr(fin_comp, "L") else 0.0
                        R = np.round(comp.Refl_HR,4)
                        comps_table.add_row([
                            comp.name, pos, alpha,
                            comp.diameter, f"{comp.Trans_HR:.2e}", L, 
                            R, comp.Refl_AR, normAngle,
                            comp.n, 
                            Rc, RcAR, comp.thickness, 
                            wedge]
                        )

        # Do cavities next
        cavs_table = prettytable.PrettyTable(col_names['Cavities'])
        
        for cav in self.cavities:
            # prop_cav_vals = self.proper_cav_vals[cav.name]
            # print(prop_cav_vals)
            # print(f"{cav.name} ABCD matrices\n",cav.ABCD)
            finesse = f"{cav.finesse:.2f}"
            fsr = f"{cav.FSR:.2e}"
            fwhm = f"{cav.FWHM:.2e}"
            gouy = f"[{cav.gouy_x:.2f}," +\
                    f"{cav.gouy_y:.2f}]"
            g = f"[{cav.mx:.2f}, {cav.my:.2f}]"
            tms = f"[{cav.mode_separation[0]:.2e},"+\
                    f"{cav.mode_separation[1]:.2e}]"
            w0 = f"[{cav.w0[0]:.2e}, {cav.w0[1]:.2e}]"
            waistpos = f"[{cav.waistpos[0]:.2f}, {cav.waistpos[1]:.2f}]"
            cavs_table.add_row([
                cav.name, finesse,
                fsr, fwhm, gouy, g,
                f"{cav.loss:.2e}", f"{cav.pole:.2e}",
                f"{cav.round_trip_optical_length:.2e}",
                f"{cav.storage_time:.2e}", tms, 
                w0, waistpos]
            )

        
        # Do detectors next
        dets_table = prettytable.PrettyTable(col_names['Detectors'])
        
        for det in self.detectors:
            for name, comp in self.gtrace_dict.items():
                if type(comp) == Photodiode:
                    is_fin_equiv = det.name == name 
                    if is_fin_equiv:
                        fin_comp = comp
                        pos = f"[{fin_comp.point[0]:.3f}, {fin_comp.point[1]:.3f}]"
                        demod = f"{det.demod:.2e}" if hasattr(det, 'demod') \
                                    else None
                        dets_table.add_row([
                            det.name, pos, demod]
                        )


        s = ""
        s += "\n\033[3;32mLaser:\033[0m\n"
        s += str(laser_table) + "\n"
        s += "\n\033[3;32mComponents:\033[0m\n"
        s += str(comps_table) + "\n"
        s += "\n\033[3;32mCavities:\033[0m\n"
        s += str(cavs_table) + "\n"
        s += "\n\033[3;32mDetectors:\033[0m\n"
        s += str(dets_table) + "\n"
        return s

    def handle_shapes(self, shape, gtrace_dict):

        s = shape
        if s['Type'] == 'Circle':
            center = [s['Center']["X"], s['Center']["Y"]]
            cir = Circle(
                center=center,
                radius=s['Radius'],
                thickness=s['Thickness'] if 'Thickness' in s.keys() \
                    else .01,
            )
            
            cir.color = list(s['Color']) if 'Color' in s.keys() \
                else [255, 255, 255]
            cir.name = s['Name']
            gtrace_dict[cir.name] = cir

        elif s['Type'] == 'PolyLine':
            x = tuple(s['Points']['X'])
            y = tuple(s['Points']['Y'])
            thickness=s['Thickness'] if 'Thickness' in s.keys() \
                    else .01
            poly = PolyLine(x, y, thickness)
            poly.name = s['Name']
            poly.color = list(s['Color']) if 'Color' in s.keys() \
                else [255, 255, 255]
            
            gtrace_dict[poly.name] = poly

        elif s['Type'] == 'Line':
            start = tuple(s['Points']['X'][0],s['Points']['Y'][0])
            stop = tuple(s['Points']['X'][1],s['Points']['Y'][1])
            thickness=s['Thickness'] if 'Thickness' in s.keys() \
                    else .01
            line = Line(start, stop, thickness)
            line.name = s['Name']
            line.color = list(s['Color']) if 'Color' in s.keys() \
                else [255, 255, 255]
            
            gtrace_dict[line.name] = line
        
        elif s['Type'] == 'Arc':
            center = [s['Center']["X"], s['Center']["Y"]]
            radius = s['Radius']
            startangle = s['StartAngle']
            stopangle = s['StopAngle']
            thickness=s['Thickness'] if 'Thickness' in s.keys() \
                    else .01
            arc = Arc(center, radius, startangle, stopangle,
                        angle_in_rad=False, thickness=thickness)
            arc.name = s['Name']
            arc.color = list(s['Color']) if 'Color' in s.keys() \
                else [255, 255, 255]
            gtrace_dict[arc.name] = arc

        elif s['Type'] == 'Rectangle':
            center = [s['Center']["X"], s['Center']["Y"]]
            width = s['Width']
            height = s['Height']
            point = [float(center[0]) - width/2, float(center[1]) - height/2]
            thickness=s['Thickness'] if 'Thickness' in s.keys() \
                    else .01
            if 'normAngle' in s.keys():
                color = list(s['Color']) if 'Color' in s.keys() \
                    else [255, 255, 255]
                rect = RotatedRect(point, width, height,
                                    s['Name'],color,
                                    thickness=thickness,
                                    normAngle=s['normAngle'])
            else:
            
                rect = Rectangle(point, width, height,
                                thickness=thickness)
                rect.name = s['Name']
                rect.color = list(s['Color']) if 'Color' in s.keys() \
                    else [255, 255, 255]
            gtrace_dict[rect.name] = rect

        elif s['Type'] == 'Text':
            tt = s['Text']
            point = [s['Center']["X"], s['Center']["Y"]]
            height = s['Height'] if 'Height' in s.keys() \
                        else .05
            rotation = s['Rotation'] if 'Rotation' in s.keys() \
                        else 1
            
            text = Text(tt, point, height, rotation,
                        angle_in_rad=False)
            text.name = s['Name']
            text.color = list(s['Color']) if 'Color' in s.keys() \
                else [255, 255, 255]
            gtrace_dict[text.name] = text

        elif s['Type'] == 'Grid':
            xlim = s['Xlim']
            ylim = s['Ylim']
            xstep = s['Xstep'] if 'Xstep' in s.keys() \
                    else None
            ystep = s['Ystep'] if 'Ystep' in s.keys() \
                    else None
            grid = Grid(xlim, ylim, xstep, ystep)
            grid.name = s['Name']
            gtrace_dict[grid.name] = grid

        if s['Type'] == 'Hexagon':
            center = [s['Center']["X"], s['Center']["Y"]]
            hex = Hexagon(
                center=center,
                radius=s['Radius'],
                normAngle=s['normAngle'] if 'normAngle' in s.keys() \
                    else 0,
                thickness=s['Thickness'] if 'Thickness' in s.keys() \
                    else .01,
                color=list(s['Color']) if 'Color' in s.keys() \
                else [255, 255, 255],
                name=s['Name']
            )
            
            gtrace_dict[hex.name] = hex

        return gtrace_dict

    def build_from_yaml(self, yamlfile, 
                        gtrace = None,
                        verbose = False):
        
        "Builds a finesse model from input yamlfile."

        self.yamlfile = yamlfile
        shape_types = ['Circle', 'PolyLine', 'Line', 'Arc', 'Rectangle', 'Text', 'Grid', 'Hexagon']
        components_to_add = []
        cavities_to_add = []
        shapes_to_add = []
        detectors_to_add = []

        with open(yamlfile, 'r') as file:

            param_dict = yaml.safe_load(file)

            graph = {}

            for name, component in param_dict.items():
                if name.lower() == 'define':
                    continue

                if 'Type' not in component.keys():
                    raise KeyError("Must have Type declared.")

                if component['Type'] == 'Beamsplitter':
                    finesse_comp, graph = pop_beamsplitter(name,
                                                    component,
                                                    graph,
                                                    param_dict)
                    components_to_add.append(finesse_comp)

                elif component['Type'] == 'Mirror':
                    finesse_comp, graph = pop_mirror(name,
                                            component,
                                            graph,
                                            param_dict)
                    components_to_add.append(finesse_comp)
                
                elif component['Type'] == 'Lens':
                    finesse_comp, graph = pop_lens(name,
                                            component,
                                            graph,
                                            param_dict)
                    components_to_add.append(finesse_comp)
                
                elif component['Type'] == 'Laser':
                    finesse_comp, graph = pop_laser(name,
                                            component,
                                            graph,
                                            param_dict)
                    components_to_add.append(finesse_comp)
                
                elif component['Type'] == 'Photodiode':
                    detectors_to_add.append(name)
                    continue

                elif component['Type'] == 'Cavity':
                    cavities_to_add.append(name)
                    continue

                elif component['Type'] in shape_types:
                    component['Name'] = name
                    shapes_to_add.append(component)
                else:
                    raise TypeError(f"""Type {component['Type']}
                                    not found or unaccepted.""")
                
        
        for each in components_to_add:
            self.add(each)

        # set lambda0 first! 
        for m in components_to_add:
            if isinstance(m, Laser):
                wl = getattr(m, 'lamb', 1064e-9)
                self.lambda0 = wl

        for path, length in graph.items():
            ports = path.split('_to_')
            optic1, optic2 = ports[0].split('_')[0], ports[1].split('_')[0]
            port1, port2 = ports[0].split('_')[1], ports[1].split('_')[1]

            for each in components_to_add:
                
                if optic1 == each.name:
                    if port1 == 'Front':
                        connA = each.fr if hasattr(each, 'fr') else each.p1
                    elif port1 == 'Front1':
                        connA = each.fr1
                    elif port1 == 'Front2':
                        connA = each.fr2
                    elif port1 == 'Back':
                        connA = each.bk if hasattr(each, 'bk') else each.p2
                    elif port1 == 'Back2':
                        connA = each.bk2
                    elif port1 == 'Back1':
                        connA = each.bk1
                if optic2 == each.name:
                    if port2 == 'Front':
                        connB = each.fr if hasattr(each, 'fr') else each.p1
                    elif port2 == 'Front1':
                        connB = each.fr1
                    elif port2 == 'Front2':
                        connB = each.fr2
                    elif port2 == 'Back':
                        connB = each.bk if hasattr(each, 'bk') else each.p2
                    elif port2 == 'Back2':
                        connB = each.bk2
                    elif port2 == 'Back1':
                        connB = each.bk1
            self.connect(connA, connB, length, name=path)
        
        detectors = {}
        if len(detectors_to_add) > 0:
            for det in detectors_to_add:
                detector = pop_pd(det, param_dict,
                                  self.components, self)
                self.add(detector)
                detectors[detector.name] = detector

        cavities = {}
        if len(cavities_to_add) > 0:
            for each_cav in cavities_to_add:
                cavity = pop_cavity(each_cav,param_dict[each_cav],
                                    self.components, self)
                cavities[cavity.name] = [cavity, cavity.path.components]
        
        if gtrace:
            gtrace_dict = {}

            for m in components_to_add:
                if (type(m) == Laser):
                    wl = getattr(m, 'lamb', 1064e-9)
                    self.lambda0 = wl
                    if hasattr(m, 'q0'):
                        if type(m.q0) == dict:
                            q0x, q0y = self.calculate_matched_mode(m, m.q0['TBD'])
                        else:
                            if isinstance(m.q0, list):
                                q0x, q0y = m.q0
                            else:
                                q0x = m.q0
                                q0y = m.q0
                    else:
                        q0x = gauss.Rw2q(np.inf, 3e-3, wl)
                        q0y = gauss.Rw2q(np.inf, 3e-3, wl)
                        
                     
                    gtrace_dict[m.name] = GaussianBeam(
                        q0x=q0x,
                        q0y=q0y,
                        pos=m.position,
                        dirAngle=m.normAngle*np.pi/180,
                        name=m.name,
                        P=m.P,
                        wl = wl
                    )
                    self.laser_beam = gtrace_dict[m.name]
                    self.laser_width = getattr(m, 'Width', 0.1)
                    self.laser_length = getattr(m, 'Length', 0.2)
                    self.laser_gauss = Gauss(m.name+"Beam", m.fr.o,
                                   qx=q0x, qy=q0y)
                    self.add(self.laser_gauss)
                    continue
                elif (type(m) == Lens):
                    focus = float(m.f)
                    nr = m.nr if hasattr(m, 'nr') else 1.45
                    trans_hr = getattr(m, 'T', 1)
                    refl_hr = getattr(m, 'R', 0)
                    goptic = gMirror(
                        name=m.name,
                        HRcenter=m.position,
                        normAngleHR=m.normAngle*np.pi/180,
                        diameter=m.diameter if hasattr(m, 'diameter') else .05,
                        thickness=5e-5, # 5mm thickness for thin lens
                        inv_ROC_HR=1/(-2*focus*(nr-1)),
                        inv_ROC_AR=1/(-2*focus*(nr-1)),
                        Refl_HR=refl_hr,
                        Trans_HR=trans_hr,
                        Refl_AR=0,
                        Trans_AR=1,
                        wedgeAngle=m.wedge_angle*np.pi/180 if hasattr(m, 'wedge_angle') else 0,
                        n=nr,
                        HRtransmissive=False,
                    )
                else:
                    if hasattr(m, 'Rc_AR'):
                        if type(m.Rc_AR) == np.ndarray:
                            Rc_AR = float(m.Rc_AR[0])
                        else:
                            Rc_AR = float(m.Rc_AR)
                    else:
                        Rc_AR = None
                    
                    if hasattr(m, 'Rc'):
                        if type(m.Rc) == np.ndarray:
                            Rc = float(m.Rc[0])
                        else:
                            Rc = float(m.Rc)
                    else:
                        Rc = None
                    goptic = gMirror(
                        name=m.name,
                        HRcenter=m.position,
                        normAngleHR=m.normAngle*np.pi/180,
                        diameter=m.diameter if hasattr(m, 'diameter') else .05,
                        thickness=m.thickness,
                        inv_ROC_HR=1/Rc if Rc else 0,
                        inv_ROC_AR=-1/Rc_AR if Rc_AR else 0,
                        Refl_HR=m.R,
                        Trans_HR=1-m.R-m.L,
                        Refl_AR=m.R_AR,
                        Trans_AR=1-m.R_AR,
                        wedgeAngle=m.wedge_angle*np.pi/180 if (hasattr(m, 'wedge_angle') and \
                                   m.wedge == 'horiz') else 0,
                        n=m.nr
                    )
                if isinstance(m, ThickBeamsplitter):
                    goptic.aoi = float(m.alpha.value)
                else:
                    goptic.aoi = 0.0

                gtrace_dict[m.name] = goptic
            
            for s in shapes_to_add:

                gtrace_dict = self.handle_shapes(s, gtrace_dict)
                
            for det in detectors_to_add:
                detect = detectors[det]
                gdetector = Photodiode(detect.position,
                                       detect.normAngle,
                                       width = detect.width if\
                                        hasattr(detect, 'width') \
                                        else .10,
                                       name=det,
                                       )
                gtrace_dict[det] = gdetector
            
            self.gtrace_dict = gtrace_dict
            if verbose:
                
                self.print_model_info()
                
            return gtrace_dict, cavities, detectors
        
        return

    def save_to_yaml(self, filename):
        
        raise NotImplementedError
        
        return
    
    def save_to_csv(self, filename):
        
        """Prints current model info.
        """

        col_names = {
            'Detectors': ["Name", "Position (m)", "Omega (Hz)"],
            'Cavities': ["Name", "finesse", "FSR [Hz]", 
                         "FWHM [Hz]", "Gouy (deg)", "stability-m", "Loss", 
                         "f_p [Hz]", "RTL[m]", "\N{GREEK SMALL LETTER tau} [s]",
                          "TMS [Hz]", "w0 [m]", 
                         "z0 [m]"],
            'Components': ["Name", "Position [m]", "AOI [deg]", "diameter [m]",
                           "T", "L", "R", "R_AR", "\N{GREEK SMALL LETTER THETA} [deg]", "n",
                           "RoC [m]", "RoC_AR [m]", "thickness [m]",
                           "wedgeAngle [deg]", "beamsize"],
            'Laser': ['Name', 'Position[m]', 'P [W]', 'q [m]', '\N{GREEK SMALL LETTER THETA} [deg]',
                      "\N{GREEK SMALL LETTER LAMDA} [m]"]
        }

        # Do Laser first
        laser_table = prettytable.PrettyTable(col_names['Laser'])
        for name, comp in self.gtrace_dict.items():
            if type(comp) == GaussianBeam:
                name = comp.name
                pwr = comp.P
                normAngle = comp.dirAngle*180/np.pi 
                pos = comp.pos
                qx, qy = comp.qx, comp.qy
                laser_table.add_row([
                    name,
                    f"[{pos[0]:.3f} {pos[1]:.3f}]",
                    pwr,
                    f"[{qx:.2e}, {qy:.2e}]",
                    f"{normAngle:.3f}",
                    f"{comp.wl:.3e}"
                ])


        # Do Components next
        comps_table = prettytable.PrettyTable(col_names['Components'])
        self.beam_trace()
        for name, comp in self.gtrace_dict.items():
            if type(comp) == gMirror:
                for each in self.components:
                    if len(each.name.split('_')) > 1:
                        is_fin_equiv = each.name.split('_')[0] == name \
                                    and ( each.name.split('_')[1] == 'HR' or \
                                    each.name.split('_')[1] == 'front' )
                    else:
                        is_fin_equiv = each.name.split('_')[0] == name 

                    if is_fin_equiv:
                        fin_comp = getattr(self, name)
                        alpha = f"{float(fin_comp.alpha.value):.2f}" \
                                if isinstance(fin_comp, ThickBeamsplitter) else 0
                        if hasattr(fin_comp, 'Rcx'):
                            Rc = f"[{float(fin_comp.Rcx):.2e}, {float(fin_comp.Rcy):.2e}]"
                        elif hasattr(fin_comp, 'Rc'):
                            Rc = f"[{float(fin_comp.Rc):.2e}, {float(fin_comp.Rc):.2e}]"
                        else:
                            Rc = "[inf, inf]"
                        
                        if hasattr(fin_comp, 'Rc_AR'):
                            if type(fin_comp.Rc_AR) == np.ndarray:
                                RcAR = f"[{float(fin_comp.Rc_AR[0]):.2e}, {float(fin_comp.Rc_AR[1]):.2e}]"
                            else:
                                RcAR = f"[{float(fin_comp.Rc_AR):.2e}, {float(fin_comp.Rc_AR):.2e}]"
                        else:
                            RcAR = "[inf, inf]"

                        normAngle = f"{comp.normAngleHR*180/np.pi:.2f}"
                        pos = f"[{comp.HRcenter[0]:.2f}, {comp.HRcenter[1]:.2f}]"
                        wedge = f"{comp.wedgeAngle*180/np.pi:.2f}"
                        L = float(fin_comp.L) if hasattr(fin_comp, "L") else 0.0
                        R = np.round(comp.Refl_HR,4)
                        if isinstance(fin_comp, ThickBeamsplitter):
                            w = f"{EngNumber(float(fin_comp.fr1.i.qx.w))}m, {str(EngNumber(float(fin_comp.fr1.i.qy.w)))}m"
                        elif isinstance(fin_comp, ThickMirror):
                            w = f"{EngNumber(float(fin_comp.fr.i.qx.w))}m, {str(EngNumber(float(fin_comp.fr.i.qy.w)))}m"
                        else:
                            w = ["-", "-"]
                        comps_table.add_row([
                            comp.name, pos, alpha,
                            comp.diameter, f"{comp.Trans_HR:.2e}", L, 
                            R, comp.Refl_AR, normAngle,
                            comp.n, 
                            Rc, RcAR, comp.thickness, 
                            wedge, w]
                        )

        # Do cavities next
        cavs_table = prettytable.PrettyTable(col_names['Cavities'])
        
        for cav in self.cavities:
            # prop_cav_vals = self.proper_cav_vals[cav.name]
            # print(prop_cav_vals)
            # print(f"{cav.name} ABCD matrices\n",cav.ABCD)
            finesse = f"{cav.finesse:.2f}"
            fsr = f"{cav.FSR:.2e}"
            fwhm = f"{cav.FWHM:.2e}"
            gouy = f"[{cav.gouy_x:.2f}," +\
                    f"{cav.gouy_y:.2f}]"
            g = f"[{cav.mx:.2f}, {cav.my:.2f}]"
            tms = f"[{cav.mode_separation[0]:.2e},"+\
                    f"{cav.mode_separation[1]:.2e}]"
            w0 = f"[{cav.w0[0]:.2e}, {cav.w0[1]:.2e}]"
            waistpos = f"[{cav.waistpos[0]:.2f}, {cav.waistpos[1]:.2f}]"
            cavs_table.add_row([
                cav.name, finesse,
                fsr, fwhm, gouy, g,
                f"{cav.loss:.2e}", f"{cav.pole:.2e}",
                f"{cav.round_trip_optical_length:.2e}",
                f"{cav.storage_time:.2e}", tms, 
                w0, waistpos]
            )

        
        # Do detectors next
        dets_table = prettytable.PrettyTable(col_names['Detectors'])
        
        for det in self.detectors:
            for name, comp in self.gtrace_dict.items():
                if type(comp) == Photodiode:
                    is_fin_equiv = det.name == name 
                    if is_fin_equiv:
                        fin_comp = comp
                        pos = f"[{fin_comp.point[0]:.3f}, {fin_comp.point[1]:.3f}]"
                        demod = f"{det.demod:.2e}" if hasattr(det, 'demod') \
                                    else None
                        dets_table.add_row([
                            det.name, pos, demod]
                        )


        laser_filename = filename+"_laser.csv"
        with open(laser_filename, 'w') as file:
            file.write(laser_table.get_csv_string())

        components_filename = filename+"_components.csv"
        with open(components_filename, 'w') as file:
            file.write(comps_table.get_csv_string())

        cavities_filename = filename+"_cavities.csv"
        with open(cavities_filename, 'w') as file:
            file.write(cavs_table.get_csv_string())

        detectors_filename = filename+"_detectors.csv"
        with open(detectors_filename, 'w') as file:
            file.write(dets_table.get_csv_string())
        
        return
    
    def print_model_info(self, ):

        print(self)
            
        return
    
    def gtrace_plot(self, gtrace_dict: dict,
                finesse_cavities: dict,
                finesse_detectors: list,
                render=True, beam_origin = 'laser',
                skip_optics = [],
                grid = False, draw_width=True,
                savefile = None, img_res=600,
                power_threshold=1e-3, 
                keep_dxf = False,
                keep_svg = False):
        """Plots the gtrace rendering of current finesse model.

        Args:
            gtrace_dict (dict): Dictionary with populated gtrace objects
                generated during model initialization.
            finesse_cavities (list): List of cavities to plot and analyze.
            finesse_detectors (list): List of detectors to draw.
            render (bool, optional): Whether or not to render the gtrace
                model upon completion, or just return the unrendered
                Canvas object. Defaults to True.
            beam_origin (str, optional): Whether to use laser as initial
                beam origin or to create a beam with calculated cavity
                eigenmodes. Defaults to 'laser'.
            grid (bool, optional): Whether or not to draw prewritten/
                dynamic grid. Defaults to False.
            draw_width (bool, optional): Whether or not to draw
                beamwidths throughout the rendering. Defaults to True.
            savefile (_type_, optional): Path to save rendered (if
                applicable) drawing, **without extensions!**. If none
                is provided, it will produce gtrace.png in your current
                working directory. Defaults to None.
            img_res (int, optional): Choice of image resolution. Defaults to 600.
            power_threshold (float, optional): Threshold to use in the
                nonsequential beamtrace, which plots all beams until a 
                beam falls below the set power threshold. Defaults to 1e-3.
            keep_dxf (bool, optional): Whether to save the originally 
                rendered dxf file. Defaults to False.
            keep_svg (bool, optional): Whether to save rendered svg file. 
                Defaults to False.

        Returns:
            Canvas: If render is set to false, will return populated 
                Canvas object for rendering.
        """
        
        cnv = draw.Canvas()
        beams = []

        if beam_origin == 'laser':
            
            if self.laser_beam != None:
                optics_to_plot = make_optics_list(gtrace_dict, skip_optics)
                    
                drawLaser(cnv, self.laser_beam, self.laser_width, self.laser_length, layer='laser')

                cnv.layers['laser'].color = (255, 255, 255)


            else:
                optics_to_plot = make_optics_list(gtrace_dict, skip_optics)
                dirVect = optics_to_plot[1].HRcenter - optics_to_plot[0].HRcenter
                laser = GaussianBeam(gauss.ROCandWtoQ(np.inf, 3e-3),
                                pos=optics_to_plot[0].HRcenter,
                                dirVect=list(dirVect),
                                length=.01
                                )

            beams.append(non_seq_trace(optics_to_plot[:],
                                src_beam=self.laser_beam,
                                order=10,
                                power_threshold=power_threshold,
                                open_beam_length=.1))

            # #Add a layer to the canvas
            cnv.add_layer("main_beam", color=(180,0,0))
            cnv.add_layer("main_beam_width", color=(180,0,0))

            #Draw all the beams in beamDict
            
            
        else:
            optics_to_plot = make_optics_list(gtrace_dict, skip_optics)
            cavities_to_plot = make_cavities_dict(finesse_cavities,
                                                  skip_optics)
            cnv.add_layer("main_beam", color=(180,0,0))
            cnv.add_layer("main_beam_width", color=(180,0,0))

            for each_cav in cavities_to_plot.keys():
                cavity, comps = cavities_to_plot[each_cav]
                beams.append(get_seq_beams(cavity, comps, optics_to_plot))
                
        #Draw grid
        if grid:
            grid = checkGrid(gtrace_dict)
            drawGrid(cnv, grid, gtrace_dict)

        #Draw beams
        for beam in beams:
            if draw_width:
                try:
                    drawAllBeams(cnv, beam, drawWidth=True, sigma=3.0, drawPower=False,
                                    drawROC=False, drawGouy=False, drawOptDist=False, layer='main_beam')
                except RuntimeError:
                    drawAllBeams(cnv, beam, drawWidth=False, sigma=3.0, drawPower=False,
                                        drawROC=False, drawGouy=False, drawOptDist=False, layer='main_beam')
            else:
                drawAllBeams(cnv, beam, drawWidth=False, sigma=3.0, drawPower=False,
                                        drawROC=False, drawGouy=False, drawOptDist=False, layer='main_beam')
                
        #Draw the mirrors
        cnv.add_layer("optics", color=(0,0,0))
        drawAllOptics(cnv, optics_to_plot, layer='optics')
        
        #Draw the shapes
        shapes_to_plot = make_shapes_list(gtrace_dict)
        drawAllShapes(cnv, shapes_to_plot)

        #Draw the detectors
        cnv.add_layer('detectors', color =(255,255,255))
        detectors_to_draw = []
        for each_det in finesse_detectors:
            if each_det not in skip_optics:
                detectors_to_draw.append(each_det)
        drawAllDetectors(cnv, detectors_to_draw, gtrace_dict,
                    layername='detectors')

        cnv.layers['Mirrors'].color = (255, 255, 255)
        cnv.layers['text'].color = (255, 255, 255)

        # put main_beam and beam_width at end of dict keys so drawn last
        mainbeam = cnv.layers['main_beam']
        beamwidth = cnv.layers['main_beam_width']
        del cnv.layers['main_beam']
        del cnv.layers['main_beam_width']
        cnv.layers['main_beam'] = mainbeam 
        cnv.layers['main_beam_width'] = beamwidth 

        #Save the result as a DXF file
        if type(savefile) == str:
            fname = savefile
            if not os.path.exists(os.path.dirname(os.path.abspath(fname))):
                    os.makedirs(os.path.dirname(fname))
        else:
            fname = os.curdir+'/gtrace'
        if render:
            renderer.renderDXF(cnv, fname+'.dxf')
            convert = DXF2IMG()

            convert.convert_dxf2img(((fname+'.dxf'),), img_res=img_res,
                                        background="#FFFFFF")
            if keep_svg:
                convert.convert_dxf2svg(((fname+'.dxf'),), img_res=img_res,
                                        background="#FFFFFF")
            if not keep_dxf:
                os.remove(fname+'.dxf')

        else:
            return cnv
        
        return 

    def trace_cavities(self,
                    cavity_traces: list = ['all'],
                    savepath = None,
                    q_at = None,
                    imshow = False,
                    show = False,
                    plot = ['all'],
                    direction = None,
                    astig_difference=True,
                    verbose = False) -> None:
        """Draws beam trace(s) of each cavity specified by args, that are
        also specified in the .yaml config file.

        Args:
            cavity_trace (list, optional): list of cavities you wish 
                to trace. Defaults to ['all'].
            savepath (str, optional): Path to where you'd
                like to save the figures produced. Defaults to None.
            q_at (str, optional): Node to print the q-parameter within an
                eigenmode.
            imshow (bool, optional): When true, will plot beam intensity
                at given q_at on image. Defaults to False.
            show (bool, optional): When true, will call `plt.show()`
                and bring up the figures of each plot. Defaults to False.

        Raises:
            KeyError: If cavity name listed is not found yamlfile.
        """
        cavities = {}
        init_plotting()
        for each in self.cavities:
            cavities[each.name] = each

        if len(cavity_traces) == 1 and cavity_traces[0] == 'all':

            cavities_to_trace = list(cavities.keys())
        else:
            cavities_to_trace = []
            for each_cav in cavity_traces:
                if each_cav not in cavities.keys():
                    raise KeyError(f"Cavity {each_cav} not found in yamlfile.")
                else:
                    cavities_to_trace.append(each_cav)
        
        if verbose:
            row_names = ['Name', 'q', 'w','RoC', 'w0']
            table = prettytable.PrettyTable(row_names)
            print(f"\n\033[32mEigenmodes:", end='')
            print("\033[0m")

        qs = []
        width=1 + astig_difference*1
        if plot == ['all']:
            plot = ['beamsize', 'gouy', 'curvature']
        for each_cav in cavities_to_trace:
            cavity = cavities[each_cav]
            path = cavity.path
            q = cavity.q
            sol_x = propagate_beam(path=cavity.path, q_in=q[0], direction='x')
            sol_y = propagate_beam(path=cavity.path, q_in=q[1], direction='y')

            sol = AstigmaticPropagationSolution(ps_x=sol_x, ps_y=sol_y, name=f"APS_{each_cav}")
            if not isinstance(plot, list):
                height = 1
                if plot in [True, 'all']:
                    height = 3
                    fig, axs = self.plot_beam_trace(sol, plot, direction=direction, 
                                                    astig_difference=astig_difference)
                
                elif plot is False:
                    return
                else:
                    fig, axs = self.plot_beam_trace(sol, plot, direction=direction, 
                                                    astig_difference=astig_difference)
            else:
                height = len(plot)
                fig, axs = self.plot_beam_trace(sol, *plot, direction=direction, 
                                    astig_difference=astig_difference)

            fig.set_size_inches(10*width, 4*height, forward=True)
            

            
            if verbose: 
                qx, qy = cavity.qx, cavity.qy
                q = f"[{np.real(qx.q):.2e}+{np.imag(qx.q):.2e}j, "
                q += f"{np.real(qy.q):.2e}+{np.imag(qy.q):.2e}j]"
                w = f"[{qx.w:.2e}, {qy.w:.2e}]"
                Rc = f"[{qx.Rc:.2e}, {qy.Rc:.2e}]"
                w0 = f"[{qx.w0:.2e}, {qy.w0:.2e}]"
                table.add_row([each_cav, q,
                               w, Rc, 
                               w0])
            if q_at != None:
                for each_node in q_at:
                    l = each_node.split('.')
                    comp = getattr(self, l[0])
                    port = getattr(comp, l[1])
                    node = getattr(port, l[2])
                    
                    if node in cavity.path.nodes:
                        sol = cavity.trace_beam()
                        
                        row_names = ['direction', 'q [m]', 'w [m]','RoC [m]', 'w0 [m]', 'Accum Gouy [deg]', 'Dist. from source [m]']
                        table1 = prettytable.PrettyTable(row_names)
                        s = f"\n\033[32mq at {each_node} in {cavity.name}:" + "\033[0m\n"
                        q = (sol.qx(at = node), sol.qy(at = node))
                        table.add_row(["x", f"{q[0].q.real:2e} + {q[0].q.imag:2e}j", 
                                   f"{q[0].w:.2e}", f"{q[0].Rc:.2e}", f"{q[0].w0:.2e}",
                                   f"{sol.ps_x.acc_gouy_up_to(node):.2f}",
                                   f"{sol.ps_x.position(node):.3f}"])
                        table.add_row(["y", f"{q[1].q.real:2e} + {q[1].q.imag:2e}j", 
                                   f"{q[1].w:.2e}", f"{q[1].Rc:.2e}", f"{q[1].w0:.2e}",
                                   f"{sol.ps_y.acc_gouy_up_to(node):.2f}",
                                   f"{sol.ps_y.position(node):.3f}"])
                        s += str(table1) + "\n"
                        qs.append(s)

                        if imshow:
                            w0x, w0y = q[0].w, q[1].w
                            x = np.linspace(-1,1,200)*np.max([w0x,w0y])*1.5
                            y = np.linspace(-1,1,200)*np.max([w0x,w0y])*1.5
                            beamint = np.abs(HGMode(q, 0, 0).unm(x, y)**2)

                            fig, axs = plt.subplots(1, 1, figsize = (10, 8))
                            axs.imshow(beamint.T, extent=(x.min()*1e3,x.max()*1e3,y.min()*1e3,y.max()*1e3))
                            axs.grid(True,color='white')
                            axs.set_xlabel('[mm]')
                            axs.set_ylabel('[mm]')
                            axs.set_title(f"Beam intensity profile\nat "+\
                                          f"{each_node} in {cavity.name}\n"+\
                                          f"qx={q[0].q:.2e}, qy={q[1].q:.2e}")
                            if savepath:
                                savepath = os.path.abspath(savepath)
                            else:
                                savepath = os.path.join(os.path.curdir, 'figures')
                            if not os.path.exists(savepath):
                                os.makedirs(savepath)
                            fig.savefig(os.path.join(savepath,each_cav+\
                                                     f"_{each_node}"+'_intprofile.png'))
                    else:
                        qs.append(Warning(f"Warning: Node {each_node} not in {cavity.name} cavity path."))

            
            # pargs = pargs
            # # print(pargs)
            # kwargs = {'show': show}
            
            
            # fig, axs =  ps.plot(*pargs, **kwargs)
            # fig.set_size_inches(14, 8, forward=True)
            fig.suptitle(f"Beam-trace of {each_cav} cavity")

            if hasattr(axs, 'ndim') and axs.ndim == 1 \
                and direction == None:
                axs[0].legend(["x", "y"])
            elif hasattr(axs, 'ndim') and axs.ndim == 2 \
                and direction == None:
                axs[0, 0].legend(["x", "y"])
                axs[1, 0].legend(["x", "y"])

            if savepath:
                savepath = os.path.abspath(savepath)
            else:
                savepath = os.path.join(os.path.curdir, 'figures')
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            fig.savefig(os.path.join(savepath,each_cav+'_trace.png'))

        
        if verbose:
            print(table)
        for each in qs:
            print(each)
        return 

    def trace_beam(self,
                beamtrace: list,
                q_at = None,
                q_in = None,
                plot = False,
                imshow = False,
                show: bool = False,
                savepath: str = None,
                direction: str = 'both',
                astig_difference: bool = True,
                **kwargs) -> None:
        
        """Performs a beam trace from a given starting point 
        and end point. The syntax for start and end nodes uses
        the finesse style. Can only have a start and end node no
        more, no less.

        Args:
            beamtrace (list): Start and end nodes, with optional via node.
                List should be a maximum of 3 nodes, minimum of 2.
            q_at (str, optional): Node to print the q-parameter within an
                optical path generated with beamtrace.
            q_in (complex, optional): initial q to use beam propagation 
                for beamtrace.
            plot (bool, optional): whether or not to plot the beam trace.
                Defaults to False.
            imshow (bool, optional): When true, will plot beam intensity
                at given q_at on image. Defaults to False.
            show (bool, optional): When true, will call `plt.show()`
                and bring up the figures of each plot. Defaults to False.
            savepath (str, optional): Path to where you'd
                like to save the figures produced. Defaults to None.

        Raises:
            ValueError: Must define a start and end node.
            AttributeError: The node does not have this port.
        """
        if plot == ['all']:
            plot = ['beamsize', 'gouy', 'curvature']

        init_plotting()
        if len(beamtrace) < 2:
            raise ValueError("Must define a start and end node. Via node optional.")
        if direction not in ['both', 'x', 'y']:
            raise ValueError(f"Must have a valid direction to trace ['both', 'x', 'y']."+
                             f"Found {direction}.")
        
        start = self
        for div in beamtrace[0].split('.'):
            if hasattr(start, div):
                start = getattr(start, div)
            else:
                if self == start:
                    raise AttributeError(f"Model does not have component {div}")
                else:
                    raise AttributeError(f"{start.name} does not have attr {div}")
        
        end = self
        for div in beamtrace[1].split('.'):
            if hasattr(end, div):
                end = getattr(end, div)
            else:
                raise AttributeError(f"{end.name} does not have attr {div}")

        if len(beamtrace) == 3:
            via = self
            for div in beamtrace[2].split('.'):
                if hasattr(via, div):
                    via = getattr(via, div)
                else:
                    raise AttributeError(f"{via.name} does not have attr {div}")
        else:
            via = None

        if q_in == None:
            qx_in, qy_in = self.laser_beam.qx, self.laser_beam.qy
        else:
            qx_in, qy_in = q_in, q_in

        sol = propagate_beam_astig(from_node=start, to_node=end, qx_in=qx_in,
                                   qy_in=qy_in, via_node=via)

        if q_at != None:
            for each_node in q_at:
                try:
                    l = each_node.split('.')
                    comp = getattr(self, l[0])
                    port = getattr(comp, l[1])
                    node = getattr(port, l[2])

                    row_names = ['direction', 'q [m]', 'w [m]','RoC [m]', 'w0 [m]', 'Accum Gouy [deg]',
                                 "Dist. form source [m]"]
                    table = prettytable.PrettyTable(row_names)
                    print(f"\n\033[32mq at {each_node} from BeamTrace:", end='')
                    print("\033[0m")
                    q = (sol.qx(at = node), sol.qy(at = node))
                    
                    table.add_row(["x", f"{q[0].q.real:2e} + {q[0].q.imag:2e}j", 
                                   f"{q[0].w:.2e}", f"{q[0].Rc:.2e}", f"{q[0].w0:.2e}",
                                   f"{sol.ps_x.acc_gouy_up_to(node):.2f}",
                                   f"{sol.ps_x.position(node):.3f}"])
                    table.add_row(["y", f"{q[1].q.real:2e} + {q[1].q.imag:2e}j", 
                                   f"{q[1].w:.2e}", f"{q[1].Rc:.2e}", f"{q[1].w0:.2e}",
                                   f"{sol.ps_y.acc_gouy_up_to(node):.2f}",
                                   f"{sol.ps_y.position(node):.3f}"])
                    print(table)
                except KeyError:
                    print("\033[91m", end='')
                    print(f"{each_node} not in beam-trace solution.")
                    print("\033[0m")

        width=1 + astig_difference*1

        if not isinstance(plot, list):
            height = 1
            if plot in [True, 'all']:
                height = 3
                fig, axs = self.plot_beam_trace(sol, plot, direction=direction, 
                                                astig_difference=astig_difference)
            
            elif plot is False:
                return
            else:
                fig, axs = self.plot_beam_trace(sol, plot, direction=direction, 
                                                astig_difference=astig_difference)
        else:
            height = len(plot)
            fig, axs = self.plot_beam_trace(sol, *plot, direction=direction, 
                                 astig_difference=astig_difference)

        fig.set_size_inches(10*width, 4*height, forward=True)

        if savepath:
            savepath = os.path.abspath(savepath)
        else:
            savepath = os.path.join(os.path.curdir, 'figures')
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        fig.suptitle(f"Beam-trace from {start.component.name} to {end.component.name}\n"+\
                        f"q_in = [{qx_in:.2e}, {qy_in:.2e}]")

        fig.savefig(os.path.join(savepath,f'beamtrace.png'))
        if show:
            plt.show()
        return
    
    def scan_cavity(self,
                    cavity_names: list = ['all'],
                    savepath = None,
                    show = False,
                    nm = 7,
                    yscale = 'linear'
                    ):
        """Scans the cavity for higher-order mode resonance, 
        normalizing each succesive HOM by 1/(n+m+1).

        Args:
            cavity_names (list, optional): List of cavities 
            you wish to scan. Defaults to ['all'].
            savepath (_type_, optional): Place to save produced plot. 
            Defaults to None.
            show (bool, optional): Whether or not to display plot. 
            Defaults to False.
            nm (int, optional): Total number of HOMs to include. 
            Defaults to 7.
        """
        import scipy.constants as scc
        init_plotting()

        cavities = {}
        figures = {}
        axes = {}
        for each in self.cavities:
            cavities[each.name] = each

        if len(cavity_names) == 1 and cavity_names[0] == 'all':

            cavities_to_scan = list(cavities.keys())
        else:
            cavities_to_scan = []
            for each_cav in cavity_names:
                if each_cav not in cavities.keys():
                    print(f"Warning: Cavity {each_cav} not found in yamlfile.")
                else:
                    cavities_to_scan.append(each_cav)
        for name in cavities_to_scan:
            figures[name] = {}
            axes[name] = {}
            cavity = getattr(self, name, None)
            if cavity == None:
                print("\033[91m", end='')
                print(f"Warning: {name} not in list of cavities in model.")
                print("\033[0m")

            phase = np.linspace(0*np.pi, 16*np.pi, 5000)
            freq = (scc.c*phase)/(cavity.round_trip_optical_length)/(2*np.pi) #Hz
            w = cavity.FWHM/2

            total_peaks = int((phase[-1]-phase[0])/(2*np.pi))
            freq2 = np.linspace(-total_peaks//2, total_peaks//2, len(freq))
            for pol in range(2):
                fig, axs = plt.subplots(1,1,figsize=(10,8))
                for dir in range(2):
                    powers = []
                    for i in range(nm+1):
                        fsrs = []
                        for j in range(-total_peaks//2, total_peaks//2+1):
                            f0 = (scc.c)/(cavity.round_trip_optical_length)*\
                                (total_peaks*np.pi/2)/(2*np.pi) + j*cavity.FSR + \
                                i * cavity.mode_separation[dir] \
                                + cavity.n_refls/2*(scc.c)/(cavity.round_trip_optical_length)*pol # for s polarization

                            fsr = w/((freq-f0)**2+w**2)
                            fsrs.append(fsr)
                        power_nm = np.sum(fsrs, 0)/np.pi/(i+1)
                        powers.append(power_nm)
                        
                        axs.plot(freq2, power_nm/max(powers[0]), 
                                label = f"n+m = {i}" if dir == 1 else None,
                                color = f"C{i+3}",
                                ls = "--" if dir == 0 else "-")

                    axs.plot(freq2, np.sum(powers, 0)/max(powers[0]), 
                            label = "Total" if dir == 1 else None,
                            color = 'black',
                            ls = "--" if dir == 0 else "-")
                axs.set_xlim([-1, 1])
                axs.set_xlabel(r"$\nu_0$: FSR = "+f"{cavity.FSR*1e-6:.2f} MHz"+\
                            f"\nTMS = [{cavity.mode_separation[0]*1e-6:.2f}" +\
                                f", {cavity.mode_separation[1]*1e-6:.2f}] MHz")
                axs.legend()
                title = f"{name} cavity scan\nx: dashed     y: solid"
                title += f"\n{'S' if pol else 'P'}-pol"
                fig.suptitle(title)
                if savepath:
                    savepath = os.path.abspath(savepath)
                else:
                    savepath = os.path.join(os.path.curdir, 'figures')
                if not os.path.exists(savepath):
                    os.makedirs(savepath)
                suffix = f"\n{'S' if pol else 'P'}-pol"
                figures[name]['S' if pol else 'P'] = fig
                axes[name]['S' if pol else 'P'] = axs
                # fig.savefig(os.path.join(savepath,f'{name}_cavityscan{suffix[1:]}.png'))
                if show:
                    plt.show()

        if isinstance(yscale, dict):
            print('is dict')
            for key, value in yscale.items():
                print(key, 'is dict')
                if isinstance(value, dict):
                    print(value, 'is dict')
                    for key1, value1 in value.items():
                        axes[key][key1].set_yscale(value1)
                        print(key1)
                else:
                    axes[key]['S'].set_yscale(value)
                    axes[key]['P'].set_yscale(value)
        else:
            for key, value in axes.items():
                for key1, value1 in value.items():
                    print(key, key1, value1)
                    axes[key][key1].set_yscale(yscale)
                    
        for key, value in figures.items():
                for key1, value1 in value.items():
                    figures[key][key1].savefig(os.path.join(savepath, 
                                                            f'{key}_cavityscan{key1}-pol.png'))

        return figures, axes
    
    def calculate_matched_mode(self, laser, cav: str):
        """Calculates the needed q-parameter for laser given a cavity to be
        matched to.

        Args:
            laser (Laser): Laser object, as a model object
            cav (str): Name of cavity to match to.

        Returns:
            (qx, qy): needed q parameters in x and y direction.
        """
        for cavity in self.cavities:
            if cav == cavity.name:
                qx, qy = cavity.qx, cavity.qy
                ABCDx, ABCDy = self.ABCD(laser.fr.o, cavity.source, direction='x'), \
                        self.ABCD(laser.fr.o, cavity.source, direction='y')
                
                q0x = transform_beam_param(np.linalg.inv(ABCDx.M), qx).q
                q0y = transform_beam_param(np.linalg.inv(ABCDy.M), qy).q

        laser.q0 = (q0x, q0y)
        return q0x, q0y

    def match_beam(self, target_q: BeamParam,
                   from_node, match_node,
                   start_q: BeamParam,
                   params, guess,
                   dir=None,):
        """Runs minimization function on mode mismatch with parameters set in arguments,
        which must be syntaxed the FINESSE way.

        Args:
            target_q (BeamParam): Target q that you are trying to mode match to.
            from_node (OpticalNode): OpticalNode to start beam propagation to.
            match_node (OpticalNode): OpticalNode to end at and evaluate mode match at.
            start_q (BeamParam): Initial q to start beam propagation with.
            params (list): List of parameters (FINESSE syntax) in minimization function.
            guess (list): List of initial guesses for parameters that give minima.
            dir (str): either 'x' or 'y' to use mode matching direction. default is 'x'.

        """
        from scipy.optimize import minimize
        print("Matching...")
        def min_mismatch(x, *args):
            self, params, yamlfile, from_node, match_node, start_q, target_q = args
            with open(yamlfile, 'r') as file:
                yaml_parameters = yaml.safe_load(file)
                for i in range(len(params)):
                    param = yaml_parameters
                    comp = self
                    keys = params[i].split('.')
                    for j in range(len(keys)-1):
                        param = param.get(keys[j])
                        comp = getattr(comp, keys[j])
                    param[keys[-1]] = float(x[i])
                    setattr(comp,  keys[-1], float(x[i]))
                    
            with open(yamlfile, 'w') as file:
                yaml.safe_dump(yaml_parameters, file)

            # self.print_model_info()
            sol = self.propagate_beam_astig(from_node=from_node, to_node=match_node, 
                                       qx_in=start_q[0],  qy_in=start_q[1])
            if dir == None or dir == 'x':
                mismatch = BeamParam.mismatch(sol.qx(at=match_node), target_q)
            elif dir == 'y':
                mismatch = BeamParam.mismatch(sol.qy(at=match_node), target_q)

            print("\rMismatch: " + str(mismatch), end='')
            return mismatch
        
        args = (self, params, self.yamlfile, from_node, match_node, start_q, target_q)
        sol = minimize(min_mismatch, guess, args, tol=1e-6)
        print()
        print(sol)
        return

    def plot_beam_trace(self, sol, *args, direction='both', astig_difference=True,
                        filename=None,
                        show=False,):
        
        valid_args = ("beamsize", "gouy", "curvature")
        if any(arg not in valid_args for arg in args):
            raise ValueError(
                "Invalid target argument in args, expected any "
                f"combination of {valid_args} or 'all'"
            )
        N = len(args)
        if astig_difference:
            fig, axs = plt.subplots(N, 2, sharex=True)

            if N == 1:
                axs = np.array([axs])

            maximums = {k: 0 for k in args}
            diff_mins = {k: 0 for k in args}

            data_x = sol.ps_x.all_segments(
                w_scale=1e3, npts=1000, resolution="equal", subs=None
            )
            data_y = sol.ps_y.all_segments(
                w_scale=1e3, npts=1000, resolution="equal", subs=None
            )
            first = True
            for (zs_x, segd_x), (zs_y, segd_y) in zip(data_x.values(), data_y.values()):
                for i, arg in enumerate(args):
                    vx = segd_x[arg]
                    vy = segd_y[arg]
                    if arg == "beamsize":
                        if direction == 'both':
                            if first:
                                axs[i][0].fill_between([], [], [], label="X", color="r", alpha=0.5)
                                axs[i][0].fill_between([], [], [], label="Y", color="b", alpha=0.5)
                                axs[i][0].legend()
                            axs[i][0].fill_between(zs_x, vx, -vx, color="r", alpha=0.5)
                            axs[i][0].fill_between(zs_y, vy, -vy, color="b", alpha=0.5)
                        elif direction == 'x':
                            axs[i][0].fill_between(zs_x, vx, -vx, color="r", alpha=1)
                        else:
                            axs[i][0].fill_between(zs_y, vy, -vy, color="b", alpha=.7)

                    else:
                        if direction == 'both':
                            if first:
                                axs[i][0].plot([], [], label="X", color="k")
                                axs[i][0].plot([], [], label="Y", ls='--', color="k")
                                axs[i][0].legend()
                            axs[i][0].plot(zs_x, vx)
                            axs[i][0].plot(zs_y, vy, linestyle="--",)
                        elif direction == 'x':
                            axs[i][0].plot(zs_x, vx)
                        else:
                            axs[i][0].plot(zs_y, vy,)

                    axs[i][1].plot(zs_x, vx - vy, color="k")
                    maximums[arg] = max(maximums[arg], vx.max(), vy.max())
                    diff_mins[arg] = min(diff_mins[arg], (vx - vy).min())
                first=False

            if direction == 'x':
                sub_sol = sol.ps_x
            else:
                sub_sol = sol.ps_y

            for node, info in sub_sol.node_info.items():
                if node.is_input:
                    z = sub_sol._eval_z_for_display(info, subs=None)

                    comp = node.component
                    if "AR" not in comp.name:
                        name = comp.name
                        x_offset = 0
                        y_offset = 0
                        # display the name in a nicer way
                        name = name.replace("_", "\n")
                        n_newlines = name.count("\n")

                        for i, arg in enumerate(args):
                            if not i:
                                for ax in axs[i]:
                                    ax.axvline(
                                        z,
                                        0.12 + 0.1 * n_newlines,
                                        color="k",
                                        linestyle="--",
                                    )

                                if arg == "beamsize":
                                    ytext_pos = [-1 * maximums[arg], diff_mins[arg]]
                                else:
                                    ytext_pos = [0, 0]

                                for ax, ytp in zip(axs[i], ytext_pos):
                                    ax.text(
                                        z + x_offset,
                                        ytp + y_offset,
                                        name,
                                        ha="center",
                                        va="center",
                                    )
                            else:
                                for ax in axs[i]:
                                    ax.axvline(z, color="k", linestyle="--")

            for ax in axs.flatten():
                ax.set_xlim(0, None)

            for ax in axs[-1]:
                ax.set_xlabel("Distance [m]")

            ylabel_mappings = {
                "beamsize": "Beam size [mm]",
                "gouy": "Gouy phase\naccumulation [deg]",
                "curvature": "Wavefront curvature [1/m]",
            }
            ylabel_diff_mappings = {
                "beamsize": r"$\mathrm{w}_\mathrm{x} - \mathrm{w}_\mathrm{y}$ [mm]",
                "gouy": r"$\psi_\mathrm{x} - \psi_\mathrm{y}$ [deg]",
                "curvature": r"$\mathrm{S}_\mathrm{x} - \mathrm{S}_\mathrm{y}$ [1/m]",
            }
            
            ylims = {}
            for i, arg in enumerate(args):
                if arg != "beamsize":
                    ylim = ylims.get(arg, None)
                    if ylim is None:
                        axs[i][0].set_ylim(0 if arg == "gouy" else None, maximums[arg])
                    else:
                        axs[i][0].set_ylim(ylim[0], ylim[1])

                ylabel = ylabel_mappings.get(arg, arg)
                axs[i][0].set_ylabel(ylabel)

                dylabel = ylabel_diff_mappings.get(arg)
                axs[i][1].set_ylabel(dylabel)

            if filename is not None:
                fig.savefig(filename)
            if show:
                plt.show()

            if N == 1:
                return fig, axs[0]

            return fig, axs
        else:
            fig, axs = plt.subplots(N, 1, sharex=True)

            if N == 1:
                axs = np.array([axs])

            maximums = {k: 0 for k in args}
            diff_mins = {k: 0 for k in args}

            data_x = sol.ps_x.all_segments(
                w_scale=1e3, npts=1000, resolution="equal", subs=None
            )
            data_y = sol.ps_y.all_segments(
                w_scale=1e3, npts=1000, resolution="equal", subs=None
            )

            for (zs_x, segd_x), (zs_y, segd_y) in zip(data_x.values(), data_y.values()):
                for i, arg in enumerate(args):
                    vx = segd_x[arg]
                    vy = segd_y[arg]
                    if arg == "beamsize":
                        if direction == 'both':
                            axs[i].fill_between(zs_x, vx, -vx, color="r", alpha=0.5)
                            axs[i].fill_between(zs_y, vy, -vy, color="b", alpha=0.5)
                        elif direction == 'x':
                            axs[i].fill_between(zs_x, vx, -vx, color="r", alpha=1)
                        else:
                            axs[i].fill_between(zs_y, vy, -vy, color="b", alpha=0.8)

                    else:
                        if direction == 'both':
                            axs[i].plot(zs_x, vx)
                            axs[i].plot(zs_y, vy, linestyle="--")
                        elif direction == 'x':
                            axs[i].plot(zs_x, vx)
                        else:
                            axs[i].plot(zs_y, vy,)

                    

                    maximums[arg] = max(maximums[arg], vx.max(), vy.max())
                    diff_mins[arg] = min(diff_mins[arg], (vx - vy).min())

            if direction == 'x':
                sub_sol = sol.ps_x
            else:
                sub_sol = sol.ps_y

            for node, info in sub_sol.node_info.items():
                if node.is_input:
                    z = sub_sol._eval_z_for_display(info, subs=None)

                    comp = node.component
                    if "AR" not in comp.name:
                        name = comp.name
                        x_offset = 0
                        y_offset = 0
                        # display the name in a nicer way
                        name = name.replace("_", "\n")
                        n_newlines = name.count("\n")

                        for i, arg in enumerate(args):
                            if not i:
                                axs[i].axvline(
                                    z,
                                    0.12 + 0.1 * n_newlines,
                                    color="k",
                                    linestyle="--",
                                )

                                if arg == "beamsize":
                                    ytext_pos = -1 * np.max(vy)
                                else:
                                    ytext_pos = 0
                                
                                # print(f"adding text {name}: {z}, {ytext_pos}")
                                axs[i].text(
                                    z + x_offset,
                                    ytext_pos + y_offset,
                                    name,
                                    ha="center",
                                    va="center",
                                    color='k'
                                )
                            else:
                                axs[i].axvline(z, color="k", linestyle="--")

            for ax in axs.flatten():
                ax.set_xlim(0, None)

            axs[-1].set_xlabel("Distance [m]")

            ylabel_mappings = {
                "beamsize": "Beam size [mm]",
                "gouy": "Gouy phase\naccumulation [deg]",
                "curvature": "Wavefront curvature [1/m]",
            }
            ylabel_diff_mappings = {
                "beamsize": r"$\mathrm{w}_\mathrm{x} - \mathrm{w}_\mathrm{y}$ [mm]",
                "gouy": r"$\psi_\mathrm{x} - \psi_\mathrm{y}$ [deg]",
                "curvature": r"$\mathrm{S}_\mathrm{x} - \mathrm{S}_\mathrm{y}$ [1/m]",
            }
            ylims = {}
            for i, arg in enumerate(args):
                if arg != "beamsize":
                    ylim = ylims.get(arg, None)
                    if ylim is None:
                        axs[i].set_ylim(0 if arg == "gouy" else None, maximums[arg])
                    else:
                        axs[i].set_ylim(ylim[0], ylim[1])

                ylabel = ylabel_mappings.get(arg, arg)
                axs[i].set_ylabel(ylabel)

            if filename is not None:
                fig.savefig(filename)
            if show:
                plt.show()

            if N == 1:
                return fig, axs[0]

            return fig, axs