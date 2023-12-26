/*jshint esversion: 6 */

class PathwayHandler {

     /** 
     * @param {cytoscape.js object} cy
     * @param {json structure} pathways_info 
     */
    constructor(cy, pathways_info){
        // List of the class attributes
        this.cy = cy;
        this.all_path_ids = new Set()
        this.path_to_edges = new Object()
        this.path_to_nodes = new Object()
        this.path_to_scores = new Object()
        this.pinned_path_ids = new Set()
        
        for (let path_id in pathways_info){
            if (this.all_path_ids.has(path_id)){
                console.log('path_id already referenced: ' + path_id);
            } else {
                // Path ID itselft
                this.all_path_ids.add(path_id);
                // List involved edges and nodes
                let info = pathways_info[path_id];
                this.path_to_edges[path_id] = info['edge_ids'];
                this.path_to_nodes[path_id] = info['node_ids'];
                // Extract scores
                this.path_to_scores[path_id] = info['scores'];
                // Set specific data field in the cytoscape object
                cy.elements().data('pinned', 0);
            }
        }
    }

    /**
     * Get the list of pinned pathways
     */
    get_pinned_paths(){
        return [...this.pinned_path_ids];
    }

    /**
     * Add one or more pinned pathways
     * 
     * @param {Array} path_ids
     */
    add_pinned_paths(path_ids){
        // Update path ids
        path_ids.forEach((path_id) => {
            this.pinned_path_ids.add(path_id);
        }, this);
        // Update the "pinned" status of nodes and edges
        path_ids.forEach((path_id) => {
            let node_ids = this.path_to_nodes[path_id];
            let edge_ids = this.path_to_edges[path_id];
            let element_ids = new Set([...node_ids, ...edge_ids]);
            element_ids.forEach((ele_id) => {
                let element = this.cy.getElementById(ele_id);
                element.data('pinned', 1);
            }, this);
        }, this);
        return true
    }

    /**
     * Remove one or more pinned pathways
     * 
     * @param {Array} path_ids: list of pathway IDs
     */
    remove_pinned_paths(path_ids){
        // Update path ids
        path_ids.forEach((path_id) => {
            this.pinned_path_ids.delete(path_id);
        }, this);
        // Update the "pinned" status of nodes and edges
        path_ids.forEach((path_id) => {
            let node_ids = this.path_to_nodes[path_id];
            let edge_ids = this.path_to_edges[path_id];
            let element_ids = new Set([...node_ids, ...edge_ids]);
            element_ids.forEach((element_id) => {
                if (! this.involved_in_any_pinned_path(element_id)){  // knowing we already removed the path_id from the list pinned path 
                    this.cy.getElementById(element_id).data('pinned', 0);
                }
            }, this);
        }, this);
        return true
    }

    /**
     * To know if an element is involved in at least one pinned path
     * 
     * @param {string} element_id: cytoscape element ID
     */
    involved_in_any_pinned_path(element_id){
        let path_ids = this.cy.getElementById(element_id).data('path_ids')  // returns a list
        for (let i = 0; i < path_ids.length; i++){
            if (this.pinned_path_ids.has(path_ids[i])){
                return true
            }
        }
        return false
    }

    /** 
     * Update the visibility of pinned elements
     */
    update_pinned_elements(){
        // If no any element pinned, unfade everything
        if (this.cy.elements('[pinned = 1]').length == 0){
            this.cy.elements().forEach((element) => {
                element.removeClass('faded');
            })
            return true;
        }
        // Otherwise, separate the grain from the bran
        this.cy.elements('[pinned = 1]').forEach((element) => {
            element.removeClass('faded');
        });
        this.cy.elements('[pinned = 0]').forEach((element) => {
            element.addClass('faded');
        });
    }

    /**
     * Highlight "even more" a particular set of pathways, new algo
     * 
     * @param {Array} path_ids 
     */
    highlight_pathways(path_ids=[]){
        // No pathway to highlight
        if (path_ids.length == 0){
            this.cy.edges('[highlighted = 1]').forEach((edge) => {
                edge.data('highlighted', 0);
                edge.removeClass('highlighted');
            });
            this.cy.nodes('[highlighted = 1]').forEach((node) => {
                node.data('highlighted', 0);
            });
            this.update_pinned_elements();
            return true;
        }

        // No pinned pathways
        if (this.pinned_path_ids.size == 0){
            this.cy.elements().addClass('faded');
        }

        //
        path_ids.forEach((path_id) => {
            let edge_ids = this.path_to_edges[path_id];
            let node_ids = this.path_to_nodes[path_id];
            let element_ids = new Set([...node_ids, ...edge_ids]);
            element_ids.forEach((element_id) => {
                let element = this.cy.getElementById(element_id);
                element.data('highlighted', 1);
            }, this);
        }, this);

        this.cy.edges('[highlighted = 1]').forEach((edge) => {
            edge.addClass('highlighted');
            edge.removeClass('faded');
        });
        this.cy.nodes('[highlighted = 1]').forEach((node) => {
            node.removeClass('faded');
        });
    }

    /** Colourise one pathway
     * 
     * @param {String} path_id: pathway ID
     * @param {string} colour_hex: colour in HTML hexadecical notation
     */
    colourise_one_pathwat(path_id, colour_hex){
        return true;
    }

