import dash
from dash import dcc, html, dash_table, callback
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
#from dash import callback_context
from dash.dependencies import Input, Output, State


import pandas as pd
import base64
import io
import requests
from pprint import pprint
from time import time

ontology_service_api_url='https://eaq62kbd3d.execute-api.us-east-1.amazonaws.com/default/parkers_ontology_service_lambda'
app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    children=[
        dbc.Row(
            children=[
                dbc.Button(
                    'Download knockout form',
                    id='button_study_form_knockout',
                ),        
                dcc.Download(
                    id='download_study_form_knockout'
                ),
                dbc.Button(
                    'Download generic form',
                    id='button_study_form_generic',
                ),
                dcc.Download(
                    id='download_study_form_generic'
                ),
            ]
        ),
        dbc.Row(
            children=[
                # dbc.Button(
                #     'Upload completed form',
                #     id='button_study_form_upload',
                # ),
                dcc.Upload(
                    id='upload_study_form',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                ),
            ]                
        ),
        dbc.Row(
            children=[
                html.Div(
                    id='here_is_where_we_put_the curation_interface'
                )
            ]
        )
    ]
)

def parse_contents(contents):#, filename, date):
    #parse contents is a bit of a misnomer at the moment, could use some rearranging


    # content_type, content_string = contents.split(',')
    # decoded = base64.b64decode(content_string)
    # df = pd.read_excel(io.BytesIO(decoded))

    #####
    #do some checks on validity. currently not a thing.
    #####

    #####
    #determine form type. currently not a thing.
    #####

    #####
    #based on form type, choose parse approach. currently not a thing.
    #####

    #for now, we pretend like we spent time parsing this excel file
    species_to_curate=['homo sapiens', 'rats']
    organs_to_curate=['liver','lungz ']
    disease_to_curate=['lung cancer']
    genes_to_curate=['TP54','APOE','AR']

    elements_to_curate=species_to_curate+organs_to_curate
    elements_curated_dict=dict()
    #for each curation value, reach out to API
    for element in elements_to_curate:
        api_body={
            "freetext_string": element,
            "number_of_neighbors": 20
        }
        
        start_time=time()
        response = requests.post(ontology_service_api_url, json=api_body)
        print(response)
        end_time=time()
        print(end_time-start_time)

        elements_curated_dict[element]=response.json()
    


    



    pprint(elements_curated_dict)

    return elements_curated_dict
    # #total_panda = pd.read_json(response.json(), orient="records")
    # print(response.json())
    # print(response)

@callback(
    [
        Output(component_id="download_study_form_knockout", component_property="data"),
    ],
    [
        Input(component_id="button_study_form_knockout", component_property="n_clicks"),
    ],
    prevent_initial_call=True
)
def download_study_form_knockout(    button_study_form_knockout_n_clicks    ):
    return [dcc.send_file(
        '../../resources/knockout_template.xlsx'
    )]

@callback(
    [
        Output(component_id="download_study_form_generic", component_property="data"),
    ],
    [
        Input(component_id="button_study_form_generic", component_property="n_clicks"),
    ],
    prevent_initial_call=True
)
def download_study_form_generic(    button_study_form_generic_n_clicks    ):
    return [dcc.send_file(
        '../../resources/generic_template.xlsx'
    )]

@callback(
    [
        Output(component_id="here_is_where_we_put_the curation_interface", component_property="children"),
    ],
    [
        Input(component_id="upload_study_form", component_property="contents"),
    ],
    [
        State(component_id="upload_study_form", component_property="filename"),
        State(component_id="upload_study_form", component_property="last_modified"),
    ],
    prevent_initial_call=True
)
def upload_study_form(
    upload_study_form_contents,
    upload_study_form_filename,
    upload_study_form_last_modified
):


    elements_curated_dict=parse_contents(upload_study_form_contents)

    #for each element, create a "curation row"
    output_children=list()
    for element in elements_curated_dict.keys():
        #the core idea seems to simply be that, for pattern matching callbacks, the id becomes a dict, with arbitrary keys (altho conventions exist)
        output_children.append(
            dbc.Row(
                children=[
                    dbc.Col(
                        html.H6('input: '+element)
                    ),
                    dbc.Col(
                        html.H6('top proposal: '+elements_curated_dict[element][0][0])
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id={
                                'type':'dropdown_curation',
                                'index':element
                            },
                            options=[proposal[0] for proposal in elements_curated_dict[element]]
                        )
                    ),
                    dbc.Col(
                        dcc.Input(
                            id={
                                'type':'input_curation',
                                'index':element
                            },
                            placeholder="hate all the proposals? enter your own here!"
                        )
                    )
                    
                ]
            )
        )

    output_children.append(
        dbc.Row(
            children=[
                dbc.Button(
                    'Download curated form',
                    id='button_study_form_curated',
                ),        
                dcc.Download(
                    id='download_study_form_curated'
                ),
            ]
        )
    )

    return [
        #html.H6('got a file')
        output_children
    ]


if __name__ == "__main__":
    app.run(debug=True)