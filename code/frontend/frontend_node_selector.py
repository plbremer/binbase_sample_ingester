import string
import dash
from dash import dcc, html, dash_table, callback
#from dash.dependencies import Input, Output, State
#from dash.dependencies import State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import callback_context
from time import time
from pprint import pprint
import json
import jsons
from frontend_helper import *
from selectednode import *

from neo4j import GraphDatabase
driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))
#
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform, State
#app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP])#external_stylesheets=[dbc.themes.BOOTSTRAP])
app = DashProxy(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP],transforms=[MultiplexerTransform()])


my_FrontendHelper=FrontendHelper()
my_FrontendHelper.read_in_freetext_jsons('../../intermediate_results/attribute_node_id_pairs/')
my_FrontendHelper.read_in_models()
my_FrontendHelper.read_in_training_set()
# my_test_string_list=['utero']
# my_test_strings_vector=my_FrontendHelper.tfidf_vectorizer.transform(my_test_string_list)
# kn_dist,kn_ind=my_FrontendHelper.nea_nei_model.kneighbors(my_test_strings_vector,100)
# for location in kn_ind[0]:
#     print(my_FrontendHelper.tfidf_vectorizer_training_set[location])
# my_FrontendHelper.get_node_property_matrix()


#getting the labels happens on app startup
existing_node_labels=my_FrontendHelper.get_all_node_labels()
existing_node_labels.remove('ALL_NODE_LABEL')
existing_node_labels=list(existing_node_labels)

existing_edge_labels=list(my_FrontendHelper.get_all_edge_labels())
print('here')
app.layout = html.Div(
    children=[
        dcc.Store(
            id='my_store',
            storage_type='memory',
            data={'generic_nodes':dict(),'edges':list()}
        ),

        dbc.Card(
            children=[
                html.H6('search for existing nodes'),
                dcc.Input(
                    id="input_nodesearch",
                    type='text',
                    placeholder='search for a node'
                ),
                dbc.Button(
                    'Search available nodes',
                    id='button_nodesearch',
                ),
                dcc.Dropdown(
                    id='dropdown_nodesearch',
                    options=['no node searched'],
                    value='no node searched',
                    multi=False,
                ),
                dbc.Button(
                    'Add this node',
                    id="button_nodeselect",
                ),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H6('create new node'),

                #choose nodetype
                #choose
                dcc.Dropdown(
                    id='dropdown_createnode_labels',
                    options=existing_node_labels,
                    placeholder='choose existing node label',
                    multi=False,
                ),   
                dcc.Input(
                    id="input_createnode_label",
                    type='text',
                    placeholder='or enter a new label type here'
                ),  
                html.H6('also'),
                dcc.Input(
                    id="input_createnode_nodeid",
                    type='text',
                    placeholder='put node id here'
                ),  
                dbc.Button(
                    'Create new node',
                    id='button_createnode',
                ),

            ],
            style={"width": "18rem"}
        ),

        
        html.Br(),
        html.Br(),
        dbc.Card(
            children=[
                html.H6('add edge'),
                dcc.Dropdown(
                    id='dropdown_nodefrom',
                    options=['no node selected'],
                    value='no node selected',
                    multi=False,
                ),
                dcc.Dropdown(
                    id='dropdown_nodeto',
                    options=['no node selected'],
                    value='no node selected',
                    multi=False,
                ),
                #there is a countable number of edges, so it doesnt feel natural to have an approach
                #that is symmetric wth the nodes
                html.H6('create new edge'),


                dcc.Dropdown(
                    id='dropdown_createedge_labels',
                    options=existing_edge_labels,
                    placeholder='choose existing node label',
                    multi=False,
                ),   
                dcc.Input(
                    id="input_createedge_label",
                    type='text',
                    placeholder='or enter a new edge type here'
                ),  
                # "label" is all that describes an edge, so this is not necessary
                # html.H6('also'),
                # dcc.Input(
                #     id="input_createedge_edgeid",
                #     type='text',
                #     placeholder='put edge type here'
                # ),  
                dbc.Button(
                    'Create new edge',
                    id='button_createedge',
                ),

            ],
            style={"width": "18rem"}
        ),   
        html.Br(),
        html.Br(),
        dbc.Card(
            children=[
                html.H6('add samples'),
                dcc.Input(
                    id="input_samplenumber",
                    type='number',
                    placeholder='add this many samples'
                ),
                dbc.Button(
                    'Search available nodes',
                    id='button_addsamples',
                ),

            ],
            style={"width": "18rem"}
        ),   
    ]
)