    /**
     * Colourise a list pathways
     * 
     * @param {Array} path_ids: dictionary provided as a JSON
     * @param {String} score_label: the score label to use within available scores
     */
    colourise_pathways(path_ids, score_label='global_score'){
        let score_values = Object();
        // Shortand for all pathways
        if (path_ids == '__ALL__'){
            path_ids = [...this.all_path_ids];  // all_path_ids is a Set
        }
        // Collect and refine scores
        for (let i = 0; i < path_ids.length; i++){
            let path_id = path_ids[i];
            let score = this.path_to_scores[path_id][score_label];
            if (! isNaN(score)){
                let score_value = parseFloat(score);
                score_values[path_id] = score_value;
            }
        }
        // Sort path IDs by their values
        let items = Object.keys(score_values).map(function(key) {
            return [key, score_values[key]];
        });
        items.sort(function(first, second) {  // by inceasing order
            return first[1] - second[1];
        });
        // Set up the scale
        let list_of_values = [];
        for (let i = 0; i < items.length; i++){
            list_of_values.push(items[i][1]);
        }
        let min_score = Math.min(...list_of_values);
        let max_score = Math.max(...list_of_values);
        let colour_maker = chroma.scale(['red', 'yellow', 'blue']).domain([max_score, min_score]);
        // Finally colourise
        for (let i = 0; i < items.length; i++){
            // Get values
            let path_id = items[i][0];
            let score = items[i][1];
            // Get colour according to scale 
            let score_hex = colour_maker(score).hex();
            // Apply colour on edges
            let edge_ids = this.path_to_edges[path_id];
            edge_ids.forEach((edge_id) => {
                this.cy.getElementById(edge_id).style({
                    'line-color': score_hex,
                    'target-arrow-color': score_hex
                })
            }, this);
            // Apply colour on colour picker
            let colour_input = $('td.path_colour[data-path_id=' + path_id + '] > input')
            colour_input.val(score_hex);
        }
        return true;
    }

    /**
     * Reset all pathway colours to a same colour
     * 
     * @param {String} colour_hex: the hexadecimal colour to apply
     */
    reset_pathway_colours(colour_hex='#A9A9A9'){
        // Reset edge colours
        this.cy.edges().style({
            'line-color': colour_hex,
            'target-arrow-color': colour_hex
        });
        // Reset colour pickers
        $('td.path_colour > input').val(colour_hex);
        return true;
    }

};

// Utils ///////////////////////////

/**
 * Build the pathway table
 *
 * Derived from: http://jsfiddle.net/manishmmulani/7MRx6
 */
function build_pathway_table(){
    console.assert(pathways_info);
    $("#table_choice").empty();
    
    // Table skeleton
    let table_base = $('<table></table>');
    
    // Build the header
    let field_names = ['Pathway', 'Show', 'Colour', 'Steps', 'Score'];
    let field_classes = ['path_id_head', 'path_checkbox_head', 'path_colour_head', 'path_steps_head', 'path_value_head'];  // This is needed for tablesort
    let table_row = $('<tr></tr>');
    for (let i = 0; i < field_names.length; i++){
        let value = field_names[i];
        let class_ = field_classes[i];
        table_row.append($('<th class="' + class_ + '"></th>').html(value));
    }
    table_base.append($('<thead></thead>').append(table_row));
    
    // Build the body
    let table_body = $('<tbody></tbody>');
    for (let path_id in pathways_info){
        let info = pathways_info[path_id];
        let table_row = $('<tr></tr>');
        table_row.append($('<td class="path_id" data-path_id="' + path_id + '"></td>').html(path_id));
        table_row.append($('<td class="path_checkbox"></td>').append($('<input type="checkbox" name="path_checkbox" value=' + path_id + '>')));
        table_row.append($('<td class="path_colour" data-path_id="' + path_id + '"><input type="color" name="head" value="#A9A9A9"></td>'));
        table_row.append($('<td class="path_steps" data-path_id="' + path_id + '">'+String(info.nb_steps)+'</td>'));
        table_row.append($('<td class="path_value" data-path_id="' + path_id + '"></td>'));
        table_body.append(table_row);
    }
    table_base.append(table_body);
    // Append the content to the HTML
    $("#table_choice").append(table_base);
}

function build_detectable_info(node){
    $("#table_detectable_info").empty();

    // Table skeleton
    let table_base = $('<table></table>');

    // Build the header
    let field_names = ['Species', 'TF', 'Bibliographic', 'Database', 'NCBI', 'UniProt', 'AA Sequence'];
    let field_classes = ['Species_head', 'TF_head', 'Bibliographic_head', 'Database_head', 'NCBI_head', 'UniProt_head', 'AA Sequence_head'];
    let table_row = $('<tr></tr>');
    for (let i =0; i< field_names.length; i++){
        let value = field_names[i];
        let class_ = field_classes[i];
        table_row.append($('<th class="' + class_ + '"></th>').html(value));
    }
    table_base.append($('<thead></thead>').append(table_row));

    // Build the body
    let table_body = $('<tbody></tbody>');
    for (let i = 0; i <node.data('species').length; i++){
        let species = node.data('species')[i];
        let tf = node.data('tf')[i];
        let biblio_ref = node.data('biblio_ref')[i];
        let data_ref = node.data('data_ref')[i];
        let ncbi = node.data('ncbi')[i];
        let uniprot = node.data('uniprot')[i];
        let aa_seq = node.data('aa_seq')[i];
        let table_row = $('<tr></tr>');
        table_row.append($('<td class="species">'+species+'</td>'));
        table_row.append($('<td class="tf">'+tf+'</td>'));
        table_row.append($('<td class="biblio_ref">'+biblio_ref+'</td>'));
        table_row.append($('<td class="data_ref">'+data_ref+'</td>'));
        table_row.append($('<td class="ncbi">'+ncbi+'</td>'));
        table_row.append($('<td class="uniprot">'+uniprot+'</td>'));
        table_row.append($('<td class="aa_seq">'+aa_seq+'</td>'));
        table_body.append(table_row);
    }
    table_base.append(table_body);
    // Append the content to the HTML
    $("#table_detectable_info").append(table_base);
}

