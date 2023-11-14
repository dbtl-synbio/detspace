#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""cli.py: CLI for generating the JSON file expected by the pathway visualiser."""
 
__author__ = 'Thomas Duigou'
__license__ = 'MIT'


import os
import csv
import glob
import logging

from statistics import mean
from collections import OrderedDict

import rpSBML

miriam_header = {'compartment': {'go': 'go/GO:', 'mnx': 'metanetx.compartment/', 'bigg': 'bigg.compartment/', 'seed': 'seed/', 'name': 'name/'}, 'reaction': {'metanetx': 'metanetx.reaction/', 'rhea': 'rhea/', 'reactome': 'reactome/', 'bigg': 'bigg.reaction/', 'sabiork': 'sabiork.reaction/', 'ec-code': 'ec-code/', 'biocyc': 'biocyc/', 'lipidmaps': 'lipidmaps/'}, 'species': {'metanetx': 'metanetx.chemical/', 'chebi': 'chebi/CHEBI:', 'bigg': 'bigg.metabolite/', 'hmdb': 'hmdb/', 'kegg_c': 'kegg.compound/', 'kegg_d': 'kegg.drug/', 'biocyc': 'biocyc/META:', 'seed': 'seed.compound/', 'metacyc': 'metacyc.compound/', 'sabiork': 'sabiork.compound/', 'reactome': 'reactome/R-ALL-'}}