#this is the callback that searches for matching generic nodes that already exist in the database
@app.callback(
    [
        Output(component_id='dropdown_nodesearch', component_property="options"),
        Output(component_id='my_store', component_property="data"),
    ],
    [
        Input(component_id='button_nodesearch', component_property='n_clicks'),
    ],
    [
        State(component_id='input_nodesearch', component_property="value"),
        State(component_id='my_store', component_property="data"),
    ],
    prevent_initial_call=True
)
def find_best_node_matches(
    button_nodesearch_n_clicks,
    input_nodesearch_value,
    my_store_data
): 
    print('$'*50)
    print(my_store_data)
    
    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)
    
    #print(asdf)
    #print(input_nodesearch_value)
    #print(my_FrontendHelper.total_node_id_dict)
    string_node_id_list_pairs=my_FrontendHelper.generate_nodes_from_freetext_string(input_nodesearch_value)
    #form of temp results:[('Liver Neoplasms', ['C04.588.274.623', 'C06.301.623', 'C06.552.697']), ('Ear Neoplasms', ['C04.588.443.665.312', 'C09.218.334', 'C09.647.312']),
    graph_db_matching_records=list()
    for freetext_match in string_node_id_list_pairs:
        for counter,node in enumerate(freetext_match[1]):
        #we accidentally overwrote mesh labels that appeared multiple times in our note_and_attribute_jsons
        #so this funciton needs to get reworked
        
        #maybe can improve speed with "where OR OR OR" eg 1 call?
        #seems we might need a different index
            #for the moment, we are making the design decision that a text strin must automatically confer all nodes to which it belongs
            #eg, the user is not interested in obtaining all of the results for all of the node id for some "Iris Neoplasms"
            #so we only need the first    
            if counter>=1:
                continue
        #print(my_FrontendHelper.get_node_labels_for_string(node,driver)[0])
        #print(my_FrontendHelper.get_node_labels_for_string(node,driver))
            print('*'*50)
            graph_db_matching_records.append(my_FrontendHelper.get_node_labels_for_string(node,driver)[0])

    
    print(string_node_id_list_pairs)
    
    #convert to a dict for convenient access to the option that we want in storage
    stored_options_dict={
        element[0]:element[1] for element in string_node_id_list_pairs
    }
    my_store_data['search_node_compressed_results']=stored_options_dict
    #driver.close()
    displayed_string_list=list()
    for i in range(len(graph_db_matching_records)):
        displayed_string_list.append(
            my_FrontendHelper.construct_smart_node_selection_options(graph_db_matching_records[i],string_node_id_list_pairs[i])
        )
    
    returned_options_dict=[
        {'value':string_node_id_list_pairs[i][0], 'label':displayed_string_list[i]} for i in range(len(displayed_string_list))
    ]
    print(my_store_data)
    return [returned_options_dict,jsons.dumps(my_store_data)]



@app.callback(
    [
        Output(component_id='my_store', component_property="data"),
    ],
    [
        Input(component_id='button_nodeselect', component_property='n_clicks'),
    ],
    [
        State(component_id='dropdown_nodesearch', component_property="value"),
        State(component_id='my_store', component_property="data"),

    ],
    prevent_initial_call=True
)
def add_generic_node_to_store(
    button_nodeselect_n_clicks,
    dropdown_nodesearch_value,
    my_store_data
):
    print('+'*50)
    print('arrival store data')
    pprint(my_store_data)
    print(type(my_store_data))

    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)
    #if this is an already existing node


    my_SelectedNode=SelectedNode(dropdown_nodesearch_value,'existing_node',my_store_data['search_node_compressed_results'])
    my_store_data['generic_nodes'][dropdown_nodesearch_value]=my_SelectedNode
    #if this is a new node
    
    print(jsons.dumps(my_SelectedNode))

    pprint(my_store_data)
    return jsons.dumps(my_store_data)

