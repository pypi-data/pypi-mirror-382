#!/usr/bin/env python
"""
Command-line script to quickly plot gtrace renderings as well as traces
of cavity eigenmodes, as well as defined beam traces.

\nExample:\n
fintrace_plot_yaml examples/bowtie_test.yaml \
    --gtrace examples/figures/bowtie_cavity \
    --beam-origin cavity  \
    --draw-width --grid  \
    --cavity-trace all \
    --beam-trace M3.fr2.o M4.fr1.i \
    --save-path examples/figures/ \
    --verbose
"""

import argparse, yaml, os
from fintrace.model import FintraceModel

def complex_q(value):
    real, imag = value.split('+')
    imag = imag[:-1]
    real, imag = map(float, [real, imag])
    return real+1j*imag

parser = argparse.ArgumentParser(
    description=__doc__)

parser.add_argument("yamlfile", type=str,
                    help="Path of .yml file to plot.")
parser.add_argument("--gtrace", type=str, default=None,
                    nargs='?', const=True,
                    help="Plot Gtrace, and path to save the \
                        figure (optional)")
parser.add_argument("--beam-origin", 
                    choices=['cavity', 'laser'],
                    default='laser',
                    help='What kind of beam trace to do in \
                        gtrace. If using a laser, than put \
                        so in the .yaml file; otherwise, define \
                        a cavity to plot the beam trace of \
                        (if unstable, will not plot).')
parser.add_argument("--skip-optics", nargs="+", type=str,
                    default = [],
                    help="List of component names (must be optics) to skip \
                        in plotting and beam tracing (useful to reduce \
                        scale of rendering). However these optics will \
                        remain present in any finesse modelings.")
parser.add_argument("--power-threshold", type=float,
                    default=1e-3, help="Parameter controlling minimum power threshold \
                    to continue non-sequential beam trace with gtrace.")
parser.add_argument("--draw-width", default=False, action='store_true',
                    help="Draw 3*beamwidth lines in gtrace rendering. Otherwise just \
                        plot central ray.")
parser.add_argument('--img-res', default=600, type=int,
                    help="Image resolution to save.")
parser.add_argument("--grid", '-+', default=False,
                    action='store_true', help="Plot dynamically \
                    generated grid lines, or if Grid object is defined \
                    in yamlfile then will plot that.")

parser.add_argument("--cavity-trace", type=str, default=None,
                    nargs='+',
                    help='Plot a beam trace of specified cavity(s), or \
                        all. Will default be saved to $PWD/figures/, \
                        or can specify --save-path.')
parser.add_argument("--cavity-scan", type=str, default=None,
                    nargs='+',
                    help='Plot a beam trace of specified cavity(s), or \
                        all. Will default be saved to $PWD/figures/, \
                        or can specify --save-path.')
parser.add_argument("--beam-trace", type=str, default=None,
                    nargs='+',
                    help='Plot a beam trace with specified start and end, as well as \
                        optional via node. Syntax for nodes follow FINESSE notation.')
parser.add_argument("--plot", type=bool, default=True,
                    help="Whether or not to plot beam trace and save to $PWD/figures/, \
                        or save to --save-path.")
parser.add_argument("--plot-args", type=str, default=['all'], nargs='+',
                    help="Which of beamsizes, gouys, curvatures to plot \
                          on cavity trace.")
parser.add_argument("--direction", type=str, default=None, nargs=1,
                    help="Which of x y direction to plot \
                          on cavity trace.")
parser.add_argument("--q-at", type=str, default=None, nargs='+',
                    help="Prints the q-parameter at a given node in path given beam-trace nodes \
                        or within specifed cavity.")
parser.add_argument("--imshow", default=False,
                    action='store_true',
                    help="Plot image of beam intensity at the given q-at, and \
                        save to savepath.")
parser.add_argument("--q-in", type=complex_q, default=None, nargs=1,
                    help="Defines the starting q to propagate beam through beam-trace path.\
                          Real and Imaginary as separate arguments. Note if the real part \
                          of your q is negative use an equal sign between: --q-in=q. \
                          Default is q corresponding to 3mm beam at its waist.")
parser.add_argument("--scan-max-mode", type=int, default=3,
                    help="Integer n+m to serve as maximum modes plotted in cavity \
                        scan.")

parser.add_argument('--save-path', type=str, default=None,
                    help="Path to save figures generated by beam-trace and cavity-trace.")
parser.add_argument('--keep-dxf', default=False,
                    action='store_true',
                    help='Whether or not to keep .dxf file of gtrace plot.')
parser.add_argument('--keep-svg', default=False,
                    action='store_true',
                    help='Whether or not to keep .svg file of gtrace plot.')
parser.add_argument('--show', default=False,
                    action='store_true')
parser.add_argument('-v','--verbose', default=False,
                    action='store_true')

def main():
    args = parser.parse_args()

    model = FintraceModel()
    gdict, cavs, dets = model.build_from_yaml(args.yamlfile, True, 
                                        verbose=args.verbose)

    if args.gtrace:
        
        model.gtrace_plot(gdict, cavs, dets, beam_origin=args.beam_origin,
                        grid=args.grid, draw_width=args.draw_width,
                        savefile=args.gtrace, img_res=args.img_res,
                        skip_optics=args.skip_optics,
                        power_threshold=args.power_threshold,
                        keep_dxf=args.keep_dxf,
                        keep_svg=args.keep_svg)

    if args.cavity_trace:

        cavities = args.cavity_trace
        # print(args.plot_args)
        astig=True
        if args.direction != None:
            astig=False
            direction=args.direction[0]  
        else:
            direction='both'
        model.trace_cavities(cavity_traces=cavities, show=args.show, q_at=args.q_at,
                            verbose=args.verbose, savepath=args.save_path, 
                            imshow=args.imshow, plot=args.plot_args,
                            direction = direction, astig_difference=astig)
        
    if args.cavity_scan:

        cavities = args.cavity_scan
        model.scan_cavity(cavity_names=cavities, show=args.show, nm=args.scan_max_mode,
                        savepath=args.save_path)

    if args.beam_trace:
        
        q_in =  args.q_in
        astig=True
        if args.direction != None:
            astig=False
            direction=args.direction[0]  
        else:
            direction='both'

        if isinstance(q_in, list):
            for q in q_in:
                model.trace_beam(beamtrace=args.beam_trace, savepath=args.save_path,
                                    plot=args.plot_args, q_at=args.q_at, show=args.show, q_in=q,
                                    imshow = args.imshow, direction=direction, 
                                    astig_difference=astig)
        elif q_in == None:
            model.trace_beam(beamtrace=args.beam_trace, savepath=args.save_path,
                                    plot=args.plot_args, q_at=args.q_at, show=args.show, q_in=None,
                                    imshow = args.imshow, direction=direction, 
                                    astig_difference=astig)
