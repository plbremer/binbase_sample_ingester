import dash
from dash import dcc, html, dash_table, callback
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
#from dash import callback_context
from dash.dependencies import Input, Output, State


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

    return [
        html.H6('got a file')
    ]


if __name__ == "__main__":
    app.run(debug=True)