/**
 * Collect checked pathways
 */
function get_checked_pathways(){
    let selected_paths=[];
    $('input[name=path_checkbox]:checked').each(function(){
        let path_id = $(this).val();
        selected_paths.push(path_id);
    });
    return selected_paths;
}

/**
 * Reverse the visibility
 */
function reverse_visibility(element){
    if (element.style().visibility == 'visible'){
        element.css({visibility:'hidden'});
    } else {
        element.css({visibility:'visible'});
    }
}

/**
 * Get the collection of edges involved in a given path_id
 *
 * @param path_id (str): pathway ID
 * @param cy (cytoscape object): Cytoscape object
 */
function get_edges_from_path_id(path_id, cy){
    edges_col = cy.collection();
    cy.edges().forEach(function(edge, index){
        let edge_path_ids = edge.data('path_ids');
        if (share_at_least_one(edge_path_ids, [path_id])){
            edges_col = edges_col.union(edge);
        }
    });
    return edges_col;
}

/**
 * Get pinned pathways IDs
 */
function get_pinned_pathway_IDs(){
    let pinned_paths = [];
    $('td.pinned').each(function(){
        let path_id = $(this).text();
        pinned_paths.push(path_id);
    });
    return pinned_paths
}

/**
 * Put chemical info into the information panel
 */
function panel_chemical_info(node, show=false){
    if (show){
        // Collect
        let node_id = node.data('id');
        let label = node.data('label');
        let svg = node.data('svg');
        let smiles = node.data('smiles');
        let inchi = node.data('inchi');
        let inchikey = node.data('inchikey');
        if (node.data('cofactor') == 1){
            var cofactor = 'Yes';
        } else {
            var cofactor = 'No';
        }
        let xlinks = node.data('xlinks');
        let path_ids = node.data('path_ids');
        // Inject
        $("span.chem_info_label").html(label);
        if (inchikey == "" || inchikey == null){
            $("span.chem_info_inchikey").html("NA");
            $("span.chem_info_inchikey_search").html("");
        } else {
            $("span.chem_info_inchikey").html(inchikey);
            //$("span.chem_info_inchikey_search").html('<a target="_blank" href="http://www.google.com/search?q=' + encodeURI(inchikey) + '">Look for identical structure using Google</a>');
        }
        if (inchi == ""|| inchi == null){
            $("span.chem_info_inchi").html("NA");
            $("span.chem_info_inchi_search").html("");
        } else {
            $("span.chem_info_inchi").html(inchi);
            //$("span.chem_info_inchi_search").html('<a target="_blank" href="https://pubchem.ncbi.nlm.nih.gov/search/#collection=compounds&query_type=structure&query_subtype=identity&query=' + encodeURI(inchi) + '">Look for identical structure using PubChem</a>');
        }
        if (smiles == ""|| smiles == null){
            $("span.chem_info_smiles").html("NA");
            $("span.chem_info_smiles_search").html("");
        } else {
            $("span.chem_info_smiles").html(smiles);
            $("span.chem_info_smiles_search").html('<a target="_blank" href="https://pubchem.ncbi.nlm.nih.gov/search/#collection=compounds&query_type=structure&query_subtype=identity&query=' + encodeURI(smiles) + '">Look for identical structure using PubChem</a>');
        }        
        // Inject SVG depiction as a background image (if any)
        if (svg !== null && svg !== ""){
            $('div.img-box').show();
            $('div.chem_info_svg').css('background-image', "url('" + svg + "')");
        } else {
            $('div.img-box').hide();
        }
        // Inject crosslinks
        $("div.chem_info_xlinks").html('');  // Reset div content
        if (xlinks.length > 0){
            for (let i = 0; i < xlinks.length; i++){
                $("div.chem_info_xlinks").append('<a target="_blank" href="' + xlinks[i]['url'] + '">' + xlinks[i]['db_name'] + ':' + xlinks[i]['entity_id'] + '</a>');
                $("div.chem_info_xlinks").append('<br/>');
            }
        } else {
            $("div.chem_info_xlinks").append('None<br/>');
        }
        // Inject path IDs
        $("div.chem_info_pathids").html('');  // Reset div content
        if (path_ids.length > 0){
            for (let i = 0; i < path_ids.length; i++){
                $("div.chem_info_pathids").append(path_ids[i] + '<br/>');
            }
        } else {
            $("div.chem_info_pathids").append('None<br/>');
        }
        // Show
        $("#panel_chemical_info").show();
        document.getElementById("info").style.borderLeftStyle="solid";
        document.getElementById("info").style.borderBottomStyle="solid";
        document.getElementById("info").style.borderRightStyle="solid";
        document.getElementById("info").style.borderTopStyle="solid";
    } else {
        $("#panel_chemical_info").hide();
    }
}
/**
 * Put producible info into the information panel
 */