def sbml_to_json(input_folder, pathway_id='rp_pathway', sink_species_group_id='rp_sink_species'):
    """Parse the collection of rpSBML files and outputs as dictionaries the network and pathway info

    :param input_folder: str,  path to the folder containing the collection of rpSBML
    :param pathway_id: str, pathway_ID prefix
    :return: 2 dictionaries, network and pathways_info

    Notice: need to parse the structure to SVG files
    """
    network = {'elements': {'nodes': [], 'edges': []}}
    pathways_info = {}

    # Shortcuts
    reac_nodes = {}
    chem_nodes = {}
    edges_nodes = {}

    # glob.escape() prevents issues with brackets in the inputted path
    for sbml_path in glob.glob(glob.escape(input_folder) + '/*.xml'):
        filename = sbml_path.split('/')[-1].replace('.sbml', '').replace('.rpsbml', '').replace('.xml', '')
        rpsbml = rpSBML.rpSBML(filename)
        rpsbml.readSBML(sbml_path)
        groups = rpsbml.model.getPlugin('groups')
        rp_pathway = groups.getGroup(pathway_id)
        brsynth_annot = rpsbml.readBRSYNTHAnnotation(rp_pathway.getAnnotation())
        norm_scores = [i for i in brsynth_annot if i[:5]=='norm_']
        norm_scores.append('global_score')
        logging.info('norm_scores: '+str(norm_scores))
        ############## pathway_id ##############
        scores = {}
        pathway_rule_scores = []
        for i in norm_scores:
            try:
                scores[i] = brsynth_annot[i]['value']
            except KeyError:
                logging.warning('Cannot retreive the following information in rpSBML: '+str(i)+'. Setting to 0.0...')
                pass
        try:
            target_flux = brsynth_annot['fba_obj_fraction']['value']
        except KeyError:
            logging.warning('Cannot retreive objective function fba_obj_fraction, must be another one')
            target_flux = 0.0
        pathways_info[rpsbml.modelName] = {
            'path_id': rpsbml.modelName,
            'node_ids': [],
            'edge_ids': [],
            'scores': scores,
            'nb_steps': rp_pathway.num_members,
            'fba_target_flux': target_flux,
            'thermo_dg_m_gibbs': None,
            'rule_score': None
        }
        try:
            pathways_info[rpsbml.modelName]['thermo_dg_m_gibbs'] = brsynth_annot['dfG_prime_m']['value']
        except KeyError:
            pass
        ################ REACTIONS #######################
        for reaction_name in rpsbml.readRPpathwayIDs():
            reaction = rpsbml.model.getReaction(reaction_name)
            brsynth_annot = rpsbml.readBRSYNTHAnnotation(reaction.getAnnotation())
            miriam_annot = rpsbml.readMIRIAMAnnotation(reaction.getAnnotation())
            # Build the node ID -- Based on the reaction SMILES
            tmp_smiles = None
            if not 'smiles' in brsynth_annot:
                try:
                    node_id = sorted(miriam_annot['metanetx'], key=lambda x: int(x.replace('MNXR', '')))[0]
                except KeyError:
                    try:
                        node_id = sorted(miriam_annot['kegg'], key=lambda x: int(x.replace('R', '')))[0]
                    except KeyError:
                        logging.error('Could not assign a valid ID, node reaction skipped')
                        continue
            else:
                node_id = brsynth_annot['smiles']
                tmp_smiles = brsynth_annot['smiles']
            # Build a new node if not met yet
            if node_id not in reac_nodes:
                node = dict()
                node['id'] = node_id
                node['path_ids'] = [rpsbml.modelName]
                node['type'] = 'reaction'
                if ('ec-code' in miriam_annot) and (len(miriam_annot['ec-code'])):
                    node['label'] = miriam_annot['ec-code'][0]  # Expected to be a list
                    node['all_labels'] = miriam_annot['ec-code'] + [brsynth_annot['rule_id']]
                else:
                    node['label'] = brsynth_annot['rule_id']
                    node['all_labels'] = [brsynth_annot['rule_id']]
                node['svg'] = ''
                node['xlinks'] = []
                for xref in miriam_annot:
                    for ref in miriam_annot[xref]:
                        # Refine EC annotations
                        if xref == 'ec-code':
                            # Getting rid of dashes
                            old_ref = ref
                            tmp = []
                            for _ in ref.split('.'):
                                if _ != '-':
                                    tmp.append(_)
                            ref = '.'.join(tmp)
                            if old_ref != ref:
                                logging.info('Refining EC number crosslinks from {} to {}'.format(old_ref, ref))
                            # Use direct link to workaround generic ECs issue with identifiers.org
                            try:
                                node['xlinks'].append({
                                    'db_name': 'intenz',
                                    'entity_id': ref,
                                    'url': 'https://www.ebi.ac.uk/intenz/query?cmd=SearchEC&ec=' + ref })
                                logging.debug('Shunting identifiers.org to IntEnz crosslinks for EC number {}'.format(ref))
                            except KeyError:
                                pass
                        # Generic case
                        else:
                            try:
                                node['xlinks'].append({
                                    'db_name': xref,
                                    'entity_id': ref,
                                    'url': 'http://identifiers.org/'+miriam_header['reaction'][xref]+str(ref)})
                            except KeyError:
                                pass
                node['rsmiles'] = tmp_smiles
                node['rule_id'] = brsynth_annot['rule_id']
                try:
                    node['ec_numbers'] = miriam_annot['ec-code']
                except KeyError:
                    node['ec_numbers'] = None
                try:
                    node['thermo_dg_m_gibbs'] = brsynth_annot['dfG_prime_m']['value']
                except KeyError:
                    node['thermo_dg_m_gibbs'] = None
                #node['fba_reaction'] = '0'
                try:
                    node['rule_score'] = round(brsynth_annot['rule_score']['value'], 3)
                    pathway_rule_scores.append(brsynth_annot['rule_score']['value'])
                except KeyError:
                    node['rule_score'] = None
                    pathway_rule_scores.append(0.0)
                node['smiles'] = None
                node['inchi'] = None
                node['inchikey'] = None
                node['target_chemical'] = None
                node['sink_chemical'] = None
                node['thermo_dg_m_formation'] = None
                node['cofactor'] = None
                # Store
                reac_nodes[tmp_smiles] = node
            # Update already existing node
            else:
                try:
                    node['rule_score'] = round(brsynth_annot['rule_score']['value'], 3)
                    pathway_rule_scores.append(brsynth_annot['rule_score']['value'])
                except KeyError:
                    node['rule_score'] = None
                    pathway_rule_scores.append(0.0)
                if rpsbml.modelName not in reac_nodes[node_id]['path_ids']:
                    reac_nodes[node_id]['path_ids'].append(rpsbml.modelName)
                if brsynth_annot['rule_id'] not in reac_nodes[node_id]['all_labels']:
                    reac_nodes[node_id]['all_labels'].append(brsynth_annot['rule_id'])
                try:
                    assert tmp_smiles == reac_nodes[node_id]['rsmiles']
                except AssertionError as e:
                    logging.warning(e)
                try:
                    assert brsynth_annot['rule_id'] == reac_nodes[node_id]['rule_id']
                except AssertionError as e:
                    logging.warning(e)
            # Keep track for pathway info
            if node_id not in pathways_info[rpsbml.modelName]['node_ids']:
                pathways_info[rpsbml.modelName]['node_ids'].append(node_id)
        pathways_info[rpsbml.modelName]['rule_score'] = round(mean(pathway_rule_scores), 3)
        ################# CHEMICALS #########################
        ## compile all the species that are sink molecules
        #
        largest_rp_reac_id = sorted([i.getIdRef() for i in rp_pathway.getListOfMembers()], key=lambda x: int(x.replace('RP', '')), reverse=True)[0]
        reactants = [i.species for i in rpsbml.model.getReaction(largest_rp_reac_id).getListOfReactants()]
        sink_species = [i.getIdRef() for i in groups.getGroup(sink_species_group_id).getListOfMembers()]
        '''
        sink_molecules_inchikey = []
        for i in reactants:
            if i in sink_species:
                spec_annot = rpsbml.readBRSYNTHAnnotation(rpsbml.model.getSpecies(i).getAnnotation())
                if 'inchikey' in spec_annot:
                    sink_molecules_inchikey.append(spec_annot['inchikey'])
                #TODO: use other keys when the species does not have an inchikey
        '''
        for species_name in rpsbml.readUniqueRPspecies():
            species = rpsbml.model.getSpecies(species_name)
            brsynth_annot = rpsbml.readBRSYNTHAnnotation(species.getAnnotation())
            miriam_annot = rpsbml.readMIRIAMAnnotation(species.getAnnotation())
            # Build the node ID -- Based on if available the inchikey, else on MNX crosslinks
            if not 'inchikey' in brsynth_annot:
                try:
                    node_id = sorted(miriam_annot['metanetx'], key=lambda x: int(x.replace('MNXM', '')))[0]
                except KeyError:
                    try:
                        node_id = sorted(miriam_annot['chebi'], key=lambda x: int(x.replace('CHEBI:', '')))[0]
                    except KeyError:
                        logging.error('Could not assign a valid id, chemical node skipped')
                        continue
            else:
                node_id = brsynth_annot['inchikey']
            # Make a new node in the chemical has never been met yet
            if node_id not in chem_nodes:
                node = dict()
                node['id'] = node_id
                node['path_ids'] = [rpsbml.modelName]
                node['type'] = 'chemical'
                node['label'] = node_id
                node['all_labels'] = [node_id]
                node['svg'] = ''
                node['xlinks'] = []
                for xref in miriam_annot:
                    if xref=='reactome':
                        continue
                    if xref=='metacyc':
                        continue
                    for ref in miriam_annot[xref]:
                        try:
                            if not all([xref=='bigg', len(ref.split('_'))>1]):
                                #print(xref)
                                if xref=='kegg' and ref[0]=='C':
                                    url_str = 'http://identifiers.org/'+miriam_header['species']['kegg_c']+ref
                                elif xref=='kegg' and ref[0]=='D':
                                    url_str = 'http://identifiers.org/'+miriam_header['species']['kegg_d']+ref
                                else:
                                    url_str = 'http://identifiers.org/'+miriam_header['species'][xref]+ref
                                node['xlinks'].append({
                                    'db_name': xref,
                                    'entity_id': ref,
                                    'url': url_str})
                        except KeyError:
                            pass
                node['rsmiles'] = None
                node['rule_id'] = None
                node['ec_numbers'] = None
                node['thermo_dg_m_gibbs'] = None
                #node['fba_reaction'] = None
                node['rule_score'] = None
                try:
                    node['smiles'] = brsynth_annot['smiles']
                except KeyError:
                    node['smiles'] = None
                try:
                    node['inchi'] = brsynth_annot['inchi']
                except KeyError:
                    node['inchi'] = None
                try:
                    node['inchikey'] = brsynth_annot['inchikey']
                except KeyError:
                    node['inchikey'] = None
                #TODO: need a better way if not TARGET in name
                if species_name[:6] == 'TARGET':  
                    node['target_chemical'] = 1
                else:
                    node['target_chemical'] = 0
                node['cofactor'] = 0
                #check the highest RP{\d} reactants and ignore cofactors
                #TODO: not great but most time inchikey is the key
                if species_name in sink_species:
                    node['sink_chemical'] = 1
                else:
                    node['sink_chemical'] = 0
                # Store
                chem_nodes[node_id] = node
            # Else update already existing node
            else:
                if rpsbml.modelName not in chem_nodes[node_id]['path_ids']:
                    chem_nodes[node_id]['path_ids'].append(rpsbml.modelName)
                # TODO: manage xref, without adding duplicates
                try:
                    assert brsynth_annot.get('smiles', None) == chem_nodes[node_id]['smiles']
                except AssertionError:
                    try:
                        msg = 'Not the same SMILES: {} vs. {}'.format(
                            brsynth_annot['smiles'],
                            chem_nodes[node_id]['smiles']
                        )
                        logging.warning(msg)
                    except KeyError:
                        logging.warning('The brsynth_annot has no smiles: ' + str(node_id))
                        logging.info(brsynth_annot)
                try:
                    assert brsynth_annot.get('inchi', None) == chem_nodes[node_id]['inchi']
                except AssertionError:
                    try:
                        msg = 'Not the same INCHI: {} vs. {}'.format(
                            brsynth_annot['inchi'],
                            chem_nodes[node_id]['inchi']
                        )
                        logging.warning(msg)
                    except KeyError:
                        logging.warning('The brsynth_annot has no inchi: ' + str(node_id))
                        logging.info(brsynth_annot)
                try:
                    assert brsynth_annot.get('inchikey', None) == chem_nodes[node_id]['inchikey']
                except AssertionError:
                    try:
                        msg = 'Not the same INCHIKEY: {} vs. {}'.format(
                            brsynth_annot['inchikey'],
                            chem_nodes[node_id]['inchikey']
                        )
                        logging.warning(msg)
                    except KeyError:
                        logging.warning('The brsynth_annot has no inchi: ' + str(node_id))
                        logging.info(brsynth_annot)
            # Keep track for pathway info
            if node_id not in pathways_info[rpsbml.modelName]['node_ids']:
                pathways_info[rpsbml.modelName]['node_ids'].append(node_id)
        ################### EDGES ###########################
        for reaction_name in rpsbml.readRPpathwayIDs():
            reaction = rpsbml.model.getReaction(reaction_name)
            reac_species = rpsbml.readReactionSpecies(reaction)
            reac_brsynth_annot = rpsbml.readBRSYNTHAnnotation(reaction.getAnnotation())
            reac_miriam_annot = rpsbml.readMIRIAMAnnotation(reaction.getAnnotation())
            # Deduce reaction ID -- TODO: make this more robust
            if not 'smiles' in reac_brsynth_annot:
                try:
                    reac_nodeid = sorted(reac_miriam_annot['metanetx'], key=lambda x: int(x.replace('MNXR', '')))[0]
                except KeyError:
                    logging.warning('Could not assign valid id')
                    continue
            else:
                reac_nodeid = reac_brsynth_annot['smiles']
            # Iterate over chemicals linked to the reaction as substrate
            for spe in reac_species['left']:
                species = rpsbml.model.getSpecies(spe)
                spe_brsynth_annot = rpsbml.readBRSYNTHAnnotation(species.getAnnotation())
                spe_miriam_annot = rpsbml.readMIRIAMAnnotation(species.getAnnotation())
                # Deduce chemical ID -- TODO: make this more robust
                if not 'inchikey' in spe_brsynth_annot:
                    try:
                        spe_nodeid = sorted(spe_miriam_annot['metanetx'], key=lambda x: int(x.replace('MNXM', '')))[0]
                    except KeyError:
                        logging.warning('Could not assign a valid ID, edge skipped')
                        continue
                else:
                    spe_nodeid = spe_brsynth_annot['inchikey']
                # Build the edge ID
                node_id = spe_nodeid + '_' + reac_nodeid
                # Build a new node if this edge has never been met yet
                if node_id not in edges_nodes:
                    node = dict()
                    node['id'] = node_id
                    node['path_ids'] = [rpsbml.modelName]
                    node['source'] = spe_nodeid
                    node['target'] = reac_nodeid
                    # Store the new node
                    edges_nodes[node_id] = node
                # Else, update the already existing node
                else:
                    if rpsbml.modelName not in edges_nodes[node_id]['path_ids']:
                        edges_nodes[node_id]['path_ids'].append(rpsbml.modelName)
                    try:
                        assert spe_nodeid == edges_nodes[node_id]['source']
                    except AssertionError:
                        logging.warning('Unexpected issue met, but execution still continued')
                    try:
                        assert reac_nodeid == edges_nodes[node_id]['target']
                    except AssertionError:
                        logging.warning('Unexpected issue met, but execution still continued')
                # Keep track for pathway info
                if rpsbml.modelName not in pathways_info[rpsbml.modelName]['edge_ids']:
                    pathways_info[rpsbml.modelName]['edge_ids'].append(node_id)
            # Iterate over chemicals linked to the reaction as product
            for spe in reac_species['right']:
                species = rpsbml.model.getSpecies(spe)
                spe_brsynth_annot = rpsbml.readBRSYNTHAnnotation(species.getAnnotation())
                spe_miriam_annot = rpsbml.readMIRIAMAnnotation(species.getAnnotation())
                # Deduce chemical ID -- TODO: make this more robust
                if not 'inchikey' in spe_brsynth_annot:
                    try:
                        spe_nodeid = sorted(spe_miriam_annot['metanetx'], key=lambda x: int(x.replace('MNXM', '')))[0]
                    except KeyError:
                        logging.warning('Could not assign a valid ID, edge skipped')
                        continue
                else:
                    spe_nodeid = spe_brsynth_annot['inchikey']
                # Build the edge ID
                node_id = reac_nodeid + '_' + spe_nodeid
                # Build a new node if this edge has never been met yet
                if node_id not in edges_nodes:
                    node = dict()
                    node['id'] = node_id
                    node['path_ids'] = [rpsbml.modelName]
                    node['source'] = reac_nodeid
                    node['target'] = spe_nodeid
                    # Store the new node
                    edges_nodes[node_id] = node
                else:
                    if rpsbml.modelName not in edges_nodes[node_id]['path_ids']:
                        edges_nodes[node_id]['path_ids'].append(rpsbml.modelName)
                    try:
                        assert reac_nodeid == edges_nodes[node_id]['source']
                    except AssertionError:
                        logging.warning('Unexpected issue met, but execution still continued, mark A')
                    try:
                        assert spe_nodeid == edges_nodes[node_id]['target']
                    except AssertionError:
                        logging.warning('Unexpected issue met, but execution still continued, mark B')
                # Keep track for pathway info
                if rpsbml.modelName not in pathways_info[rpsbml.modelName]['edge_ids']:
                    pathways_info[rpsbml.modelName]['edge_ids'].append(node_id)

    # Finally store nodes
    for node in reac_nodes.values():
        network['elements']['nodes'].append({'data': node})
    for node in chem_nodes.values():
        network['elements']['nodes'].append({'data': node})
    for edge in edges_nodes.values():
        network['elements']['edges'].append({'data': edge})

    # Finally, sort node and edge IDs everywhere
    try: 
        network_backup = network.copy()
        for node in network['elements']['nodes']:
            node['data']['path_ids'] = sorted(node['data']['path_ids'], key=lambda x: [int(s) for s in x.split('_')[1:]])
        for node in network['elements']['edges']:
            node['data']['path_ids'] = sorted(node['data']['path_ids'], key=lambda x: [int(s) for s in x.split('_')[1:]])
    except ValueError:
        logging.warning('Cannot reorder pathway IDs into node and edge items, skipped')
        network = network_backup.copy()

    # Finally, sort pathway_info by pathway ID
    try:
        pathways_info_ordered = OrderedDict()
        path_ids_ordered = sorted(pathways_info.keys(), key=lambda x: [int(s) for s in x.split('_')[1:]])
        for path_id in path_ids_ordered:
            pathways_info_ordered[path_id] = pathways_info[path_id]
    except ValueError:
        logging.warning('Cannot reorder pathway_info according to pathway IDs, skipped.')
        pathways_info_ordered = pathways_info

    return network, pathways_info_ordered


