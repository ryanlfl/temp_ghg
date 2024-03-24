#############
## Imports ##
#############


import dash
from dash import html, dcc, Input, Output, State, dash_table, ALL
from dash.long_callback import DiskcacheLongCallbackManager
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import diskcache

import json

from utils import * 


##############
## Settings ##
##############

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/css/styles.css"],background_callback_manager=long_callback_manager)


############
## Layout ##
############


# Layout with container, columns, and rows
app.layout = dbc.Container([
    
    dbc.Spinner(id="common_spinner",color="primary",spinner_style={"display":"none"}),

    dcc.Store(id='ghg_data',storage_type='memory'),
    dcc.Store(id='ghg_aggregate_data_country',storage_type='memory'),
    dcc.Store(id='ghg_aggregate_data_account',storage_type='memory'),
    dcc.Store(id='ghg_aggregate_data_year',storage_type='memory'),
    dcc.Store(id='file_name',storage_type='memory'),
    dcc.Store(id='temp_dont_modify',storage_type='memory'),

    dcc.Download(id="download"),

    dbc.Col([
        dbc.Row(html.H1("GHG Reports Portal"),style={'text-align':'center','border-bottom':'solid black 0.15rem'}), # Title

        dbc.Row(
            children=[

                dbc.Col(
                    children=[
                        dbc.Row(
                            children=[
                                html.H4("Filters",style={'text-align':'center',"margin":"0.25rem 0.25rem 1rem 0.25rem"}), 
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="country-dropdown",
                                        # options=[{'label': "All", 'value': "All"}]+[{'label': c, 'value': c} for c in get_ghg_report_name_df(reports_directory)["country"].unique() ],
                                        options=[{'label': "All", 'value': "All"}]+[{'label': c, 'value': c} for c in get_ghg_countries_accounts_df()["country"].unique() ],
                                        placeholder="Country"
                                    ),
                                    width=6,
                                    # style={'margin':'0.3rem'}
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="account-dropdown",
                                        # options=[{'label': "All", 'value': "All"}]+[{'label': a, 'value': a} for a in  get_ghg_report_name_df(reports_directory)["account"].unique()],
                                        options=[{'label': "All", 'value': "All"}]+[{'label': a, 'value': a} for a in  get_ghg_countries_accounts_df()["account"].unique()],
                                        placeholder="Account"
                                    ),
                                    width=6,
                                    # style={'margin':'0.3rem'}
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="year-dropdown",
                                        # options=[{'label': "All", 'value': "All"}]+[{'label': y, 'value': y} for y in  get_ghg_report_name_df(reports_directory)["year"].unique()],
                                        options=[{'label': "All", 'value': "All"}]+[{'label': y, 'value': y} for y in  [i for i in range(2020,2024)]],
                                        placeholder="Year"
                                    ),
                                    width=12,
                                    style={'margin-top':'0.5rem'}
                                )
                            ],
                            # style={'border':'solid black 0.15rem', 'margin':'0.05rem', "padding": "1rem 0rem",},
                            style={ 'margin':'0.05rem', "padding": "1rem 0rem",},

                        ),
                        
                        dbc.Row(
                            children=[
                                # html.H4("Tree",style={'text-align':'center',"margin":"0.25rem 0.25rem 1.5rem 0.25rem"}), 

                                dmc.Accordion(
                                    dmc.AccordionItem(
                                        [
                                            
                                            html.Div([DashIconify(icon="akar-icons:folder"), " ", "Reports"],style={"padding":"1rem"}, id="ReportsButton"),
                                            # dmc.AccordionControl([DashIconify(icon="akar-icons:folder"), " ", "Reports"]),
                                            dmc.AccordionPanel(

                                                [
                                                    dbc.ListGroup(
                                                        [
                                                            dbc.ListGroupItem(
                                                                dmc.Text([DashIconify(icon="akar-icons:file"), " ", f, " ", html.Img(src="assets/icons/view.png",height=10,title="View", style={"display":"none"}) ], style={"paddingTop": 10, "font-size":"small"}),style={"background-color":"#f6f6ea"},
                                                                id={"type": "list-item", "index": idx},
                                                                n_clicks=0
                                                            )
                                                            for idx, f in enumerate( get_ghg_report_name_df(reports_directory)["file_name"].unique())
                                                        ],
                                                        flush=True,
                                                        style={"background-color":"#f6f6ea"},
                                                        id="ghg_report_accordion_list",
                                                        
                                                    )
                                                ],

                                                # [dmc.Text([DashIconify(icon="akar-icons:file"), " ", f, " ", html.Img(src="assets/icons/view.png",height=10,title="View", style={"display":"none"}) ], style={"paddingTop": 10, "font-size":"small"}) for f in get_ghg_report_name_df(reports_directory)["file_name"].unique()],
                                            
                                                style = {'max-height': '40vh', 'overflow-x': 'hidden', 'overflow-y': 'scroll'},
                                                # className="AccordionPanelClass"

                                            ),

                                        ],
                                        value="reports",
                                    ),
                                    value="reports",
                                    style = {'max-height': '45vh',},
                                    # style = {'max-height': '45vh', 'overflow-x': 'hidden', 'overflow-y': 'scroll'},
                                    id="reports_accordion"
                                )

                                
                            ],
                            # style={'border':'solid black 0.15rem', 'margin':'0.05rem'}
                            style={'margin':'0.05rem'}
                        ),
                    ], 
                    # style={'border':'solid black 0.15rem', 'margin':'1rem', 'padding':'0rem'},
                    style={'border':'solid black 0.15rem', 'margin':'1rem', 'padding':'0rem', 'border-radius':'1.5rem'},
                    width={'size':3,'offset':0,'order':'first'}
                ),

                dbc.Col(
                    children=[
                        dbc.Container(children=[
                            html.H4("Output",style={'text-align':'center',"margin":"0.25rem 0.25rem 1rem 0.25rem"}),
                            dbc.Row(children=[
                                html.Div(id="data_table_panel",style={"display":"none"}),
                                html.Div(id="aggregate_data_panel",style={"display":"none"}),
                                html.Div(id="starter_image_panel",children=[html.Img(src="assets/icons/carbon-dioxide-1.png", style={'width': '20rem', 'height': 'auto', 'opacity': '0.2'})],style={'justify-content': 'center','align-items': 'center', 'display': 'flex','padding': '1.3rem 0rem'}),
                            ],justify="between"),
                            dbc.Row(children=[
                                dbc.RadioItems(
                                    id="output_navigator",
                                    className="btn-group",
                                    inputClassName="btn-check",
                                    labelClassName="btn btn-outline-primary",
                                    labelCheckedClassName="active", 
                                    options=[
                                        {"label": [html.Img(src="assets/icons/table.png", height=30,title="Data")], "value": 1},
                                        {"label": [html.Img(src="assets/icons/dashboard.png", height=30,title="Aggregate Data")], "value": 2},
                                        {"label": [html.Img(src="assets/icons/download.png", height=30,title="Download")], "value": 3},
                                        {"label": [html.Img(src="assets/icons/support.png", height=30,title="WOS")], "value": 4, "disabled":True},
                                        
                                    ],
                                    value=1,
                                    style={"padding":"1rem 0rem"},
                                ),
                            ],align="end",justify="between"  ),
                        ],style={"display":"flex","flex-direction":"column","align-items":"center",})
                    ],
                    style={'border':'solid black 0.15rem',  'margin':'1rem', 'border-radius':'1.5rem'}
                )

            ],
            style={'margin-top':'1rem', },
            justify="evenly"
        )


    ])
], className="p-3",style={'max-height': '95vh', 'overflow-y': 'hidden'}
)


