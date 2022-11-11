import string
import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
#from dash.dependencies import State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import callback_context
from time import time
from pprint import pprint
import json
from frontend_helper import *
from selectednode import *

from neo4j import GraphDatabase
driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))
#
#from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform
app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP])#external_stylesheets=[dbc.themes.BOOTSTRAP])
#app = DashProxy(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP],transforms=[MultiplexerTransform()])


asdf='hello'
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

app.layout = html.Div(
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
        dcc.Store(
            id='my_store',
            storage_type='memory',
            data={'generic_nodes':dict()}
        )
    ]
)

#this is the callback that searches for matching generic nodes that already exist in the database
@callback(
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
def download_graph(
    button_nodesearch_n_clicks,
    input_nodesearch_value,
    my_store_data
): 
    print('$'*50)
    print(my_store_data)
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
    
    return [returned_options_dict,my_store_data]


#this callback creates new "non-generic nodes" based on the generic node that the user chose
@callback(
    [
        Output(component_id='my_store', component_property="data"),
    ],
    [
        Input(component_id='button_nodeselect', component_property='n_clicks'),
        Input(component_id='button_createnode', component_property='n_clicks')
    ],
    [
        State(component_id='dropdown_nodesearch', component_property="value"),

        State(component_id='dropdown_createnode_labels', component_property="value"),
        State(component_id='input_createnode_label', component_property="value"),
        State(component_id='input_createnode_nodeid', component_property="value"),



        State(component_id='my_store', component_property="data"),

    ],
    prevent_initial_call=True
)
def download_graph(
    button_nodeselect_n_clicks,
    button_createnode_n_clicks,
    dropdown_nodesearch_value,

    dropdown_createnode_labeloptions_value,
    input_createnode_label_value,
    input_createnode_nodeid_value,

    my_store_data
):

    #if this is an already existing node
    pprint(my_store_data)
    if callback_context.triggered[0]['prop_id']=='button_nodeselect.n_clicks':
        my_SelectedNode=SelectedNode(dropdown_nodesearch_value,'existing_node',my_store_data['search_node_compressed_results'])
        my_store_data['generic_nodes'][dropdown_nodesearch_value]=my_SelectedNode
    #if this is a new node
    
    if callback_context.triggered[0]['prop_id']=='button_createnode.n_clicks':
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
        my_store_data['generic_nodes'][dropdown_createnode_labeloptions_value]=my_SelectedNode


    pprint(my_store_data)
    return [my_store_data]



if __name__ == "__main__":
    app.run(debug=True)#, host='0.0.0.0')