def annotate_cofactors(network, cofactor_file):
    """Annotate cofactors based on structures listed in the cofactor file.

    :param network: dict, network of elements as outputted by the sbml_to_json method
    :param cofactor_file: str, file path
    :return: dict, network annotated
    """
    if not os.path.exists(cofactor_file):
        logging.error('Cofactor file not found: {}'.format(cofactor_file))
        return network
    # Collect cofactor structures
    cof_inchis = set()
    with open(cofactor_file, 'r') as ifh:
        reader = csv.reader(ifh, delimiter='\t')
        for row in reader:
            if row[0].startswith('#'):  # Skip comments
                continue
            try:
                assert row[0].startswith('InChI')
            except AssertionError:
                msg = 'Cofactor skipped, depiction is not a valid InChI for row: {}'.format(row)
                logging.info(msg)
                continue  # Skip row
            cof_inchis.add(row[0])
    # Match and annotate network elements
    for node in network['elements']['nodes']:
        if node['data']['type'] == 'chemical' and node['data']['inchi'] is not None:
            match = False
            for cof_inchi in cof_inchis:
                if node['data']['inchi'].find(cof_inchi) > -1:  # Match
                    node['data']['cofactor'] = 1
                    match = True
                    continue
            if match:
                continue  # Optimisation

    return network


