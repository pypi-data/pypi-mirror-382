""" 
A module for utility functions, to help populate both
finesse and gtrace models.
"""

import numpy as np
from typing import Tuple
from cosmicexplorer.finesse.components import ThickBeamsplitter, \
                                              ThickMirror, Cavity, \
                                              Laser, Lens
from finesse.components import Beamsplitter, Mirror

from finesse.detectors import PowerDetector, PowerDetectorDemod1
from gtrace.optics.gaussian import Rw2q, q2R, q2w
from termcolor import colored


def calculate_space_angle(comp: list,
                          compForward: list=None,
                          compBackward: list=None,
                          degree = False,
                          verbose = False) -> dict:
    """Calculates angle of incidence and spaces
    between optics.

    Args:
        comp (list): name, X, Y
        compForward (list): name, X, Y
        compBackward (list, optional): name, X, Y. Defaults to None.
        verbose (bool, optional): Print helpful messages. Defaults to False.

    Returns:
        dict: AOI, space to each component.
    """
    angleToComp = 0
    angleFromComp = 0
    info = {
        'normAngle': 0,
        'AOI': 0,
    }
    if compForward:
        info[f"to_{compForward[0]}"] = calculate_length(comp[1:], 
                                                         compForward[1:])
        
        angleFromComp = calculate_angle(comp[1:],
                                        compForward[1:])*np.pi/180
        
    if compBackward:
        info[f"to_{compBackward[0]}"] = calculate_length(comp[1:], 
                                                         compBackward[1:])

        angleToComp = calculate_angle(comp[1:],
                                      compBackward[1:])*np.pi/180
        
        
    # print(comp[0], angleFromComp, angleToComp)
    if angleFromComp == np.pi or angleFromComp == -np.pi:
        if not angleToComp == np.pi and not angleToComp == -np.pi:
            angleFromComp = np.pi * np.sign(angleToComp)

    if angleFromComp >= 3*np.pi/2 and angleToComp <= np.pi/2:
        angleFromComp -= 2*np.pi
    elif angleFromComp <= np.pi/2 and angleToComp>=3*np.pi/2:
        angleToComp -= 2*np.pi

    normAngle = (angleToComp + angleFromComp)/2
    # print(comp[0], normAngle)
    
    aoi = angleFromComp-normAngle
    
    info['angleF2'] = angleToComp * 180/np.pi
    info['angleF1'] = angleFromComp * 180/np.pi
    info['normAngle'] = normAngle * 180/np.pi
    info['AOI'] = np.abs(aoi) * 180/np.pi

    
    return info

def calculate_angle(comp1: list, comp2: list) -> float:
    for i in range(len(comp1)):
        comp1[i] = float(comp1[i])
        comp2[i] = float(comp2[i])
    vect = np.array(comp2) - np.array(comp1)

    

    if vect[0] == 0:
        angle = np.sign(vect[1])*np.pi/2
    
    else:
        angle = np.arctan2(vect[1],vect[0])

    if angle < 0:
        angle += 2*np.pi
    return angle * 180 / np.pi
    
def calculate_length(comp1: list, comp2: list) -> float:
    for i in range(len(comp1)):
        comp1[i] = float(comp1[i])
        comp2[i] = float(comp2[i])

    vect = np.array(comp2) - np.array(comp1)
    length = np.sqrt((np.sum(vect@vect)))
    return length
    