@app.callback(
    [
        Output(component_id='my_store', component_property="data"),
    ],
    [
        Input(component_id='button_createnode', component_property='n_clicks')
    ],
    [
        State(component_id='dropdown_createnode_labels', component_property="value"),
        State(component_id='input_createnode_label', component_property="value"),
        State(component_id='input_createnode_nodeid', component_property="value"),
        State(component_id='my_store', component_property="data"),

    ],
    prevent_initial_call=True
)
def add_created_node_to_store(
    button_createnode_n_clicks,
    dropdown_createnode_labeloptions_value,
    input_createnode_label_value,
    input_createnode_nodeid_value,
    my_store_data
):
    print('+'*50)
    print('arrival store data')
    pprint(my_store_data)
    print(type(my_store_data))

    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)
    #if this is an already existing node

    my_SelectedNode=SelectedNode(
        input_createnode_nodeid_value,
        'created_node',
        {input_createnode_nodeid_value:input_createnode_nodeid_value}
    )
    ####
    #!!!!
    #we need to create some kind of exception handling if they put values in both
    #for now we only accept values from the dropdown
    #!!!!
    ####
    my_SelectedNode.set_label(dropdown_createnode_labeloptions_value)
    my_store_data['generic_nodes'][input_createnode_nodeid_value]=my_SelectedNode#jsons.dumps(my_SelectedNode)


    print('#'*50)
    print(jsons.dumps(my_SelectedNode))

    pprint(my_store_data)
    return jsons.dumps(my_store_data)


@app.callback(
    [
        Output(component_id='my_store', component_property="data"),
    ],
    [
        Input(component_id='button_addsamples', component_property='n_clicks'),
    ],
    [
        State(component_id='input_samplenumber', component_property="value"),
        State(component_id='my_store', component_property="data"),
    ],
    prevent_initial_call=True
)
def add_sample_node_to_store(
    button_addsamples_n_clicks,
    input_samplenumber_value,
    my_store_data
):

    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)

    #should have assertion statement that number is integer
    my_store_data['sample_nodes']=list()
    for i in range(input_samplenumber_value):
        my_store_data['sample_nodes'].append(str(i))

    return jsons.dumps(my_store_data)


@app.callback(
    [
        Output(component_id='dropdown_nodefrom', component_property="options"),
        Output(component_id='dropdown_nodeto', component_property="options"),
    ],
    [
        Input(component_id='my_store', component_property="data"),
    ],
    # [
    #     State(component_id='input_samplenumber', component_property="value"),
    #     State(component_id='my_store', component_property="data"),
    # ],
    prevent_initial_call=True
)
def generate_dropdown_options_for_edge(
    my_store_data
):
    '''
    create a new edge
    '''
    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)

    output_options=list()
    if 'generic_nodes' in my_store_data.keys():
        for temp_node in my_store_data['generic_nodes']:
            output_options.append(
                {'value':temp_node,'label':temp_node}
            )
    if 'sample_nodes' in my_store_data.keys():
        output_options.append(
            {'value': 'Samples', 'label': 'Samples'}
        )

    #if we found none, then the length is zero
    if len(output_options)==0:
        output_options.append(
            {'value': 'no node selected', 'label': 'no node selected'}
        )

    return [output_options,output_options]

@app.callback(
    [
        Output(component_id='my_store', component_property="data"),
    ],
    [
        Input(component_id='button_createedge', component_property='n_clicks'),
    ],
    [
        State(component_id='dropdown_createedge_labels', component_property="value"),
        State(component_id='input_createedge_label', component_property="value"),
        State(component_id='dropdown_nodefrom', component_property="value"),
        State(component_id='dropdown_nodeto', component_property="value"),
        State(component_id='my_store', component_property="data"),
    ],
    prevent_initial_call=True
)
def add_edge_to_store(
    button_addedge_n_clicks,
    dropdown_createedge_labels_value,
    input_createedge_label_value,
    dropdown_nodefrom_value,
    dropdown_nodeto_value,
    my_store_data
):

    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)

    ####
    #!!!!
    #we need to create some kind of exception handling if they put values in both
    #for now we only accept values from the dropdown
    #!!!!
    #need to disallow sample to sample edges
    ####   
    my_store_data['edges'].append(
        {
            'from':dropdown_nodefrom_value,
            'to':dropdown_nodeto_value,
            'type':dropdown_createedge_labels_value
        }
    )

    pprint(my_store_data)


    return jsons.dumps(my_store_data)




if __name__ == "__main__":
    app.run(debug=True)#, host='0.0.0.0')