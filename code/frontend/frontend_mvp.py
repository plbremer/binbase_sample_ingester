import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import callback_context
from time import time
from pprint import pprint
import json

app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP])#external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    children=[
        cyto.Cytoscape(
            id='cyto_sample_nature',
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
        dcc.Dropdown(
            id='dropdown_node_sample',
            options=[1,2,3,4,5],
            value=None,
            multi=False,
        ),
        dbc.Button(
            'Add Sample Nodes',
            id='button_add_node_sample',
        ),
        dcc.Dropdown(
            id='dropdown_node_type',
            options=sorted(
                ['species','organ','location','status']
            ),
            value=None,
            multi=False,
        ),
        dbc.Button(
            'Add node',
            id='button_add_node',
        ),
        dcc.Dropdown(
            id='dropdown_node_property',
            options=sorted(
                ['quercus lobata','mouse','cow','male','female','heated','cooled','plant leaves','damaged','highway']
            ),
            multi=False,
        ),
        dbc.Button(
            'Add node property',
            id='button_add_node_property',
        ),
        dcc.Dropdown(
            id='dropdown_edge_type',
            options=sorted(
                ['derived_from','infected_by','treated_by','nearby']
            ),
            multi=False,
        ),
        dbc.Button(
            'Add edge',
            id='button_add_edge',
        ),
        dcc.Download(
            id='download_graph'
        ),
        dbc.Button(
            'Download Graph',
            id='button_download_graph',
        ),
    ]
)


@callback(
    [
        Output(component_id='cyto_sample_nature', component_property="elements"),
    ],
    [
        Input(component_id='button_add_node_sample', component_property='n_clicks'),
        Input(component_id='button_add_node', component_property='n_clicks'),
        Input(component_id='button_add_node_property', component_property='n_clicks'),
        Input(component_id='button_add_edge', component_property='n_clicks'),
    ],
    [
        State(component_id='cyto_sample_nature', component_property="elements"),
        State(component_id='dropdown_node_sample', component_property="value"),
        State(component_id='dropdown_node_type', component_property="value"),
        State(component_id='cyto_sample_nature', component_property='tapNodeData'),
        State(component_id='dropdown_node_property', component_property="value"),
        State(component_id='cyto_sample_nature', component_property='selectedNodeData'),
        State(component_id='dropdown_edge_type', component_property="value"),
    ],
    prevent_initial_call=True
)
def add_node(
    button_add_node_sample_n_clicks,
    button_add_node_n_clicks,
    button_add_node_property_n_clicks,
    button_add_edge_n_clicks,
    cyto_sample_nature_elements,
    dropdown_node_sample_value,
    dropdown_node_type_value,
    cyto_sample_nature_tapNodeData,
    dropdown_node_property_value,
    cyto_sample_nature_selectedNodeData,
    dropdown_edge_property_value 
):
    print(callback_context.triggered[0]['prop_id'])


    if callback_context.triggered[0]['prop_id']=='button_add_node_sample.n_clicks':
        for i in range(0,dropdown_node_sample_value):
            cyto_sample_nature_elements.append(
                {'data':
                    {'id':i,'label':'Sample '+str(i)}
                }
            )

    elif callback_context.triggered[0]['prop_id']=='button_add_node.n_clicks':
        cyto_sample_nature_elements.append(
            {'data':
                {'id':time(),'label':dropdown_node_type_value}
            }
        )
        pprint(cyto_sample_nature_elements)

    elif callback_context.triggered[0]['prop_id']=='button_add_node_property.n_clicks':
        # print('-'*50)
        # pprint(cyto_sample_nature_tapNodeData)
        # print('-'*50)
        # pprint(cyto_sample_nature_elements)
        # print('-'*50)
        #adjust the main data using the id that we get from the tap node data
        #the nodes are a list of dicts, so we literally have to iterate over all of them until we encounter the one with the right data
        #that is, the one whose id matches the tapnode id
        #print(cyto_sample_nature_elements['data'][cyto_sample_nature_tapNodeData['id']]['label'])#=cyto_sample_nature_elements['data'][cyto_sample_nature_tapNodeData['id']]['label']+' '+dropdown_node_property_value
        for i,temp_element in enumerate(cyto_sample_nature_elements):
            #print(i)
            #edges are also dicts starting with data. but they have different keys. so we do a check to avoid a no key error
            if 'id' in temp_element['data'].keys():
                if temp_element['data']['id']==cyto_sample_nature_tapNodeData['id']:
                    #print(cyto_sample_nature_elements[i]['data'][cyto_sample_nature_tapNodeData['id']])
                    #cyto_sample_nature_elements[i]['data'][cyto_sample_nature_tapNodeData['id']]['label']=cyto_sample_nature_elements[i]['data'][cyto_sample_nature_tapNodeData['id']]['label']+' '+dropdown_node_property_value
                    cyto_sample_nature_elements[i]['data']['label']=cyto_sample_nature_elements[i]['data']['label']+': '+dropdown_node_property_value
    

    elif callback_context.triggered[0]['prop_id']=='button_add_edge.n_clicks':
        #pprint(cyto_sample_nature_selectedNodeData)
        cyto_sample_nature_elements.append(
            {'data':
                {
                    'source':cyto_sample_nature_selectedNodeData[0]['id'],
                    'target':cyto_sample_nature_selectedNodeData[1]['id'],#,
                    'label':dropdown_edge_property_value,
                    'id':time()
                }
            }
        )

    return [cyto_sample_nature_elements]

@callback(
    [
        Output(component_id='download_graph', component_property="data"),
    ],
    [
        Input(component_id='button_download_graph', component_property='n_clicks'),
    ],
    [
        State(component_id='cyto_sample_nature', component_property="elements"),
    ],
    prevent_initial_call=True
)
def download_graph(
    button_download_graph_n_clicks,
    cyto_sample_nature_elements
):
    pprint(cyto_sample_nature_elements)
    # return [
    #     dict(
    #         content=cyto_sample_nature_elements,
    #         filename='temp_graph_as_txt.txt'
    #     )
    # ]
    print('-'*50)
    print(
        json.dumps(
            cyto_sample_nature_elements
        )
    )
    return [dict(
        content=json.dumps(cyto_sample_nature_elements),
        filename='temp_graph_as_txt.txt'
    )]



# @callback(
#     [
#         Output(component_id='cyto_sample_nature', component_property="elements"),
#     ],
#     [
#         Input(component_id='button_add_node_property', component_property='n_clicks'),
#     ],
#     [
#         State(component_id='cyto_sample_nature', component_property="elements"),
#         #State(component_id='dropdown_node_type', component_property="value"),
#         #State(component_id='radio_items_sunburst_value',component_property='value'),
#         State(component_id='dropdown_node_property', component_property="value"),
#         State(component_id='cyto_sample_nature', component_property='tapNodeData')
#     ],
#     prevent_initial_call=True
# )
# def add_node(button_add_node_property_n_clicks,cyto_sample_nature_elements,dropdown_node_type_value,cyto_sample_nature_tapNodeData):
#     # cyto_sample_nature_elements.append(
#     #     {'data':
#     #         {'id':time(),'label':dropdown_node_type_value}
#     #     }
#     # )
#     pprint(cyto_sample_nature_tapNodeData)
#     return [cyto_sample_nature_elements]


if __name__ == "__main__":
    app.run(debug=True)#, host='0.0.0.0')