def set_params(component, parameters):

    # finesse_params = {
    #     'T': parameters['T'] if 'T' in parameters.keys() else 0,
    #     'L': parameters['L'] if 'L' in parameters.keys() else 0,
    #     'R_AR': parameters['R_AR'],
    # }

    # print(finesse_params)
    keys = list(parameters.keys())

    if 'T' in keys:
        component.T = parameters['T']
        component.R = 1 - component.T
    
    if 'L' in keys:
        component.L = parameters['L']
        component.R -= component.L

    if 'R_AR' in keys:
        component.R_AR = parameters['R_AR']

    if 'thickness' in keys:
        component.thickness = parameters['thickness']

    if 'phi' in keys:
        component.phi = parameters['phi']
    
    if 'Rc' in keys:
        if type(parameters['Rc']) == dict:
            Rc = parameters['Rc']
            if 'x' in Rc.keys() and 'y' in Rc.keys():
                component.Rc = [Rc['x'], Rc['y']]
            else:
                component.Rc = [Rc['X'], Rc['Y']]
        else:
            component.Rc = parameters['Rc']
    
    elif 'Rc_HR' in keys:
        if type(parameters['Rc_HR']) == dict:
            Rc = parameters['Rc_HR']
            if 'x' in Rc.keys() and 'y' in Rc.keys():
                component.Rc = [Rc['x'], Rc['y']]
            else:
                component.Rc = [Rc['X'], Rc['Y']]
        else:
            component.Rc = parameters['Rc_HR']
    
    if 'Rc_AR' in keys:
        if type(parameters['Rc_AR']) == dict:
            Rc = parameters['Rc_AR']
            if 'x' in Rc.keys() and 'y' in Rc.keys():
                component.Rc_AR = [Rc['x'], Rc['y']]
            else:
                component.Rc_AR = [Rc['X'], Rc['Y']]
        else:
            component.Rc_AR = parameters['Rc_AR']

    if 'alpha' in keys:
        component.alpha = parameters['alpha']
    
    elif 'aoi' in keys:
        component.alpha = parameters['aoi']

    if 'n' in keys:
        component.nr = parameters['n']
    elif 'nr' in keys:
        component.nr = parameters['nr']

    if 'diameter' in keys:
        component.diameter = parameters['diameter']
    
    if 'normAngle' in keys:
        component.normAngle = parameters['normAngle']

    if 'position' in keys:
        component.position = parameters['position']

    # if 'wedgeAngle' in keys:
    #     component.wedge_angle = parameters['wedgeAngle']
    #     if 'wedge' in keys:
    #         component.wedge = parameters['wedge']
    #     else:
    #         component.wedge = 'horz'

    if 'P' in keys:
        component.P = parameters['P']
    
    if 'Wavelength' in keys:
        component.lamb = parameters['Wavelength']

    if 'xbeta' in keys:
        component.xbeta = parameters['xbeta']

    if 'ybeta' in keys:
        component.ybeta = parameters['ybeta']
        
    if 'Width' in keys:
        component.Width = parameters['Width']
    
    if 'Length' in keys:
        component.Length = parameters['Length']

    # print(component.normAngle)
    return component