###############
## Callbacks ##
###############


@app.callback(
    Output(component_id='ghg_report_accordion_list', component_property='children'),
    Input(component_id='country-dropdown', component_property='value'),
    Input(component_id='account-dropdown', component_property='value'),
    Input(component_id='year-dropdown', component_property='value'),
    prevent_initial_call=True,
)
def filter_ghg_reports(country_dropdown_value, account_dropdown_value, year_dropdown_value):

    with open("tempsol","w") as fob:
        fob.write("X")

    # get report name df
    df = get_ghg_report_name_df(reports_directory)

    if country_dropdown_value and country_dropdown_value != "All":
        df = df[df["country"] == country_dropdown_value]

    if account_dropdown_value and account_dropdown_value != "All":
        df = df[df["account"] == account_dropdown_value]

    if year_dropdown_value and year_dropdown_value != "All":
        df = df[df["year"] == year_dropdown_value]


    if not df.empty:
        _output = [
            dbc.ListGroupItem(
                dmc.Text([DashIconify(icon="akar-icons:file"), " ", f, " ", html.Img(src="assets/icons/view.png",height=10,title="View", style={"display":"none"}) ], style={"paddingTop": 10, "font-size":"small"}),style={"background-color":"#f6f6ea"},
                id={"type": "list-item", "index": idx},
                n_clicks=0
            )
            for idx, f in enumerate( df["file_name"].unique() )
        ]

    else:
        contact_info_json = get_contact_info_json()
        contact_info_message = ""
        if country_dropdown_value:
            contact_info = contact_info_json.get(country_dropdown_value)
            contact_info_message = f"Please contact the following people to sort this issue : {', '.join(contact_info)}" if contact_info else ""
        _output = dbc.Alert(
            [
                html.H5("Absent Data!", className="alert-heading"),
                html.P(
                    "Emission report unavailable due to incomplete transport data",
                    style={"font-size":"small"}
                ),
                html.Hr(),
                html.P(
                    contact_info_message,
                    className="mb-0",
                    style={"font-size":"small"}
                ),
            ],
            color="danger"
        ) 

    return _output 


