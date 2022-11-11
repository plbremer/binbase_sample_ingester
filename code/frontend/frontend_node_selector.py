import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import callback_context
from time import time
from pprint import pprint
import json
from frontend_helper import *

from neo4j import GraphDatabase
driver=GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j','elaine123'))


app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP])#external_stylesheets=[dbc.themes.BOOTSTRAP])

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

app.layout = html.Div(
    children=[
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
        )
    ]
)


@callback(
    [
        Output(component_id='dropdown_nodesearch', component_property="options"),
    ],
    [
        Input(component_id='button_nodesearch', component_property='n_clicks'),
    ],
    [
        State(component_id='input_nodesearch', component_property="value"),
    ],
    prevent_initial_call=True
)
def download_graph(
    button_nodesearch_n_clicks,
    input_nodesearch_value
): 
    
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
    #driver.close()
    displayed_string_list=list()
    for i in range(len(graph_db_matching_records)):
        displayed_string_list.append(
            my_FrontendHelper.construct_smart_node_selection_options(graph_db_matching_records[i],string_node_id_list_pairs[i])
        )
    
    returned_options_dict=[
        {'value':string_node_id_list_pairs[i][0], 'label':displayed_string_list[i]} for i in range(len(displayed_string_list))
    ]
    
    return [returned_options_dict]

if __name__ == "__main__":
    app.run(debug=True)#, host='0.0.0.0')