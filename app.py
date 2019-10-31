import dash
import dash_table
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import pandas as pd
import os


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash(__name__)
#app.config['SECRET_KEY'] = 'PaulaChartAudits'

VALID_USERNAME_PASSWORD_PAIRS = [
     ['paula', 'coconut']
 ]

auth = dash_auth.BasicAuth(
     app,
     VALID_USERNAME_PASSWORD_PAIRS
 )

files = [(x, x.split(' ')[-1].replace('(', '').replace(')', '').replace('.csv', '')) for x in os.listdir('data') if x[-3:] == 'csv']

def get_files(unit):
    return [x for x in files if x[0][:3] == unit]

mic_files = get_files('MIC')
surg_services_files = get_files('Sur')
ped_files = get_files('PED')

def get_df_unit(unit_files, starting_column):
    df_unit = pd.read_csv('data//{0}'.format(unit_files[0][0]))
    df_unit = df_unit[df_unit.columns[starting_column:]]
    df_unit.insert(0, 'Year-Month', unit_files[0][1][:7])
    for x in unit_files[1:]:
        df = pd.read_csv('data//{0}'.format(x[0]))
        df = df[df.columns[starting_column:]]
        df.insert(0, 'Year-Month', x[1][:7])
        df_unit = df_unit.append(df)
    df_unit.fillna('Blank', inplace=True)
    return df_unit

df_mic = get_df_unit(mic_files, 4)
#mic_columns = [x.split(':')[-1].split('>>')[-1].strip() for x in df_mic.columns]
#df_mic.columns = mic_columns

df_surg = get_df_unit(surg_services_files, 6)
df_peds = get_df_unit(ped_files, 4)

def get_percents(df):
    # returns a list that is the percent of 'Yes' for each column
    counts = [df[x].value_counts() for x in df]
    percents = []
    for x in counts:
        if 'Yes' not in x:
            percent = 0
        elif 'No' not in x:
            percent = 100
        else:
            percent = int(100 * x['Yes'] / (x['Yes'] + x['No']))
        percents.append(percent)
    return percents

def get_month_percents(df):
    # returns list of dicts that such that column: percent
    # each dict is for a month of data
    month_percents = []
    for i in df['Year-Month'].unique():
        df_2 = df.loc[df['Year-Month']==i]
        month_percent = get_percents(df_2)
        month_dict = {k: v for k, v in zip(df_2.columns, month_percent)}
        month_dict['Year-Month']=i
        month_percents.append(month_dict)
    return month_percents

mic_month_percents = get_month_percents(df_mic)
same_day_month_percents = get_month_percents(df_surg)
peds_month_percents = get_month_percents(df_peds)

#all_percents = get_percents(df_mic)
#all_dict = {k: v for k, v in zip(df_mic.columns, all_percents)}
#all_dict['Year-Month']='Total'
#mic_month_percents.append(all_dict)

def get_all_percents(df):
    # takes a df and returns a dict that is the cumulative total of percents for each column as column: percent
    all_percents = get_percents(df)
    all_dict = {k: v for k, v in zip(df.columns, all_percents)}
    all_dict['Year-Month'] = 'Total'
    return all_dict

mic_all_dict = get_all_percents(df_mic)
mic_month_percents.append(mic_all_dict)

same_day_all_dict = get_all_percents(df_surg)
same_day_month_percents.append(same_day_all_dict)

peds_all_dict = get_all_percents(df_peds)
peds_month_percents.append(peds_all_dict)


app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('MIC Chart Audits', href='/page-1'),
    html.Br(),
    dcc.Link('Same Day Surgery Chart Audits', href='/page-2'),
    html.Br(),
    dcc.Link('PEDs Chart Audits', href='/page-3'),
])

mic_audits_layout = html.Div([
    html.Div(id='mic_audits_conent'),
    html.Br(),
    dcc.Link('Same Day Surgery Chart Audits', href='/page-2'),
    html.Br(),
    dcc.Link('PEDs Chart Audits', href='/page-3'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
    html.H1(children='MIC Chart Audits', style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Hr()
        ]),
        html.Div([
            dash_table.DataTable(
                id='mic_table',
                row_selectable='single',
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_cell={'height': '25px',
                    'width': '100px',
                    'whiteSpace': 'normal'
                            },
                columns=[{'name': x, 'id': x} for x in df_mic.columns.values],
                data=mic_month_percents,
                fixed_rows={'headers': True},
            )
        ],
        style={'padding': 15}
        ),
        html.Div([
            dcc.Graph(
                id='mic_bar_chart',
                figure={
                    'data': [
                        {'x': [x for x in mic_all_dict.keys()][1:],
                         'y': [x for x in mic_all_dict.values()][1:],
                         'type': 'bar',
                         'name': 'MIC Totals'},
                    ],
                    'layout': {
                        'title': 'MIC Totals',
                    }
                }
            )
        ]),
        html.Div([
            html.Br(),
            dash_table.DataTable(
                id='mic_table_rows',
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_cell={'height': '25px',
                    'width': '100px',
                    'whiteSpace': 'normal'
                            },
                columns=[{'name': x, 'id': x} for x in df_mic.columns.values],
                data=df_mic.to_dict('records'),
                fixed_rows={'headers': True},
            )
        ],
            style={'padding': 15}
        ),
        html.Div([
            html.Hr()
        ]),
    ])
], className='page')