@app.long_callback(
    output=[
        Output(component_id="data_table_panel", component_property='children'),
        Output(component_id="aggregate_data_panel", component_property='children'),
        Output(component_id='starter_image_panel', component_property='style'),
        Output(component_id='output_navigator', component_property='value'),

        Output(component_id='ghg_data',component_property='data'),
        Output(component_id='ghg_aggregate_data_country',component_property='data'),
        Output(component_id='ghg_aggregate_data_account',component_property='data'),
        Output(component_id='ghg_aggregate_data_year',component_property='data'),
        Output(component_id='file_name',component_property='data'),
    ],
    inputs=[
        [Input({"type": "list-item", "index": ALL}, "n_clicks")],
        [State({"type": "list-item", "index": ALL}, "children")],
        Input(component_id='ReportsButton', component_property="n_clicks"),

    ],
    running=[
        (Output("common_spinner", "style"), {"width": "3rem", "height": "3rem",'position':'fixed','left':'60%','top':'45%',"display":"flex","z-index":"1001"}, {"display":"none"}),
    ],
    prevent_initial_call=True,
)
def display_data(*args,):

    print(f"ingetdata")

    with open("tempsol","r") as fob:
        _ = fob.read()

    if _ == "X":
        with open("tempsol","w") as fob:
            fob.write("")
        return  dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, None


    ctx = dash.callback_context
    if not ctx.triggered :
        return  dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, None
    
    if ctx.triggered_id == "ReportsButton":
        file_name_list = []
        for data in args[1][0]:
            file_name_list.append(data.get("props",{}).get("children",[{}])[2])
        
        df_list= []
        for file_name in file_name_list:
            sheet_names = pd.ExcelFile(os.path.join(reports_directory, file_name)).sheet_names
            df = pd.read_excel(os.path.join(reports_directory, file_name), skiprows=1, sheet_name=sheet_names[-1])

            parts = file_name.split("_")
            country = parts[0]
            account = parts[1]
            year = parts[-1].split(".")[0]

            df["GHGRP_COUNTRY"] = country
            df["GHGRP_ACCOUNT"] = account
            df["GHGRP_YEAR"] = year

            df_list.append(df)
        
        df = pd.concat(df_list, ignore_index=True)
        file_name="output.xlsx"


    else:
        
        clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
        clicked_id = json.loads(clicked_id).get("index")

        file_name = args[1][0][clicked_id].get("props",{}).get("children",[{}])[2]

        sheet_names = pd.ExcelFile(os.path.join(reports_directory, file_name)).sheet_names
        df = pd.read_excel(os.path.join(reports_directory, file_name), skiprows=1, sheet_name=sheet_names[-1])

        parts = file_name.split("_")
        country = parts[0]
        account = parts[1]
        year = parts[-1].split(".")[0]

        df["GHGRP_COUNTRY"] = country
        df["GHGRP_ACCOUNT"] = account
        df["GHGRP_YEAR"] = year

    ghg_data_output = dbc.Container(
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            page_size=9
        ),
        style={'width': '100%', 'overflowY': 'scroll'}  # Set a fixed height and enable vertical scrolling
    )

    #aggregatedata

    df_grp_country = df.groupby('GHGRP_COUNTRY').agg({
        'co2_equivalent_[t]_wtw': 'sum',
        'co2_equivalent_[t]_ttw': 'sum',
        'co2_equivalent_[t]_wtt': 'sum',
        'distances_[km]': 'sum'
    }).reset_index()

    df_grp_account = df.groupby('GHGRP_ACCOUNT').agg({
        'co2_equivalent_[t]_wtw': 'sum',
        'co2_equivalent_[t]_ttw': 'sum',
        'co2_equivalent_[t]_wtt': 'sum',
        'distances_[km]': 'sum'
    }).reset_index()

    df_grp_year =  df.groupby('GHGRP_YEAR').agg({
        'co2_equivalent_[t]_wtw': 'sum',
        'co2_equivalent_[t]_ttw': 'sum',
        'co2_equivalent_[t]_wtt': 'sum',
        'distances_[km]': 'sum'
    }).reset_index()


    ghg_aggregate_data_output = dbc.Container(
        children=[
            html.H6("Aggregate by Country"),
            dash_table.DataTable(
                id='df_grp_country',
                columns=[{"name": i, "id": i} for i in df_grp_country.columns],
                data=df_grp_country.to_dict('records'),
                style_table={"padding":"1rem 0rem"}
            ),
            html.H6("Aggregate by Account"),
            dash_table.DataTable(
                id='df_grp_account',
                columns=[{"name": i, "id": i} for i in df_grp_account.columns],
                data=df_grp_account.to_dict('records'),
                style_table={"padding":"1rem 0rem"}
            ),
            html.H6("Aggregate by Year"),
            dash_table.DataTable(
                id='df_grp_year',
                columns=[{"name": i, "id": i} for i in df_grp_year.columns],
                data=df_grp_year.to_dict('records'),
                style_table={"padding":"1rem 0rem"}
            ),
        ],
        style={'width': '100%', 'overflowY': 'scroll', 'height':'55vh'}
    )

    
    return ghg_data_output, ghg_aggregate_data_output, {"display":"none"}, 1, compress_df_to_string(df), compress_df_to_string(df_grp_country), compress_df_to_string(df_grp_account), compress_df_to_string(df_grp_year), file_name