function panel_chemical_producible_info(node, show=true){
    if (show){
        // Collect
        let node_id = node.data('id');
        let label = node.data('label');
        let svg = node.data('svg');
        let smiles = node.data('smiles');
        let inchi = node.data('inchi');
        let inchikey = node.data('inchikey');
        let pmid = node.data('pmid');
        let kegg_id = node.data('keggid');
        let mnx_id = node.data('mnxid');
        // Inject
        $("span.chem_producible_info_label").html(label);
        if (inchikey == "" || inchikey == null){
            $("span.chem_info_inchikey").html("NA");
            $("span.chem_info_inchikey_search").html("");
        } else {
            $("span.chem_info_inchikey").html(inchikey);
            //$("span.chem_info_inchikey_search").html('<a target="_blank" href="http://www.google.com/search?q=' + encodeURI(inchikey) + '">Look for identical structure using Google</a>');
        }
        if (inchi == ""|| inchi == null){
            $("span.chem_info_inchi").html("NA");
            $("span.chem_info_inchi_search").html("");
        } else {
            $("span.chem_info_inchi").html(inchi);
            //$("span.chem_info_inchi_search").html('<a target="_blank" href="https://pubchem.ncbi.nlm.nih.gov/search/#collection=compounds&query_type=structure&query_subtype=identity&query=' + encodeURI(inchi) + '">Look for identical structure using PubChem</a>');
        }
        if (smiles == ""|| smiles == null){
            $("span.chem_info_smiles").html("NA");
            $("span.chem_info_smiles_search").html("");
        } else {
            $("span.chem_info_smiles").html(smiles);
            $("span.chem_info_smiles_search").html('<a target="_blank" href="https://pubchem.ncbi.nlm.nih.gov/search/#collection=compounds&query_type=structure&query_subtype=identity&query=' + encodeURI(smiles) + '">Look for identical structure using PubChem</a>');
        }
        if (pmid == "" || pmid == null){
            $("span.chem_info_pmid").html("NA");
        } else {
            $("span.chem_info_pmid").html('<a target="_blank" href="https://pubmed.ncbi.nlm.nih.gov/' + pmid+ '">'+pmid+'</a>');
        }
        if (kegg_id == "" || kegg_id == null){
            $("span.chem_info_keggid").html("NA");
        } else {
            $("span.chem_info_keggid").html('<a target="_blank" href="https://www.genome.jp/entry/' + kegg_id+ '">'+kegg_id+'</a>');
        }
        if (mnx_id == "" || mnx_id == null){
            $("span.chem_info_mnxid").html("NA");
        } else {
            $("span.chem_info_mnxid").html('<a target="_blank" href="https://www.metanetx.org/chem_info/' + mnx_id+ '">'+mnx_id+'</a>');
        }
        // Inject SVG depiction as a background image (if any)
        if (svg !== null && svg !== ""){
            $('div.img-box').show();
            $('div.chem_info_svg').css('background-image', "url('" + svg + "')");
        } else {
            $('div.img-box').hide();
        }
        // Inject Systemsbiotech reference
        $("span.chem_info_sbtreference").html('<a target="_blank" href="http://systemsbiotech.co.kr/"' + '">SystemsBioTech</a>');
        // Show
        $("#panel_chemical_producible_info").show();
        document.getElementById("info").style.borderLeftStyle="solid";
        document.getElementById("info").style.borderBottomStyle="solid";
        document.getElementById("info").style.borderRightStyle="solid";
        document.getElementById("info").style.borderTopStyle="solid";
    } else {
        $("#panel_chemical_producible_info").hide();
    }
} 
    
/**
 * Put detectable info into the information panel
 */
function panel_chemical_detectable_info(node, show=true){
    if (show){
        // Collect
        let node_id = node.data('id');
        let label = node.data('label');
        let svg = node.data('svg');
        let smiles = node.data('smiles');
        let inchi = node.data('inchi');
        let inchikey = node.data('inchikey');
        // Inject
        $("span.chem_detectable_info_label").html(label);
        if (smiles == ""|| smiles == null){
            $("span.chem_info_smiles").html("NA");
            $("span.chem_info_smiles_search").html("");
        } else {
            $("span.chem_info_smiles").html(smiles);
            $("span.chem_info_smiles_search").html('<a target="_blank" href="https://pubchem.ncbi.nlm.nih.gov/search/#collection=compounds&query_type=structure&query_subtype=identity&query=' + encodeURI(smiles) + '">Look for identical structure using PubChem</a>');
        }
        if (inchikey == "" || inchikey == null){
            $("span.chem_info_inchikey").html("NA");
            $("span.chem_info_inchikey_search").html("");
        } else {
            $("span.chem_info_inchikey").html(inchikey);
            //$("span.chem_info_inchikey_search").html('<a target="_blank" href="http://www.google.com/search?q=' + encodeURI(inchikey) + '">Look for identical structure using Google</a>');
        }
        if (inchi == ""|| inchi == null){
            $("span.chem_info_inchi").html("NA");
            $("span.chem_info_inchi_search").html("");
        } else {
            $("span.chem_info_inchi").html(inchi);
            //$("span.chem_info_inchi_search").html('<a target="_blank" href="https://pubchem.ncbi.nlm.nih.gov/search/#collection=compounds&query_type=structure&query_subtype=identity&query=' + encodeURI(inchi) + '">Look for identical structure using PubChem</a>');
        }
        // Inject SVG depiction as a background image (if any)
        if (svg !== null && svg !== ""){
            $('div.img-box').show();
            $('div.chem_info_svg').css('background-image', "url('" + svg + "')");
        } else {
            $('div.img-box').hide();
        }
        // Inject detectable table with info
        //build_detectable_info(node);
        // Show
        $("#panel_chemical_detectable_info").show();
        document.getElementById("info").style.borderLeftStyle="solid";
        document.getElementById("info").style.borderBottomStyle="solid";
        document.getElementById("info").style.borderRightStyle="solid";
        document.getElementById("info").style.borderTopStyle="solid";
    } else {
        $("#panel_chemical_detectable_info").hide();
    }
} 

/**
 * Put reaction info into the information panel
 */