@app.callback(
    Output('mic_bar_chart', 'figure'),
    [Input('mic_table', 'selected_rows')]
)
def update_bar_chart(selected_row_data):
    #selected row data is simply the index number of the row as a list - ex [0]
    if selected_row_data is None:
        figure = {
            'data': [
                {'x': [x for x in mic_all_dict.keys()][1:],
                 'y': [x for x in mic_all_dict.values()][1:],
                 'type': 'bar',
                 'name': 'MIC Totals'},
            ],
            'layout': {
                'title': 'MIC Totals',
            }
        }
    else:
        row_index = selected_row_data[0]
        figure = {
            'data': [
                {'x': [x for x in mic_month_percents[row_index].keys()][1:],
                 'y': [x for x in mic_month_percents[row_index].values()][1:],
                 'type': 'bar',
                 'name': 'MIC Total'},
            ],
            'layout': {
                'title': 'MIC Chart Audits for {0}'.format(mic_month_percents[row_index]['Year-Month']),
            }
        }
    return figure

@app.callback(
    Output('mic_table_rows', 'data'),
    [Input('mic_table', 'selected_rows')]
)
def update_mic_table_rows(selected_row_data):
    #selected row data is simply the index number of the row as a list - ex [0]
    year_month_values = df_mic['Year-Month'].unique()
    if not selected_row_data or selected_row_data[0] + 1 > len(year_month_values):
        #get most recent year-month
        row_index = len(year_month_values) - 1
    else:
        row_index = selected_row_data[0]
    data = df_mic.loc[df_mic['Year-Month'] == year_month_values[row_index]].to_dict('records')
    return data