def annotate_chemical_svg(network):
    """Annotate chemical nodes with SVGs depiction.

    :param network: dict, network of elements as outputted by the sbml_to_json method
    :return: dict, network annotated
    """
    from rdkit.Chem import MolFromInchi
    from rdkit.Chem.Draw import rdMolDraw2D
    from rdkit.Chem.AllChem import Compute2DCoords
    from urllib import parse

    for node in network['elements']['nodes']:
        if node['data']['type'] == 'chemical' and node['data']['inchi'] is not None:
            inchi = node['data']['inchi']
            try:
                mol = MolFromInchi(inchi)
                # if mol is None:
                #     raise BaseException('Mol is None')
                Compute2DCoords(mol)
                drawer = rdMolDraw2D.MolDraw2DSVG(200, 200)
                drawer.DrawMolecule(mol)
                drawer.FinishDrawing()
                svg_draft = drawer.GetDrawingText().replace("svg:", "")
                svg = 'data:image/svg+xml;charset=utf-8,' + parse.quote(svg_draft)
                node['data']['svg'] = svg
            except BaseException as e:
                msg = 'SVG depiction failed from inchi: "{}"'.format(inchi)
                logging.warning(msg)
                logging.warning("Below the RDKit backtrace...")
                logging.warning(e)
                node['data']['svg'] = None

    return network


