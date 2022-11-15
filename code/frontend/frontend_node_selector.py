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
import pandas as pd

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
            #sample nodes should probably be a set
            data={'generic_nodes':dict(),'edges':list(),'sample_nodes':list()}
        ),
        dbc.Card(
            children=[
                cyto.Cytoscape(
                    id='cyto',
                    #layout={'name':'dagre'},
                    elements=[],#compound_network_dict['elements'],
                    stylesheet=[
                        {
                            'selector':'node',
                            'style':{
                                'content':'data(label)',
                                'text-wrap':'wrap',
                                'text-max-width':100,
                                'font-size':13
                            }
                            
                        },
                        {
                            'selector':'edge[label]',
                            'style':{
                                'label':'data(label)',
                                #'text-wrap':'wrap',
                                #'text-max-width':100,
                                #'font-size':13
                            } 
                        },
                        {
                            'selector':'edge',
                            'style':{
                                'curve-style': 'bezier',
                                'source-arrow-shape': 'triangle',
                                #'text-wrap':'wrap',
                                #'text-max-width':100,
                                #'font-size':13
                            } 
                        },
                        {
                            "selector": ".autorotate",
                            "style": {
                                "edge-text-rotation": "autorotate",
                            }
                        }
                    #     {
                    #         'selector':'.selected',
                    #         'style':{
                    #             'background-color':'red'
                    #         }
                    #     },
                    #     #'text-wrap':'wrap'
                    ],
                    minZoom=0.3,
                    maxZoom=5
                ),
            ]
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
        html.Br(),
        html.Br(),
        dbc.Card(
            children=[
                html.H6('Node/edge property adjuster'),
                dcc.Dropdown(
                    id='dropdown_addproperty_keys',
                    options=[],
                    placeholder='choose existing propertykey',
                    multi=False,
                ),  
                dcc.Input(
                    id="input_addproperty_key",
                    type='text',
                    placeholder='add new property key'
                ),
                dcc.Input(
                    id="input_addproperty_value",
                    type='text',
                    placeholder='type property value'
                ),
                dbc.Button(
                    'Add this property key/value',
                    id='button_addproperty',
                ),


                dash_table.DataTable(
                    id='table_properties',
                    columns=[
                        {'name': 'Property', 'id': 'property'},
                        {'name': 'Value', 'id': 'value'}, 
                        #{'name': 'Sample Count', 'id': 'sample_count'}
                    ],
                    data=[],
                    page_current=0,
                    page_size=10,
                    #page_action='custom',
                    page_action='native',
                    #sort_action='custom',
                    sort_action='native',
                    sort_mode='multi',
                    #sort_by=[],
                    #filter_action='custom',
                    filter_action='native',
                    row_deletable=False,
                    #filter_query='',
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    style_cell={
                        'font-family':'sans-serif'
                    }
                ),
                dbc.Button(
                    'Save these properties',
                    id='button_saveproperties',
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
    #my_store_data['sample_nodes']=list()
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


@app.callback(
    [
        Output(component_id='cyto', component_property="elements"),
    ],
    [
        Input(component_id='my_store', component_property="data"),
    ],
    prevent_initial_call=True
)
def generate_cyto(my_store_data):
    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)

    print(my_store_data)
    cyto_elements=list()

    #if there is at least one generic node
    #unwrap the nodes
    if len(my_store_data['generic_nodes'].keys())>0:
        for node_id in my_store_data['generic_nodes']:
            cyto_elements.append(
                {
                    'data':{
                        'id':node_id,'label':node_id
                    }
                }
            )

    #if there is at least one sample node
    #visualize them as one large conglomerate
    if len(my_store_data['sample_nodes'])>0:
        cyto_elements.append(
            {
                'data':{
                    'id':'Samples','label':'Represents all samples'
                }
            }
        )

    #if there is at least one edge
    #unwrap the edges
    if len(my_store_data['edges'])>0:
        for edge in my_store_data['edges']:
            cyto_elements.append(
                {
                    'data':{
                        'source':edge['from'],
                        'target':edge['to'],
                        'label':edge['type'],
                        'id':time()
                    }
                }
            )        

    return cyto_elements


@app.callback(
    [
        Output(component_id='dropdown_addproperty_keys', component_property='options'),
        #Output(component_id='input_addproperty_key', component_property='value')),
        Output(component_id='table_properties', component_property='data'),
    ],
    [
        Input(component_id='cyto', component_property='tapNodeData'),
    ],
    [
        State(component_id='my_store', component_property="data"),    
    ],
    prevent_initial_call=True
)
def prepare_property_section(cyto_tapNodeData,my_store_data):
    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)
    #i think the best way to know if it is a node or an edge is to check the callback context?
    #or have two callbacks
    print(cyto_tapNodeData)
    pprint(my_store_data)
    print(my_store_data['generic_nodes'][cyto_tapNodeData['id']])
    print(my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'])
    if len(my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'])>0:
        #do something
        #pass
        # properties=my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'].keys()
        # values=[my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'][temp_key] for temp_key in my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'].keys()]
        #when things are stored in the data format, we don thave to do anything
        #could return thi directly
        table_properties_data=my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties']
    elif len(my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'])==0:
        #properties=[]
        #values=[]
        # table_properties_data=[
        #     {'property':dropdown_addproperty_keys_value,'value':input_addproperty_value_value}
        # ]
        table_properties_data=None
    #temp_panda=pd.DataFrame.from_dict({'property':properties,'value':values})
    #data = temp_panda.to_dict(orient='records')


    #how do we get the label that this particular node is?
    #we cant. or at least we shouldnt? because nodes can have multiple labels
    #so it a big headache. for the moment, we use the all labels option
    my_FrontendHelper.get_node_property_matrix()
    all_labels=my_FrontendHelper.property_dict['ALL_NODE_LABEL']

    return [all_labels,table_properties_data]
    

@app.callback(
    [
        Output(component_id='table_properties', component_property='data'),
    ],
    [
        Input(component_id='button_addproperty', component_property="n_clicks"),
    ],
    [
        State(component_id='dropdown_addproperty_keys', component_property="value"),
        State(component_id='input_addproperty_key', component_property="value"),
        State(component_id='input_addproperty_value', component_property="value"),
        State(component_id='table_properties', component_property='data')
    ],
    prevent_initial_call=True
)
def add_property(
    button_addproperty_n_clicks,
    dropdown_addproperty_keys_value,
    input_addproperty_key_value,
    input_addproperty_value_value,
    table_properties_data
):
    pprint(table_properties_data)
    #pass
    # if type(my_store_data)!=dict:
    #     my_store_data=jsons.loads(my_store_data)
    ####
    #!!!!
    #we need to create some kind of exception handling if they put values in both
    #for now we only accept values from the dropdown
    #!!!!
    ####
    #total_panda = pd.read_json(response.json(), orient="records")
    #    properties=my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'].keys()
    #    values=[my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'][temp_key] for temp_key in my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties'].keys()]
    if table_properties_data != None:
        table_properties_data.append(
            {'property':dropdown_addproperty_keys_value,'value':input_addproperty_value_value}
        )
    elif table_properties_data == None:
        table_properties_data=[
            {'property':dropdown_addproperty_keys_value,'value':input_addproperty_value_value}
        ]
    pprint(table_properties_data)
    return table_properties_data

@app.callback(
    [
        Output(component_id='my_store', component_property="data"),
    ],
    [
        Input(component_id='button_saveproperties', component_property='n_clicks'),
    ],
    [
        State(component_id='table_properties', component_property='data'),   
        State(component_id='cyto', component_property='tapNodeData'), 
        State(component_id='my_store', component_property="data")
    ],
    prevent_initial_call=True
)
def store_properties(
    button_saveproperties_n_clicks,
    table_properties_data,
    cyto_tapNodeData,
    my_store_data
):
#     pass
    if type(my_store_data)!=dict:
        my_store_data=jsons.loads(my_store_data)
    my_store_data['generic_nodes'][cyto_tapNodeData['id']]['properties']=table_properties_data


    print('123'*20)
    pprint(my_store_data)




    return jsons.dumps(my_store_data)


if __name__ == "__main__":
    app.run(debug=True)#, host='0.0.0.0')