def pop_beamsplitter(name, mirror_params,
                     graph, all_mirrors) -> Tuple[ThickBeamsplitter, dict]:
    
    info = {}
    if 'Connections' not in mirror_params.keys():
        raise KeyError('Must declare connections, or leave empty.')
    connections = mirror_params['Connections']
    if 'normAngle' in mirror_params.keys():
        pre_norm_angle = mirror_params['normAngle']
    else:
        pre_norm_angle = None
    needed_keys = ['Front1', 'Front2',
                   'Back1', 'Back2']
    if not all([key in connections.keys() for key in needed_keys]):
        raise KeyError("Must have all FOUR keys, leave unused ones empty.")
    
    if connections['Front1'] and connections['Front2']:
        comp1 = [name, 
                mirror_params['Position']['X'],
                mirror_params['Position']['Y']]
        comp2 = [connections['Front1'], 
                all_mirrors[connections['Front1']]['Position']['X'],
                all_mirrors[connections['Front1']]['Position']['Y']]
        comp3 = [connections['Front2'], 
                all_mirrors[connections['Front2']]['Position']['X'],
                all_mirrors[connections['Front2']]['Position']['Y']]
        
        info = calculate_space_angle(comp1, comp3, comp2)
        

    elif (connections['Front1'] and connections['Back2']) and \
        not (connections['Front2'] or connections['Back1']):
        comp1 = [name, 
                mirror_params['Position']['X'],
                mirror_params['Position']['Y']]
        comp2 = [connections['Front1'], 
                all_mirrors[connections['Front1']]['Position']['X'],
                all_mirrors[connections['Front1']]['Position']['Y']]
        angleFront = calculate_angle(comp1[1:], comp2[1:])
        comp3 = [connections['Back2'], 
                all_mirrors[connections['Back2']]['Position']['X'],
                all_mirrors[connections['Back2']]['Position']['Y']]
        angleBack = calculate_angle(comp3[1:], comp1[1:])
        normAngle = (angleFront+180 + angleBack+180)/2
        
        
        info = calculate_space_angle(comp1, comp2, comp3)
        info['normAngle'] = normAngle

    elif (connections['Back1'] and connections['Back2']) and \
        not (connections['Front2'] or connections['Front1']):
        comp1 = [name, 
                mirror_params['Position']['X'],
                mirror_params['Position']['Y']]
        comp2 = [connections['Back1'], 
                all_mirrors[connections['Back1']]['Position']['X'],
                all_mirrors[connections['Back1']]['Position']['Y']]
        angleFront = calculate_angle(comp1[1:], comp2[1:])
        comp3 = [connections['Back2'], 
                all_mirrors[connections['Back2']]['Position']['X'],
                all_mirrors[connections['Back2']]['Position']['Y']]
        angleBack = calculate_angle(comp3[1:], comp1[1:])
        normAngle = (angleFront+180 + angleBack+180)/2
        
        
        info = calculate_space_angle(comp1, comp2, comp3)
        info['normAngle'] = normAngle
    
    elif ((connections['Front1'] and connections['Back1']) and \
        not (connections['Front2'] or connections['Back2'])) or \
        ((connections['Front2'] and connections['Back2']) and \
        not (connections['Front1'] or connections['Back1'])):

        if 'normAngle' not in mirror_params.keys():
            raise UserWarning(f"Cannot derive norm angle from one front and one back connection" +
                              f", try defining norm angle yourself for {name}.")
        comp1 = [name, 
                mirror_params['Position']['X'],
                mirror_params['Position']['Y']]
        comp2 = [connections['Front1'], 
                all_mirrors[connections['Front1']]['Position']['X'],
                all_mirrors[connections['Front1']]['Position']['Y']]
        comp3 = [connections['Back1'], 
                all_mirrors[connections['Back1']]['Position']['X'],
                all_mirrors[connections['Back1']]['Position']['Y']]
        
        
        info = calculate_space_angle(comp1, comp2, comp3)
        info['normAngle'] = mirror_params['normAngle']
        print(UserWarning(colored("You are trusting that you've positioned everything correctly and" \
                                  + f" angled it right...I did not calculate any steering for {name}.", 
                                  color='yellow')))

    else:
        try: 
            normAngle = mirror_params['normAngle']
            
            try:
                comp = connections['Front1']
                angle_to_comp = calculate_angle(
                    [mirror_params['Position']['X'],
                     mirror_params['Position']['Y']],
                    [all_mirrors[comp]['Position']['X'],
                     all_mirrors[comp]['Position']['Y']]
                )
                aoi = abs(angle_to_comp - normAngle)
                if aoi >= 90:
                    aoi = abs(angle_to_comp - normAngle - 360)
                
                info['AOI'] = aoi

            except KeyError as err1:
                raise UserWarning(f"You've left all connections blank for {name}, try again.")

        except KeyError as err2:
            raise UserWarning("You only have one connection for a beamsplitter." + 
                           " And you didn't define a norm angle..." +
                           " I don't know what you expect me to be able to do with this." +
                           "\n\nAdd another connection or norm angle" + 
                           f" definition to {name}.\n")

    for port1 in needed_keys:
        connect = connections[port1]
        if connect:
            for port, mirror in all_mirrors[connect]['Connections'].items():
                if mirror == name:
                    port2 = port

                    graph_node1 = f"{name}_{port1}_to_{connect}_{port2}"
                    graph_node2 = f"{connect}_{port2}_to_{name}_{port1}"
                    if graph_node1 in graph.keys() \
                        or graph_node2 in graph.keys():
                        continue
                    else:
                        m1 = mirror_params['Position']

                        m2 = all_mirrors[connect]['Position']
                        
                        keys = list(m1.keys())
                        for each_key in keys:
                            new_key = each_key.upper()
                            if new_key == each_key:
                                continue
                            else:
                                m1[new_key] = m1[each_key]
                                del m1[each_key]

                        comp1 = [name, 
                                    m1['X'],
                                    m1['Y']]
                        
                        keys = list(m2.keys())
                        for each_key in keys:
                            new_key = each_key.upper()
                            if new_key == each_key:
                                continue
                            else:
                                m2[new_key] = m2[each_key]
                                del m2[each_key]
                        
                        comp2 = [connect, 
                                    m2['X'],
                                    m2['Y']]
                        
                        if port1 in ['Back1', 'Back2', 'Back']:
                            n = mirror_params['n'] if 'n' in \
                                mirror_params.keys() else 1.45 
                            alpha = info['AOI']
                            theta = info['normAngle']
                            alpha_sub = np.arcsin(np.sin(np.radians(alpha))/n)
                            thickness = mirror_params['thickness'] if \
                                'thickness' in mirror_params.keys() else .005
                            offset = thickness/np.cos(alpha_sub)
                            if port1 == 'Back1':
                                comp1[1] += offset*np.cos(np.deg2rad(theta+180)+alpha_sub)
                                comp1[2] += offset*np.sin(np.deg2rad(theta+180)+alpha_sub)
                            elif port1 == 'Back2':
                                comp1[1] += offset*np.cos(np.deg2rad(theta+180)-alpha_sub)
                                comp1[2] += offset*np.sin(np.deg2rad(theta+180)-alpha_sub)
                            else:
                                comp1[1] += offset*np.cos(np.deg2rad(theta+180))
                                comp1[2] += offset*np.sin(np.deg2rad(theta+180))

                        if port2 in ['Back1', 'Back2', 'Back']:
                            conn_comp = all_mirrors[connect]
                            n = conn_comp['n'] if 'n' in \
                                conn_comp.keys() else 1.45 
                            alpha = info['AOI']
                            theta = info['normAngle']
                            alpha_sub = np.arcsin(np.sin(np.radians(alpha))/n)
                            thickness = float(conn_comp['thickness']) if \
                                'thickness' in conn_comp.keys() else .005
                            offset = thickness/np.cos(alpha_sub)
                            if port1 == 'Back1':
                                comp2[1] += offset*np.cos(np.deg2rad(theta+180)+alpha_sub)
                                comp2[2] += offset*np.sin(np.deg2rad(theta+180)+alpha_sub)
                            elif port1 == 'Back2':
                                comp2[1] += offset*np.cos(np.deg2rad(theta+180)-alpha_sub)
                                comp2[2] += offset*np.sin(np.deg2rad(theta+180)-alpha_sub)
                            else:
                                comp2[1] += offset*np.cos(np.deg2rad(theta+180))
                                comp2[2] += offset*np.sin(np.deg2rad(theta+180))
                        
                        length = calculate_length(comp1[1:], comp2[1:])
                        # print(length, graph_node1)
                        graph[graph_node1] = length

    # fix this later to allow just one connection for a beamsplitter
    mirror_params['position'] = [
                        mirror_params['Position']['X'],
                        mirror_params['Position']['Y']
                        ]
    mirror_params['normAngle'] = info['normAngle'] if 'normAngle' in info.keys() else 0
    mirror_params['aoi'] = info['AOI'] if 'AOI' in info.keys() else 0
    mirror_params['normInfo'] = info
    if pre_norm_angle != None:
        mirror_params['normAngle'] = pre_norm_angle
    component = set_params(ThickBeamsplitter(name, T=.1, L=0, thickness=.005), mirror_params)

    return (component, graph)

