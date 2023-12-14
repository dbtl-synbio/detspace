#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pandas as pd
from . import models
from rdkit.Chem import MolFromInchi
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.AllChem import Compute2DCoords
from urllib import parse


def init_db1():
    data_path = os.getenv('DETSPACE_DATA')
    plist = pd.read_csv(os.path.join(data_path,"Producible.csv"))
    models.Producibles.clear()
    for prod in plist:
        p = models.Producibles( [prod[0],prod[1]])
        p.save()


def get_producibles():
    data_path = os.getenv('DETSPACE_DATA')
    plist = pd.read_csv(os.path.join(data_path,"Producible.csv"))
    prods = []
    for row in plist.index:
        item = {}
        for col in plist.columns:
            val = str( plist.loc[row,col] )
            if val == 'nan':
                val = ''
            item[col] = str( val )
        prods.append( item )
    return(prods)

def get_detectables():
    data_path = os.getenv('DETSPACE_DATA')
    plist = pd.read_csv(os.path.join(data_path,"Detectable.csv"))
    dets = []
    for row in plist.index:
        item = {}
        for col in plist.columns:
            val = str( plist.loc[row,col] )
            if val == 'nan':
                val = ''
            item[col] = str( val )
        dets.append( item )
    return(dets)

def get_prod_det_pair():
    data_path = os.getenv('DETSPACE_DATA')
    plist = pd.read_csv(os.path.join(data_path,"Pathways_pairs.csv"))
    detl = {}
    prodl = {}
    for row in plist.index:
        val = plist.loc[row,'Pair']
        try:
            det,prod = val[1:].split("P")
        except:
            continue
        if det not in detl:
            detl[det] = set()
        detl[det].add(prod)
        if prod not in prodl:
            prodl[prod] = set()
        prodl[prod].add(det)
    return(prodl,detl)

def get_prod_detec(prod):
    prodl, detl = get_prod_det_pair()
    dets = get_detectables()
    pl = []
    for item in dets:
        if str(prod) in prodl:
            if item['ID'] in prodl[str(prod)]:
                pl.append(item)
    return(pl)

def get_detec_prod(det):
    prodl, detl = get_prod_det_pair()
    prods = get_producibles()
    dl = []
    for item in prods:
        if str(det) in detl:
            if item['ID'] in detl[str(det)]:
                dl.append(item)
    return(dl)

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



