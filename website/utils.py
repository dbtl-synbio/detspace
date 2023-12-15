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
    plist = pd.read_csv(os.path.join(data_path,"data","Producible.csv"))
    models.Producibles.clear()
    for prod in plist:
        p = models.Producibles( [prod[0],prod[1]])
        p.save()


def get_all_producibles():
    data_path = os.getenv('DETSPACE_DATA')
    plist = pd.read_csv(os.path.join(data_path,"data","Producible.csv"))
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


def get_producibles():
    prodl, detl = get_prod_det_pair()
    prods = get_all_producibles()
    dprods = []
    for item in prods:
        iid = item["ID"]
        if iid in prodl:
            item['Effectors'] = len( prodl[iid] );
            item['Pathways'] = sum( [ prodl[iid][x] for x in prodl[iid] ])           
            dprods.append(item)
    return(dprods)

def get_chassis():
    data_path = os.getenv('DETSPACE_DATA')
    plist = pd.read_csv(os.path.join(data_path,"chassis","ORGIDs.csv"))
    orgs = []
    for row in plist.index:
        item = {}
        for col in plist.columns:
            val = str( plist.loc[row,col] )
            if val == 'nan':
                val = ''
            item[col] = str( val )
        orgs.append( item )
    return(orgs)

def get_all_detectables():
    data_path = os.getenv('DETSPACE_DATA')
    plist = pd.read_csv(os.path.join(data_path,"data","Detectable.csv"))
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


def get_detectables():
    prodl, detl = get_prod_det_pair()
    detec = get_all_detectables()
    pdetect = []
    for item in detec:
        iid = item["ID"]
        if iid in detl:
            item['Products'] = len( detl[iid] );
            item['Pathways'] = sum( [ detl[iid][x] for x in detl[iid] ])           
            pdetect.append(item)
    return(pdetect)

def get_prod_det_pair():
    data_path = os.getenv('DETSPACE_DATA')
    plist = pd.read_csv(os.path.join(data_path,"data","Pairs.csv"))
    detl = {}
    prodl = {}
    for row in plist.index:
        val = plist.loc[row,'Pair']
        pat = plist.loc[row,'Pathways']
        try:
            det,prod = val[1:].split("P")
        except:
            continue
        if det not in detl:
            detl[det] = {}
        detl[det][prod] = pat
        if prod not in prodl:
            prodl[prod] = {}
        prodl[prod][det] = pat
    return(prodl,detl)

def get_prod_detec(prod):
    prodl, detl = get_prod_det_pair()
    dets = get_detectables()
    prod = str(prod)
    pl = []
    if prod in prodl:
        for item in dets:
            if item['ID'] in prodl[prod]:
                item['Selected'] = prodl[prod][item['ID']]
                pl.append(item)
    return(pl)

def get_detec_prod(det):
    prodl, detl = get_prod_det_pair()
    prods = get_producibles()
    det = str(det)
    dl = []
    if det in detl:
        for item in prods:
            if item['ID'] in detl[det]:
                item['Selected'] = detl[det][item['ID']]
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