def pop_mirror(name, mirror_params,
               
               graph, all_mirrors) -> Tuple[ThickMirror, dict]:
    
    if 'Connections' not in mirror_params.keys():
        raise KeyError('Must declare connections, or leave empty.')
    
    connections = mirror_params['Connections']

    needed_keys = ['Front', 'Back']
    if not all([key in connections.keys() for key in needed_keys]):
        raise KeyError("Must have BOTH keys, leave unused ones empty.")
    
    if 'normAngle' in mirror_params.keys():
        pre_norm_angle = mirror_params['normAngle']
    else:
        pre_norm_angle = None

    for port1 in needed_keys:
        connect = connections[port1]
        if connect:
            for port, mirror in all_mirrors[connect]['Connections'].items():
                if mirror == name:
                    port2 = port

                    graph_node1 = f"{name}_{port1}_to_{connect}_{port2}"
                    graph_node2 = f"{connect}_{port2}_to_{name}_{port1}"

                    comp1_pos = mirror_params['Position']
                    keys = list(comp1_pos.keys())
                    for each_key in keys:
                        new_key = each_key.upper()
                        if new_key == each_key:
                            continue
                        else:
                            comp1_pos[new_key] = comp1_pos[each_key]
                            del comp1_pos[each_key]

                    comp1 = [name, 
                                 comp1_pos['X'],
                                 comp1_pos['Y']]
                    
                    comp2_pos = all_mirrors[connect]['Position']
                    keys = list(comp2_pos.keys())
                    for each_key in keys:
                        new_key = each_key.upper()
                        if new_key == each_key:
                            continue
                        else:
                            comp2_pos[new_key] = comp2_pos[each_key]
                            del comp2_pos[each_key]
                        
                    comp2 = [mirror, 
                                comp2_pos['X'],
                                comp2_pos['Y']]
                    
                    info = calculate_space_angle(comp1, comp2, comp2)
                    # print(name, connect, info)
                    length = info[f"to_{name}"]
                    if port1 == 'Front':
                        mirror_params['normAngle'] = calculate_angle(comp1[1:], comp2[1:])
                        mirror_params['position'] = [
                            mirror_params['Position']['X'],
                            mirror_params['Position']['Y']
                        ]
                    elif port1 == 'Back' and \
                        'normAngle' not in mirror_params.keys():
                        mirror_params['normAngle'] = calculate_angle(comp1[1:], comp2[1:])+180
                        mirror_params['position'] = [
                            mirror_params['Position']['X'],
                            mirror_params['Position']['Y']
                        ]
                        
                        length -= mirror_params['thickness'] if 'thickness' \
                                    in mirror_params.keys() else .005
                    if port2 == 'Back':
                        conn_comp = all_mirrors[connect]
                        length -= conn_comp['thickness'] if 'thickness' \
                                    in conn_comp.keys() else .005

                    if graph_node1 in graph.keys() \
                        or graph_node2 in graph.keys():
                        continue
                    else:
                        
                        # print(length, graph_node1)
                        graph[graph_node1] = length
                        
    # print(info)
    mirror_params['position'] = [
                        mirror_params['Position']['X'],
                        mirror_params['Position']['Y']
                        ]
    if pre_norm_angle != None:
        mirror_params['normAngle'] = pre_norm_angle
    component = set_params(
        ThickMirror(name, T=.1, L=0, thickness=.005,
                    wedge=mirror_params['wedge'] if 'wedge' in mirror_params.keys() else 'horiz',
                    wedge_angle=mirror_params['wedgeAngle'] if 'wedgeAngle' in mirror_params.keys() else '0',)
                    , mirror_params)
    return (component, graph)

