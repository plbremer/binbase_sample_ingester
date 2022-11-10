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
    temp_results=my_FrontendHelper.generate_nodes_from_freetext_string('Liver Neoplasms')
    #form of temp results:[('Liver Neoplasms', 'C06.552.697'), ('Ear Neoplasms', 'C09.647.312')]
    for element in temp_results:
        #we accidentally overwrote mesh labels that appeared multiple times in our note_and_attribute_jsons
        #so this funciton needs to get reworked
        print(my_FrontendHelper.get_node_labels_for_string(element[1]))
    print(temp_results)
    return [[1,2,3]]

if __name__ == "__main__":
    app.run(debug=True)#, host='0.0.0.0')