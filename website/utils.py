#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rdkit.Chem import MolFromInchi
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.AllChem import Compute2DCoords
from urllib import parse



def annotate_chemical_svg(network):
    """Annotate chemical nodes with SVGs depiction.

    :param network: dict, network of elements
    :return: dict, network annotated
    """

    for node in network['elements']['nodes']:
        if node['data']['type'] == 'chemical' and node['data']['inchi'] is not None:
            inchi = node['data']['inchi']
            try:
                mol = MolFromInchi(inchi)
                Compute2DCoords(mol)
                drawer = rdMolDraw2D.MolDraw2DSVG(200, 200)
                drawer.DrawMolecule(mol)
                drawer.FinishDrawing()
                svg_draft = drawer.GetDrawingText().replace("svg:", "")
                svg = 'data:image/svg+xml;charset=utf-8,' + parse.quote(svg_draft)
                node['data']['svg'] = svg
            except BaseException as e:
                node['data']['svg'] = None

    return network