def get_autonomous_html(ifolder):
    """Merge all needed file into a single HTML
    
    :param ifolder: folder containing the files to be merged
    :return html_str: string, the HTML
    """
    # find and open the index file 
    htmlString = open(ifolder + '/index.html', 'rb').read() 
    # open and read JS files and replace them in the HTML
    jsReplace = [
                 'js/chroma-2.1.0.min.js',
                 'js/cytoscape-3.12.1.min.js',
                 'js/cytoscape-dagre-2.2.1.js',
                 'js/dagre-0.8.5.min.js',
                 'js/jquery-3.4.1.min.js', 
                 'js/jquery-ui-1.12.1.min.js',
                 'js/jquery.tablesorter-2.31.2.min.js',
                 'js/viewer.js'
                ]
    for js in jsReplace:
        jsString = open(ifolder + '/' + js, 'rb').read()
        ori = b'src="' + js.encode() + b'">'
        rep = b'>' + jsString
        htmlString = htmlString.replace(ori, rep)
    # open and read style.css and replace it in the HTML
    cssReplace = ['css/jquery.tablesorte.theme.default-2.31.2.min.css',
                  'css/viewer.css']
    for css_file in cssReplace:
        cssBytes = open(ifolder + '/' + css_file, 'rb').read() 
        ori = b'<link href="' + css_file.encode() + b'" rel="stylesheet" type="text/css"/>'
        rep = b'<style type="text/css">' + cssBytes + b'</style>'
        htmlString = htmlString.replace(ori, rep)
    ### replace the network
    netString = open(ifolder + '/network.json', 'rb').read()
    ori = b'src="' + 'network.json'.encode() + b'">'
    rep = b'>' + netString
    htmlString = htmlString.replace(ori, rep)
    return htmlString


if __name__ == '__main__':

    pass