def pop_lens(name, mirror_params,
               
               graph, all_mirrors) -> Tuple[ThickMirror, dict]:
    
    if 'Connections' not in mirror_params.keys():
        raise KeyError('Must declare connections, or leave empty.')
    
    thin_lens = 'Focal Length' in mirror_params.keys()
    
    connections = mirror_params['Connections']

    needed_keys = ['Front', 'Back']
    if not all([key in connections.keys() for key in needed_keys]):
        raise KeyError("Must have BOTH keys, leave unused ones empty.")
    
    if 'normAngle' in mirror_params.keys():
        pre_norm_angle = mirror_params['normAngle']
    else:
        pre_norm_angle = None

    for port1 in needed_keys:
        connect = connections[port1]
        if connect:
            for port, mirror in all_mirrors[connect]['Connections'].items():
                if mirror == name:
                    port2 = port

                    graph_node1 = f"{name}_{port1}_to_{connect}_{port2}"
                    graph_node2 = f"{connect}_{port2}_to_{name}_{port1}"

                    comp1_pos = mirror_params['Position']
                    keys = list(comp1_pos.keys())
                    for each_key in keys:
                        new_key = each_key.upper()
                        if new_key == each_key:
                            continue
                        else:
                            comp1_pos[new_key] = comp1_pos[each_key]
                            del comp1_pos[each_key]

                    comp1 = [name, 
                                 comp1_pos['X'],
                                 comp1_pos['Y']]
                    
                    comp2_pos = all_mirrors[connect]['Position']
                    keys = list(comp2_pos.keys())
                    for each_key in keys:
                        new_key = each_key.upper()
                        if new_key == each_key:
                            continue
                        else:
                            comp2_pos[new_key] = comp2_pos[each_key]
                            del comp2_pos[each_key]
                        
                    comp2 = [mirror, 
                                comp2_pos['X'],
                                comp2_pos['Y']]
                    
                    info = calculate_space_angle(comp1, comp2, comp2)
                    # print(name, connect, info)
                    length = info[f"to_{name}"]
                    if port1 == 'Front':
                        mirror_params['normAngle'] = calculate_angle(comp1[1:], comp2[1:])
                        mirror_params['position'] = [
                            mirror_params['Position']['X'],
                            mirror_params['Position']['Y']
                        ]
                    elif port1 == 'Back' and \
                        'normAngle' not in mirror_params.keys():
                        mirror_params['normAngle'] = calculate_angle(comp1[1:], comp2[1:])+180
                        mirror_params['position'] = [
                            mirror_params['Position']['X'],
                            mirror_params['Position']['Y']
                        ]

                    if graph_node1 in graph.keys() \
                        or graph_node2 in graph.keys():
                        continue
                    else:
                        
                        # print(length, graph_node1)
                        graph[graph_node1] = length
                        
    # print(info)
    mirror_params['position'] = [
                        mirror_params['Position']['X'],
                        mirror_params['Position']['Y']
                        ]
    if pre_norm_angle != None :
        mirror_params['normAngle'] = pre_norm_angle

    if thin_lens:
        focus = float(mirror_params['Focal Length'])
        if 'Thickness' in mirror_params.keys():
            print("\nWarning: Model defines a focus, " \
                  +"indicating the use of a thin lens, thickness not used.")
        component = set_params(ThickMirror(name, T=1, L=0, thickness=.0005), mirror_params)
        nr = getattr(component, 'nr', 1.45)
        component.Rc = np.inf
        component.Rc_AR = focus*(nr-1)

    else:
        try:
            Rc1 = float(mirror_params['Rc']['Front'])
            Rc2 = float(mirror_params['Rc']['Back'])
            thickness = mirror_params.get('Thickness', 0.02)
            
            mirror_params['Rc'] = -Rc1
            mirror_params['Rc_AR'] = Rc2
        except BaseException("Adding thick lens to model. "\
                        +"Must use 'Rc: Front', 'Rc: Back'. "
                        +"Adding thick lens with flat faces."):
            
            mirror_params['Rc'] = np.inf
            mirror_params['Rc_AR'] = np.inf
            thickness = .02
        component = set_params(ThickMirror(name, R=0, T=1, L=0,
                                           thickness = thickness), 
                                           mirror_params)
    
    return (component, graph)