@app.long_callback(
    output=[
        Output(component_id="data_table_panel",component_property="style"),
        Output(component_id="aggregate_data_panel",component_property="style"),
        Output(component_id="download", component_property="data"),
    ],
    inputs=[
        Input(component_id='output_navigator', component_property='value'),
        State(component_id='ghg_data',component_property='data'),
        State(component_id='ghg_aggregate_data_country',component_property='data'),
        State(component_id='ghg_aggregate_data_account',component_property='data'),
        State(component_id='ghg_aggregate_data_year',component_property='data'),
        State(component_id='file_name',component_property='data'),
    ],
    running=[
        (Output("common_spinner", "style"), {"width": "3rem", "height": "3rem",'position':'fixed','left':'60%','top':'45%',"display":"flex","z-index":"1001"}, {"display":"none"}),
    ],
    prevent_initial_call=True
)
def option_panel(output_navigator_value, ghg_data, ghg_aggregate_data_country, ghg_aggregate_data_account, ghg_aggregate_data_year, file_name):

        if(output_navigator_value==1):
            return {"display":"inline-grid"},{"display":"none"}, dash.no_update
        elif(output_navigator_value==2):
            return {"display":"none"},{"display":"inline-grid"}, dash.no_update
        elif(output_navigator_value==3):

            df = decompress_string_to_df(ghg_data)

            df_grp_country = decompress_string_to_df(ghg_aggregate_data_country)
            df_grp_account = decompress_string_to_df(ghg_aggregate_data_account)
            df_grp_year = decompress_string_to_df(ghg_aggregate_data_year)

            # Create a buffer to store the Excel file
            with pd.ExcelWriter(os.path.join("__pycache__",file_name), engine='xlsxwriter') as writer:
                # Write df to a sheet named after country
                df.to_excel(writer, sheet_name="data", index=False)
                
                # Write aggregated data to a sheet named "aggregate data"
                df_grp_country.to_excel(writer, sheet_name='aggregate data', startrow=1, index=False)
                df_grp_account.to_excel(writer, sheet_name='aggregate data', startrow=len(df_grp_country) + 3, index=False)
                df_grp_year.to_excel(writer, sheet_name='aggregate data', startrow=len(df_grp_country) + len(df_grp_account) + 5, index=False)
                
                # Write headers for each section
                worksheet = writer.sheets['aggregate data']
                worksheet.write(0, 0, 'Aggregate by Country')
                worksheet.write(len(df_grp_country) + 2, 0, 'Aggregate by Account')
                worksheet.write(len(df_grp_country) + len(df_grp_account) + 4, 0, 'Aggregate by Year')


            return dash.no_update, dash.no_update, dcc.send_file(os.path.join("__pycache__",file_name))
            


if __name__ == "__main__":
    app.run_server(debug=True, port=8000)