function panel_reaction_info(node, show=true){
    if (show){
        // Collect
        let node_id = node.data('id');
        let label = node.data('label')
        let rsmiles = node.data('rsmiles');
        let rule_ids = node.data('rule_ids');
        let score = node.data('rule_score');
        let rxn_template_ids = node.data('rxn_template_ids');
        let path_ids = node.data('path_ids');
        let ec_numbers = node.data('ec_numbers');
        // Inject 
        $("span.reaction_info_rsmiles").html(rsmiles);
        // Reaction name
        $("span.reaction_info_name").html(label);
        // Rule IDs
        $("div.reaction_info_ruleids").html(rule_ids);  // Reset div content
        // Rule scores
        $("span.reaction_info_rule_score").html(score);
        // Reaction template IDs
        $("div.reaction_info_reaction_template_ids").html('');  // Reset div content
        for (let i = 0; i < rxn_template_ids.length; i++){
            $("div.reaction_info_reaction_template_ids").append(rxn_template_ids[i]);
        }
        // EC numbers
        $("div.reaction_info_ecnumbers").html('');  // Reset div content
        if (ec_numbers == null || ec_numbers.length == 0){
            $("div.reaction_info_ecnumbers").append('None<br/>');
        } else {
            for (let i = 0; i < ec_numbers.length; i++){
                $("div.reaction_info_ecnumbers").append(ec_numbers[i]);
            }
        }
        // Inject path IDs
        $("div.reaction_info_pathids").html('');  // Reset div content
        if (path_ids.length > 0){
            for (let i = 0; i < path_ids.length; i++){
                $("div.reaction_info_pathids").append(path_ids[i] + '<br/>');
            }
        } else {
            $("div.reaction_info_pathids").append('None<br/>');
        }
        // Selenzyme crosslink
        $("span.reaction_info_selenzyme_crosslink").html('<a target="_blank" href="http://selenzyme.synbiochem.co.uk/results?smarts=' + encodeURIComponent( rsmiles ) + '">Go to Selenzyme</a>');
        // Show
        $("#panel_reaction_info").show();
        document.getElementById("info").style.borderLeftStyle="solid";
        document.getElementById("info").style.borderBottomStyle="solid";
        document.getElementById("info").style.borderRightStyle="solid";
        document.getElementById("info").style.borderTopStyle="solid";
    } else {
        $("#panel_reaction_info").hide();
    }
}
/**
 * Write some default text message on the info panel
 */
function panel_startup_info(show=true){  // node
    if (show){
        $("#panel_startup_legend").show();
    } else {
        $("#panel_startup_legend").hide();
    }
    
}

/**
 * Return true if the array have at least one common items
 *
 * @param array1 (array): items
 * @param array2 (array): items
 */
function share_at_least_one(array1, array2){
    for (let i = 0; i < array1.length; i++){
        for (let j = 0; j < array2.length; j++){
            // We have  a match
            if (array1[i] == array2[j]){
                return true;
            }
        }
    }
    return false;
}

/**
 * Make labels for chemicals
 *
 * @param {Integer} max_length: string size cutoff before label truncation
function make_chemical_labels(max_length=6){
    let nodes = cy.nodes().filter('[type = "chemical"]');
    for (let i = 0; i < nodes.size(); i++){
        let node = nodes[i];
        let label = node.data('label');
        if ((typeof label != 'undefined') && (label != 'None') && (label != '')){
            if (label.length > max_length){
                short_label = label.substr(0, max_length-2)+'..';
            } else {
                short_label = label;
            }
        } else {
            short_label = '';
        }
        node.data('short_label', short_label);
    }
}
 */

/**
 * Make labels for reactions
 *
 * @param {Integer} max_length: string size cutoff before label truncation
 */
function make_reaction_labels(max_length=10){
    let nodes = cy.nodes().filter('[type = "reaction"]');
    for (let i = 0; i < nodes.size(); i++){
        let node = nodes[i];
        let label = node.data('label');
        if ((typeof label != 'undefined') && (label != 'None') && (label != '')){
            if (label.length > max_length){
                short_label = label.substr(0, max_length-2)+'..';
            } else {
                short_label = label;
            }
        } else {
            short_label = '';
        }
        node.data('short_label', short_label);
    }
}

function show_all_panels(){
    $("#panel_chemical_info").show();
    $("#panel_chemical_producible").show();
    $("#panel_reaction_info").show();
}

function hide_all_panel(){
    document.getElementById("info").style.borderLeftStyle="hidden";
    document.getElementById("info").style.borderBottomStyle="hidden";
    document.getElementById("info").style.borderTopStyle="hidden";
    document.getElementById("info").style.borderRightStyle="hidden";    
    document.getElementById("info").style.width="0%";  
    $("#panel_chemical_info").hide();
    $("#panel_chemical_producible").hide();
    $("#panel_reaction_info").hide();
}

function in_chassis(chassis='ECOLI'){
    let nodes = cy.nodes().filter('[type = "chemical"]');
    for (let n = 0; n < nodes.size(); n++){
        let in_sink = false;
        let node = nodes[n];
        let node_chassis = node.data('chassis');
        node_chassis = node_chassis.replace("['");
        node_chassis = node_chassis.replace("']");
        node_chassis = node_chassis.split("', '");
        for (let i = 0; i < node_chassis.length; i++){
            if (node_chassis[i] == chassis){
                in_sink = true;
            } else if (in_sink != true){
                in_sink = false;
            }
        }
        node.data('sink_chemical', in_sink);
    }
}
function count_intermediate(){
    let nodes = cy.nodes().filter('[type = "chemical"]');
    let suplement = 0;
    let in_chassis = 0;
    let intermediate = 0;
    let heterologous = 0;
    let precursor = 0;
    for (let n = 0; n < nodes.size(); n++){
        let node = nodes[n];
        if (node.data('inter_chemical')){
            suplement++;
        }else if (node.data('source_chemical') == false && node.data('target_chemical') == false && node.data('prod_path') == false){
            if (node.data('sink_chemical') && node.data('inter_ids').length ==0){
                in_chassis++;
                intermediate++;
            }else if (node.data('inter_ids').length ==0){
                heterologous++;
                intermediate++;
            }else {
                precursor++;
            }
        }
    }
    document.getElementById('txt_intermediate_compounds').innerHTML='Intermediate compounds: ' + String(intermediate);
    document.getElementById('txt_chassis_compounds').innerHTML='Compounds in chassis: ' + String(in_chassis);
    document.getElementById('txt_precursor_compounds').innerHTML='Precursor compounds: ' + String(precursor);
    document.getElementById('txt_suplement_compounds').innerHTML='Suplement compounds: ' + String(suplement);    
    document.getElementById('txt_heterologous_compounds').innerHTML='Heterologous compounds: ' + String(heterologous);
}