def pop_laser(name, mirror_params,
               
               graph, all_mirrors) -> Tuple[Laser, dict]:
    
    if 'Connections' not in mirror_params.keys():
        raise KeyError('Must declare connections, or leave empty.')
    if 'normAngle' in mirror_params.keys():
        pre_norm_angle = mirror_params['normAngle']
    else:
        pre_norm_angle = None
        
    connections = mirror_params['Connections']

    needed_keys = ['Front']
    if not all([key in connections.keys() for key in needed_keys]):
        raise KeyError("Must have FRONT key.")
    
    connect = connections['Front']
    if connect:
        for port, mirror in all_mirrors[connect]['Connections'].items():
            if mirror == name:
                port2 = port

                graph_node1 = f"{name}_Front_to_{connect}_{port2}"
                graph_node2 = f"{connect}_{port2}_to_{name}_Front"

                comp1 = [name, 
                                mirror_params['Position']['X'],
                                mirror_params['Position']['Y']]
                comp2 = [mirror, 
                            all_mirrors[connect]['Position']['X'],
                            all_mirrors[connect]['Position']['Y']]
                
                info = calculate_space_angle(comp1, comp2, comp2)
                length = info[f"to_{name}"]
                mirror_params['position'] = [
                                    mirror_params['Position']['X'],
                                    mirror_params['Position']['Y']
                                    ]
                angle = calculate_angle(comp1[1:], comp2[1:])
                mirror_params['normAngle'] = angle

                if graph_node1 in graph.keys() \
                    or graph_node2 in graph.keys():
                    continue
                else:
                    
                    # print(length, graph_node1)
                    graph[graph_node1] = length

    if pre_norm_angle != None:
        mirror_params['normAngle'] = pre_norm_angle
    component = set_params(Laser(name, P=1), mirror_params)
    component.fr = component.p1
    wl = getattr(component, 'lamb', 1064e-9)

    if 'Match' in mirror_params.keys():
        cav_to_match = mirror_params['Match']
        if not cav_to_match in all_mirrors.keys():
            print(f"\nWarning: {cav_to_match} cavity not found in model. " +
                  "Setting beam parameter to default.\n")
            component.Rc = np.inf
            component.w = 3e-3
            component.q0 = Rw2q(np.inf, 3e-3, wl=wl)
        else:
            component.q0 = {'TBD': cav_to_match}
        pass

    elif 'RoC' in mirror_params.keys() and \
        'w' in mirror_params.keys():
        R=float(mirror_params['RoC'])
        w=float(mirror_params['w'])
        component.Rc = R
        component.w = w
        component.q0 = Rw2q(R, w, wl=wl)
    elif 'q0' in mirror_params.keys():
        if isinstance(mirror_params['q0'], list):
            q0x, q0y = complex(mirror_params['q0'][0]), complex(mirror_params['q0'][1])
            component.q0 = [q0x, q0y]
            component.R = [q2R(q0x), q2R(q0y)]
            component.w = [q2w(q0x, wl=wl), q2w(q0y, wl=wl)]
        else:
            q0 = complex(mirror_params['q0'])
            component.q0 = q0
            component.R = q2R(q0)
            component.w = q2w(q0, wl=wl)
        
    return (component, graph)

