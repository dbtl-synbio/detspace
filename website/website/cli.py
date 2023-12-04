#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""cli.py: CLI for generating the JSON file expected by the pathway visualiser."""
 
__author__ = 'Thomas Duigou'
__license__ = 'MIT'


import os
import sys
import json
import logging
import tarfile
import argparse
import tempfile

from rpviz.utils import sbml_to_json, annotate_cofactors, annotate_chemical_svg, get_autonomous_html
from rpviz.Viewer import Viewer

if __name__ == '__main__':

    # Arguments
    parser = argparse.ArgumentParser(description='Converting SBML RP file.')
    parser.add_argument('input_rpSBMLs',
                        help='Input file containing rpSBML files in a tar archive or a folder.')
    parser.add_argument('output_folder',
                        help='Output folder to be used. If it does not exist, an attempt will be made to create it.'
                             'It the creation of the folder fails, IOError will be raised.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on debug instructions')
    parser.add_argument('--template_folder',
                        default=os.path.join(os.path.dirname(__file__), 'templates'),
                        help='Path to the folder containing templates')
    parser.add_argument('--cofactor',
                        default=os.path.join(os.path.dirname(__file__), 'data', 'cofactor_inchi_201811.tsv'),
                        help='File listing structures to consider as cofactors.')
    parser.add_argument('--autonomous_html',
                        default=None,
                        help="Optional file path, if provided will output an autonomous HTML containing all dependancies.")
    args = parser.parse_args()

    # Logging
    logging.basicConfig(stream=sys.stderr,
                        level=logging.WARNING,
                        datefmt='%d/%m/%Y %H:%M:%S',
                        format='%(asctime)s -- %(levelname)s -- %(message)s')

    # Make out folder if needed
    if not os.path.isfile(args.output_folder):
        try:
            os.makedirs(args.output_folder, exist_ok=True)
        except IOError as e:
            raise e

    # Extract input if it is a tar archive
    if os.path.isfile(args.input_rpSBMLs) and tarfile.is_tarfile(args.input_rpSBMLs):
        with tempfile.TemporaryDirectory() as tmp_folder:
            tar = tarfile.open(args.input_rpSBMLs, mode='r')
            tar.extractall(path=tmp_folder)
            tar.close()
            network, pathways_info = sbml_to_json(input_folder=tmp_folder)
    elif os.path.isdir(args.input_rpSBMLs):
        network, pathways_info = sbml_to_json(input_folder=args.input_rpSBMLs)
    else:
        raise NotImplementedError()

    # Add annotations
    network = annotate_cofactors(network, args.cofactor)  # Typical cofactors
    network = annotate_chemical_svg(network)  # SVGs depiction for chemical

    # Build the Viewer
    viewer = Viewer(out_folder=args.output_folder, template_folder=args.template_folder)
    viewer.copy_templates()

    # Write info extracted from rpSBMLs
    json_out_file = os.path.join(args.output_folder, 'network.json')
    with open(json_out_file, 'w') as ofh:
        ofh.write('network = ' + json.dumps(network, indent=4))
        ofh.write(os.linesep)
        ofh.write('pathways_info = ' + json.dumps(pathways_info, indent=4))
    
    # Write single HTML if requested
    if args.autonomous_html is not None:
        str_html = get_autonomous_html(args.output_folder)
        with open(args.autonomous_html, 'wb') as ofh:
            ofh.write(str_html)