same_day_audits_layout = html.Div([
    html.Div(id='same_day_audits_conent'),
    html.Br(),
    dcc.Link('MIC Chart Audits', href='/page-1'),
    html.Br(),
    dcc.Link('PEDs Chart Audits', href='/page-3'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
    html.H1(children='Same Day Surgery Chart Audits', style={'textAlign': 'center'}),
    html.Div([
        html.Hr()
    ]),
    html.Div([
        dash_table.DataTable(
            id='same_day_table',
            row_selectable='single',
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_cell={'height': '25px',
                        'width': '100px',
                        'whiteSpace': 'normal'
                        },
            columns=[{'name': x, 'id': x} for x in df_surg.columns.values],
            data=same_day_month_percents,
            fixed_rows={'headers': True},
        )
    ],
        style={'padding': 15}
    ),
    html.Div([
            dcc.Graph(
                id='same_day_bar_chart',
                figure={
                    'data': [
                        {'x': [x for x in same_day_all_dict.keys()][1:],
                         'y': [x for x in same_day_all_dict.values()][1:],
                         'type': 'bar',
                         'name': 'Same Day Surgery Totals'},
                    ],
                    'layout': {
                        'title': 'Same Day Surgery Totals',
                    }
                }
            )
        ]),
    html.Div([
            html.Br(),
            dash_table.DataTable(
                id='same_day_table_rows',
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_cell={'height': '25px',
                    'width': '100px',
                    'whiteSpace': 'normal'
                            },
                columns=[{'name': x, 'id': x} for x in df_surg.columns.values],
                data=df_surg.to_dict('records'),
                fixed_rows={'headers': True},
            )
        ],
            style={'padding': 15}
        )
    ])

@app.callback(
    Output('same_day_bar_chart', 'figure'),
    [Input('same_day_table', 'selected_rows')]
)
def update_same_day_bar_chart(selected_row_data):
    #selected row data is simply the index number of the row as a list - ex [0]
    if selected_row_data is None:
        figure = {
            'data': [
                {'x': [x for x in same_day_all_dict.keys()][1:],
                 'y': [x for x in same_day_all_dict.values()][1:],
                 'type': 'bar',
                 'name': 'Same Day Totals'},
            ],
            'layout': {
                'title': 'Same Day Totals',
            }
        }
    else:
        row_index = selected_row_data[0]
        figure = {
            'data': [
                {'x': [x for x in same_day_month_percents[row_index].keys()][1:],
                 'y': [x for x in same_day_month_percents[row_index].values()][1:],
                 'type': 'bar',
                 'name': 'Same Day Total'},
            ],
            'layout': {
                'title': 'Same Day Chart Audits for {0}'.format(same_day_month_percents[row_index]['Year-Month']),
            }
        }
    return figure

@app.callback(
    Output('same_day_table_rows', 'data'),
    [Input('same_day_table', 'selected_rows')]
)
def update_same_day_table_rows(selected_row_data):
    #selected row data is simply the index number of the row as a list - ex [0]
    year_month_values = df_surg['Year-Month'].unique()
    if not selected_row_data or selected_row_data[0] + 1 > len(year_month_values):
        #get most recent year-month
        row_index = len(year_month_values) - 1
    else:
        row_index = selected_row_data[0]
    data = df_surg.loc[df_surg['Year-Month'] == year_month_values[row_index]].to_dict('records')
    return data

peds_audits_layout = html.Div([
    html.Div(id='peds_audits_conent'),
    html.Br(),
    dcc.Link('MIC Chart Audits', href='/page-1'),
    html.Br(),
    dcc.Link('Same Day Surgery Chart Audits', href='/page-2'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
    html.H1(children='PEDs Chart Audits', style={'textAlign': 'center'}),
    html.Div([
        html.Hr()
    ]),
    html.Div([
        dash_table.DataTable(
            id='peds_table',
            row_selectable='single',
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_cell={'height': '25px',
                        'width': '100px',
                        'whiteSpace': 'normal'
                        },
            columns=[{'name': x, 'id': x} for x in df_peds.columns.values],
            data=peds_month_percents,
            fixed_rows={'headers': True},
        )
    ],
        style={'padding': 15}
    ),
    html.Div([
        dcc.Graph(
            id='peds_bar_chart',
            figure={
                'data': [
                    {'x': [x for x in peds_all_dict.keys()][1:],
                     'y': [x for x in peds_all_dict.values()][1:],
                     'type': 'bar',
                     'name': 'PEDs Totals'},
                ],
                'layout': {
                    'title': 'PEDS Totals',
                }
            }
        )
    ]),
    html.Div([
        html.Br(),
        dash_table.DataTable(
            id='peds_table_rows',
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_cell={'height': '25px',
                        'width': '100px',
                        'whiteSpace': 'normal'
                        },
            columns=[{'name': x, 'id': x} for x in df_peds.columns.values],
            data=df_peds.to_dict('records'),
            fixed_rows={'headers': True},
        )
    ],
        style={'padding': 15}
    )
    ])

@app.callback(
    Output('peds_bar_chart', 'figure'),
    [Input('peds_table', 'selected_rows')]
)
def update_peds_bar_chart(selected_row_data):
    #selected row data is simply the index number of the row as a list - ex [0]
    if selected_row_data is None:
        figure = {
            'data': [
                {'x': [x for x in peds_all_dict.keys()][1:],
                 'y': [x for x in peds_all_dict.values()][1:],
                 'type': 'bar',
                 'name': 'PEDs Totals'},
            ],
            'layout': {
                'title': 'PEDs Totals',
            }
        }
    else:
        row_index = selected_row_data[0]
        figure = {
            'data': [
                {'x': [x for x in peds_month_percents[row_index].keys()][1:],
                 'y': [x for x in peds_month_percents[row_index].values()][1:],
                 'type': 'bar',
                 'name': 'PEDs Total'},
            ],
            'layout': {
                'title': 'PEDs Chart Audits for {0}'.format(same_day_month_percents[row_index]['Year-Month']),
            }
        }
    return figure

@app.callback(
    Output('peds_table_rows', 'data'),
    [Input('peds_table', 'selected_rows')]
)
def update_peds_table_rows(selected_row_data):
    #selected row data is simply the index number of the row as a list - ex [0]
    year_month_values = df_peds['Year-Month'].unique()
    if not selected_row_data or selected_row_data[0] + 1 > len(year_month_values):
        #get most recent year-month
        row_index = len(year_month_values) - 1
    else:
        row_index = selected_row_data[0]
    data = df_peds.loc[df_peds['Year-Month'] == year_month_values[row_index]].to_dict('records')
    return data

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return mic_audits_layout
    elif pathname == '/page-2':
        return same_day_audits_layout
    elif pathname == '/page-3':
        return peds_audits_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here



if __name__ == '__main__':
    app.run_server(debug=True, port=5000)