def pop_cavity(name, params,
               components, model) -> Tuple[Cavity, dict]:
    
    needed_keys = ['From']  

    if not all([key in params.keys() for key in needed_keys]):
        raise KeyError("Must have From key specifying where cavity \
                       search starts.")
    
    node = params['From']
    comp, port, node = node.split('.')

    if hasattr(model, comp):
        from_node = getattr(model, comp)
        from_node = getattr(from_node, port)
        from_node = getattr(from_node, node)
    
    if 'Via' in params.keys() and params['Via'] != None:
        node = params['Via']
        comp, port, node = node.split('.')
        via_node = getattr(model, comp)
        via_node = getattr(via_node, port)
        via_node = getattr(via_node, node)
    else: via_node=None

    # print(via_node)
    cavity = Cavity(name, source=from_node, via=via_node)
    cavity.n_refls = 0
    model.add(cavity)

    reflections = set()
    for each_comp in cavity.path.components_only:
        if type(each_comp) in [Beamsplitter, Mirror]:
            reflections.add(each_comp.name.split("_")[0])
    setattr(cavity, "n_refls", len(reflections))
    return cavity

def pop_pd(name, params, components,
           model) -> PowerDetector:
    
    if 'Port' not in params[name].keys():
        raise KeyError('Must declare connected port, cannot be empty.')
        
    if 'normAngle' in params[name].keys():
        prenormAngle = params[name]['normAngle']
    else:
        prenormAngle = None

    
    ports = params[name]['Port'].split('.')
    comp = getattr(model, ports[0])
    port = getattr(comp, ports[1])
    if len(ports) == 3:
        port = getattr(port, ports[2])
    else:
        port = getattr(port, 'o')
        
    for each_comp in params:
        if each_comp == ports[0]:
            if params[each_comp]['Type'] == 'Beamsplitter':
                info = params[each_comp].get('normInfo')
                comp_norm_angle = params[each_comp]['normAngle']
                anglef2 = info.get('angleF2', info['AOI']+comp_norm_angle)
                if ports[1] == 'bk1':
                    if anglef2 > comp_norm_angle:
                        normAngle = comp_norm_angle + \
                                params[each_comp]['aoi']
                    else:
                        normAngle = comp_norm_angle - \
                                params[each_comp]['aoi']
                else: 
                    if anglef2 > comp_norm_angle:
                        normAngle = comp_norm_angle - \
                                params[each_comp]['aoi']
                    else:
                        normAngle = comp_norm_angle + \
                                params[each_comp]['aoi']
            else:
                normAngle = params[each_comp]['normAngle']

    normAngle = normAngle * np.pi/180
    if ports[1] in ['fr', 'fr1', 'fr2']:
        normAngle -= np.pi


    params[name]['normAngle'] = normAngle if prenormAngle == None else prenormAngle*np.pi/180
    params[name]['position'] = params[name]['Position']

    if 'Omega' in params[name].keys():
        f = params[name]['Omega']
        phase = params[name]['Phase'] if 'Phase' in params[name].keys() else 0
        pd = set_params(PowerDetectorDemod1(name, port,
                                            f, phase=phase), params[name])
    else:
        pd = set_params(PowerDetector(name, port), params[name])
    pd.width = float(params[name].get('width', .05))
    pd.width = float(params[name].get('Width', pd.width))
    
    return pd