// Live ///////////////////////////
function run_viz(network, pathways_info){

    // Cytoscape object to play with all along
    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),
        motionBlur: true,
        wheelSensitivity: 0.25
    });

    // Basic stuff to do only once
    build_pathway_table();
    panel_startup_info(true);
    panel_chemical_info(null, false);
    panel_chemical_detectable_info(null, false);
    panel_chemical_producible_info(null, false);
    panel_reaction_info(null, false);
    init_network(true);
    annotate_hiddable_cofactors();  // Need to be done after init_network so the network is already loaded
    refresh_layout();
    hide_all_intermedia_pathways();
    hide_all_prod_pathways();
    show_cofactors(false);
    put_pathway_values('global_score');
    make_pathway_table_sortable();  // Should be called only after the table has been populated with values

    // Pathway Handler stuff
    window.path_handler = new PathwayHandler(cy, pathways_info);
    path_handler.colourise_pathways('__ALL__', 'global_score');

    /**
     * Initialise the network, but hide everything
     *
     * @param show_graph (bool): show the loaded network
     */
    function init_network(show_graph=true){
        // Reset the graph
        cy.json({elements: {}});
        cy.minZoom(1e-50);

        // Load the full network
        cy.json({elements: network['elements']});
        
        // Create node labels
        //make_chemical_labels(6);
        make_reaction_labels(9);
        
        // Hide them 'by default'
        if (! show_graph){
            show_pathways(selected_paths='__NONE__');
        } else {
            $('input[name=path_checkbox]').prop('checked', true);  // Check all
        }
        
        // Annotate which nodes are on the chassis
        in_chassis('ECOLI');
        // Once the layout is done:
        // * set the min zoom level
        // * put default info
        cy.on('layoutstop', function(e){
            cy.minZoom(cy.zoom());
        });
        
        cy.style(
            cytoscape.stylesheet()
                .selector("node[type='reaction']")
                    .css({
                        'height': 60,
                        'width': 120,
                        'shape': 'cut-rectangle',
                        'background-color': 'white',
                        'border-width': 2,
                        'border-color': 'gray',
                        'border-style': 'solid',
                        'content': 'data(short_label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'text-opacity': 1,
                        'color': '#333333',
                        'font-size': '20px',
                    })
                .selector("node[type='chemical']")
                    .css({
                        'background-color': '#52be80',
                        'background-fit':'contain',
                        'shape': 'ellipse',
                        'width': 80,
                        'height': 80,
                        'label': 'data(short_label)',
                        'font-size': '14px',
                        // 'font-weight': 'bold',
                        'text-valign': 'bottom',
                        'text-halign': 'center',
                        'text-margin-y': 8,
                        'text-opacity': 1,
                        'text-background-color': 'White',
                        'text-background-opacity': 0.85,
                        'text-background-shape': 'roundrectangle',
                        'border-width': 4,
                    })
                .selector("node[type='chemical']")  // ie: intermediates
                    .css({
                        'background-color': '#333333',
                        'border-color': '#333333',
                    })  
                .selector("node[type='chemical'][?sink_chemical]")
                    .css({
                        'background-color': '#83d334',
                        'border-color': '#83d334',
                    })
                .selector("node[type='chemical'][?target_chemical]")
                    .css({
                        'background-color': '#CC3333',
                        'border-color': '#CC3333',
                    })
                .selector("node[type='chemical'][?source_chemical]")
                    .css({
                        'background-color': '#41bedb',
                        'border-color': '#41bedb',
                    })
                .selector("node[type='chemical'][?inter_chemical]")
                    .css({
                        'background-color': '#FFCC33',
                        'border-color': '#FFCC33',
                    })
                .selector("node[type='chemical'][?svg]")  // The beauty of it: "?" will match only non null values
                    .css({
                        'background-image': 'data(svg)',
                        'background-fit': 'contain',
                        'border-width': 4,
                    })
                .selector('edge')
                    .css({
                        'curve-style': 'unbundled-bezier',
                        'line-color': '#999999',
                        'line-fill': 'solid',
                        'line-gradient-stop-colors': 'cyan magenta',
                        'line-gradient-stop-positions': '0% 100%',
                        'width': '2px',
                        'target-arrow-shape': 'chevron',
                        'target-arrow-color': '#999999',
                        'arrow-scale' : 2
                    })                    
                .selector('.faded')
                    .css({
                        'opacity': 0.15,
                        'text-opacity': 0.25
                    })
                .selector('.highlighted')
                    .css({
                        'width': '9px'
                    })
                .selector('node:selected')
                    .css({
                        'border-width': 4,
                        'border-color': 'black'
                    })
        );
        
        cy.on('tap', 'node', function(evt){
            let node = evt.target;
            // Dump into console
            console.log(node.data());
            // Print info
            document.getElementById("info").style.width="18%";
            if (node.is('[type = "chemical"]')){
                panel_startup_info(false);
                panel_reaction_info(null, false);
                if (node.data().source_chemical) {
                    if (node.data().target_chemical){
                        node.data().target_chemical = false
                    } else {
                        node.data().target_chemical = true
                    }
                    panel_chemical_info(null, false);
                    panel_chemical_producible_info(node, true);    
                    panel_chemical_detectable_info(null, false);
                    show_prod_pathway()
                } else if (node.data().target_chemical){
                    panel_chemical_detectable_info(node, true);
                    panel_chemical_info(null, false);
                    panel_chemical_producible_info(null, false);   
                } else {
                    panel_chemical_info(node, true);
                    panel_chemical_producible_info(null, false);
                    panel_chemical_detectable_info(null, false);
                }
                if (node.data().inter_chemical){
                    show_intermedia_pathways(node.data().inter_ids) 
                }
            } else if (node.is('[type = "reaction"]')){
                panel_startup_info(false);
                panel_chemical_info(null, false);
                panel_chemical_producible_info(null, false);
                panel_chemical_detectable_info(null, false)
                panel_reaction_info(node, true);
            }
            count_intermediate();
        });

        cy.on('tap', 'edge', function(evt){
            let edge = evt.target;
            console.log(edge.data());
        });
        
        cy.on('mouseover', 'node', function(evt){            
        })
    }
    
    /**
     * Trigger a layout rendering
     * 
     * @param {cytoscape collection} element_collection: a collection of elements.
     */
    function render_layout(element_collection){
        // Playing with zoom to get the best fit
        cy.minZoom(1e-50);
        cy.on('layoutstop', function(e){

            cy.minZoom(cy.zoom()*0.5);  // 0.9 to enable the user dezoom a little

        });
        // Layout
        let layout = element_collection.layout({
            name: 'breadthfirst',
            roots: cy.elements("node[?target_chemical]")
        });
        layout.run();
    }
        
    /** Load a metabolic network
     *
     * Only nodes and edges involved in 'selected_paths' will be displayed.
     *
     * @param selected_paths (array or str): path IDs or special flags
     */
    function show_pathways(selected_paths='__ALL__'){
      
        if (selected_paths == '__ALL__'){
            cy.nodes().forEach(function(node, index){
                let length_paths = node.data('inter_ids').length;
                if (length_paths != 0 && node.data('inter_chemical') != true && node.style().visibility == 'visible'){
                    node.css({visibility:'visible'});
                } else if (length_paths != 0 && node.data('inter_chemical') != true && node.style().visibility == 'hidden'){
                    node.css({visibility:'hidden'});
                } else if ((length_paths == 0 || node.data('inter_chemical') == true) && node.data('prod_path') == false){
                node.css({visibility:'visible'});
                }
            });
            cy.edges().forEach(function(edge,index){
                let length_paths = edge.data('inter_ids').length;
                if (length_paths != 0 && edge.style().visibility == 'visible'){
                    edge.css({visibility:'visible'});
                } else if (length_paths != 0 && edge.style().visibility == 'hidden'){
                    edge.css({visibility:'hidden'});
                } else if (length_paths == 0 && edge.data('prod_path') == false){
                    edge.css({visibility:'visible'});
                }
            });
            refresh_layout()          
        } else if (selected_paths == '__NONE__'){
            cy.nodes().css({visibility: 'hidden'});
            cy.edges().css({visibility: 'hidden'});
        } else {
            // Nodes
            cy.nodes().forEach(function(node, index){
                let node_paths = node.data('path_ids');
                if (share_at_least_one(node_paths, selected_paths)){
                    node.css({visibility:'visible'});
                } else {
                    node.css({visibility:'hidden'});
                }
            });
            // Edges
            cy.edges().forEach(function(edge, index){
                let edge_paths = edge.data('path_ids');
                if (share_at_least_one(edge_paths, selected_paths)){
                    edge.css({visibility:'visible'});
                } else {
                    edge.css({visibility:'hidden'});
                }
            });
        }
    }
    
    /**
     * Hide all intermedia pathways
     */
    function hide_all_intermedia_pathways(){
        cy.nodes().forEach(function(node, index){
            let length_paths = node.data('inter_ids').length;
            if (length_paths != 0 && node.data('main_path') != true){
                node.css({visibility:'hidden'});
            }
        });
        cy.edges().forEach(function(edge,index){
            let length_paths = edge.data('inter_ids').length;
            if (length_paths != 0){
                edge.css({visibility:'hidden'});
            }
        });
    }

    function hide_all_prod_pathways(){
        cy.nodes().forEach(function(node, index){
            if (node.data('prod_path') && node.data('source_chemical') != true){
                node.css({visibility:'hidden'});
            }
        });
        cy.edges().forEach(function(edge,index){
            if (edge.data('prod_path')){
                edge.css({visibility:'hidden'});
            }
        });
    }
    
    function show_prod_pathway(){
        cy.nodes().forEach(function(node, index){
            let length_paths = node.data('inter_ids').length;
            if (node.data('source_chemical') != true && (length_paths == 0 || node.data('main_path'))){
                reverse_visibility(node);
            }
            if (length_paths != 0 && node.data('main_path') != true){
                node.css({visibility:'hidden'});
            }
        });
        cy.edges().forEach(function(edge, index){
            let length_paths = edge.data('inter_ids').length;
            if (length_paths == 0){
                reverse_visibility(edge)
            } else {
                edge.css({visibility:'hidden'});
            }
        });
        refresh_layout();
    }

    /**
     * Add intermediate pathways to the network
     */
    function show_intermedia_pathways(selected_paths){
        cy.nodes().forEach(function(node, index){
            let node_paths = node.data('inter_ids');
            if (share_at_least_one(node_paths, selected_paths)){
                if (node.data('main_path') != true){
                    reverse_visibility(node)
                }
            }
        });
        cy.edges().forEach(function(edge, index){
            let edge_paths = edge.data('inter_ids');
            if (share_at_least_one(edge_paths, selected_paths)){
                reverse_visibility(edge)
            }
        });
        //refresh_layout()
    }

    /**
     * Tag cofactor weither there could be hidden or not 
     *
     * If hidding cofactors lead to lonely / unconnected reactions then 
     * cofactors related to sucbh reaction are marked as not hiddable.
     * Otherwise, cofactors are marked as hiddable.
     */
    function annotate_hiddable_cofactors(){
        cy.elements('node[type = "reaction"]').forEach((rxn_node, i) => {
            // Check
            let in_not_cof = rxn_node.incomers().filter('node[?cofactor]');
            let out_not_cof = rxn_node.outgoers().filter('node[?cofactor]');
            // Decide
            let hiddable;
            if (in_not_cof.length == 0 || out_not_cof.length == 0){
                hiddable = 0;
            } else {
                hiddable = 1;
            }
            // Tag
            let in_chems = rxn_node.incomers().filter('node');
            in_chems.forEach((chem_node, j) => {
                if (
                    chem_node.data('cofactor') == 1 &&
                    chem_node.data('hiddable_cofactor') != 0
                ){
                    chem_node.data('hiddable_cofactor', hiddable);
                }
            });
            let out_chems = rxn_node.outgoers().filter('node');
            out_chems.forEach((chem_node, j) => {
                if (
                    chem_node.data('cofactor' == 1) &&
                    chem_node.data('hiddable_cofactor') != 0
                ){
                    chem_node.data('hiddable_cofactor', hiddable);
                }
            });
        });
    }

    /** Handle cofactor display
     *
     * Hide of show all nodes annotated as cofactor
     *
     * @param show (bool): will show cofactors if true
     */
    function show_cofactors(show=true){
        if (show){
            cy.elements().style("display", "element");
        } else {
            cy.elements('node[?cofactor][?hiddable_cofactor]').style("display", "none");
        }
        refresh_layout();
    }

    /**
     * Make the pathway table sortable
     */
    function make_pathway_table_sortable(){
        $("#table_choice > table").tablesorter({
            theme : 'default',
            sortList: [[4,1],[0,0]],  // Sort on the fourth column (descending) and then on the first column (ascending order)
            headers : {  // Disable sorting for these columns
                '.path_checkbox_head, .path_colour_head': {
                    sorter: false
                }
            }
        });
    }
    
    /**
     * Refresh layout according to visible nodes
     */
    function refresh_layout(){
        render_layout(cy.elements().not(':hidden'));
    }
    
    // When a pathway is checked
    $("input[name=path_checkbox]").change(function(){
        selected_paths = get_checked_pathways();
        show_pathways(selected_paths);
    });
    
    /** 
     * Pathway visibility is updated when a pathway label is hovered
     * 
     * Note: the hover CSS is handled in the CSS file.
     * Node: some vocabulary precisions, pinned stands for path ID locked "on",
     *      while highlighted stands for the path ID currently hovered
     */
    $("td.path_id").hover(function(){
        let path_id = $(this).data('path_id');
        path_handler.highlight_pathways([path_id]);

    }, function(){
        let path_id = $(this).data('path_id');
        path_handler.highlight_pathways([]);
    });
    
    /**
     * Pathway are pinned on click
     */
    $("td.path_id").click(function(){
        let path_id = $(this).data('path_id');
        // Removing
        if ($(this).hasClass('pinned')){
            $(this).removeClass('pinned');
            path_handler.remove_pinned_paths([path_id]);
            path_handler.update_pinned_elements();
        // Adding
        } else {
            path_handler.add_pinned_paths([path_id]);
            path_handler.update_pinned_elements();
            $(this).addClass('pinned');
        }
    });
            
    // Pathways selection
    $('#hide_all_pathways_button').on('click', function(event){
        show_pathways(selected_paths='__NONE__');  // Hide all
        $('input[name=path_checkbox]').prop('checked', false);  // Uncheck all
    });
    $('#view_all_pathways_button').on('click', function(event){
        show_pathways(selected_paths='__ALL__');  // Show all
        $('input[name=path_checkbox]').prop('checked', true);  // Check all
    });
    $('#redraw_pathways_button').on('click', function(event){
        refresh_layout();
    });
    
    // Cofactors handling
    $('#show_cofactors_button').on('click', function(event){
        show_cofactors(true);
        // Update visible pathways to update their cofactor nodes visibility
        selected_paths = get_checked_pathways();
        show_pathways(selected_paths);
        // Update hilighted pathways to update their cofactor nodes status
        path_handler.update_pinned_elements();
    });
    $('#remove_cofactors_button').on('click', function(event){
        show_cofactors(false);
    });
    
    // Manual colour handling
    colour_pickers = document.querySelectorAll(".path_colour");
    for (let i = 0; i < colour_pickers.length; i++){
        colour_pickers[i].addEventListener("input", live_update_colour, false);
    }
    
    /**
     * Set the colour of all edges involved in a pathway
     *
     * @param event: event related to a pathway
     */
    function live_update_colour(event) {
        let path_id = $(this).data('path_id');
        edges = get_edges_from_path_id(path_id, cy);
        edges.style({
            'line-color': event.target.value,
            'target-arrow-color': event.target.value
        });
    }

    /**
     * 
     * Fill table values
     * 
     * @param score_label (str): the score label to use within the path info
     */
    function put_pathway_values(score_label='global_score'){
        for (let path_id in pathways_info){
            // Collect the value
            let score = pathways_info[path_id]['scores'][score_label];
            if (! isNaN(score)){
                score = parseFloat(score).toFixed(3);
            } else {
                score = 'NaN';
            }
            // Push it into the pathway table
            let path_td = $('td.path_value[data-path_id=' + path_id + ']');
            path_td.html(score);
            
        }
    }
};