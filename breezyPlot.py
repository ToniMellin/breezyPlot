# -*- coding: utf-8 -*-
"""breezyPlot.py

Simple dash app for quick and easy plotting of CSV/XLS/XLSX data files.

@Author: https://github.com/ToniMellin

* Copyright (C) 2026 Toni Mellin - All Rights Reserved
* You may use, distribute and modify this code under the
* terms of the MIT license.
*
* See file LICENSE or go to 
* https://github.com/ToniMellin/breezyPlot/blob/master/LICENSE
* for full license details.
"""

import base64
import io
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.express as px
import dash_bootstrap_components as dbc

dbc_css = "assets/dbc.css"

# Initialize the Dash application
app = dash.Dash(__name__, title="breezyPlot",
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP,
                    dbc.icons.BOOTSTRAP,  # Gives access to bi-sun-fill and bi-moon-stars-fill icons
                    dbc_css
                ],)

# Custom Styles
UPLOAD_STYLE = {
    'width': '100%',
    'height': '120px',
    'lineHeight': '120px',
    'borderWidth': '2px',
    'borderStyle': 'dashed',
    'borderRadius': '8px',
    'textAlign': 'center',
    'borderColor': '#4A90E2',
    'cursor': 'pointer',
    'margin-bottom': '20px',
    'transition': 'all 0.3s ease-in-out'
}

app.layout = dbc.Container([html.Div(style={'fontFamily': 'Segoe UI, Helvetica, Arial, sans-serif', 'padding': '30px', 'minHeight': '100vh'}, 
    children=[
    html.Div(style={'maxWidth': '1900px', 'margin': '0 auto', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.08)'}, children=[
        
        # Header
        html.H1("breezyPlot", style={'textAlign': 'center', 'color': '#2C3E50', 'marginBottom': '30px', 'fontWeight': '600'}),

        # TODO edit the dark / light mode button
        html.Div(
            [
                # Toggle switch
                            html.Div([
                                html.I(className="bi bi-sun-fill me-2"),
                                dbc.Switch(id="theme-switch", value=False, className="d-inline-block"),
                                html.I(className="bi bi-moon-stars-fill ms-2"),
                            ], className="d-flex align-items-center mb-3"),
                dcc.Store(id="theme-store")
            ],
            className="d-flex align-items-center justify-content-end h-100", 
        ),
        
        # File Drag and Drop Box
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a File', style={'color': '#4A90E2', 'textDecoration': 'underline', 'fontWeight': 'bold'}),
                html.Span(' (Supports CSV, XLS, XLSX)', style={'color': '#7F8C8D', 'fontSize': '14px'})
            ]),
            style=UPLOAD_STYLE,
            multiple=False
        ),
        
        # Feedback and Error Banner
        html.Div(id='feedback-message', style={'marginBottom': '20px'}),

        html.Div(id='top-controls-container', style={'display': 'none', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '25px', 'border': '1px solid #E2E8F0'}, children=[
                    html.H3("Configure Plot Type", style={'marginTop': '0', 'color': '#34495E', 'marginBottom': '15px'}),
                    html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(220px, 1fr))', 'gap': '15px'}, children=[
        
                        #TODO add option for go or express type plots
                        # Plot Type
                        html.Div([
                            html.Label("Chart Type", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                            dcc.Dropdown(
                                id='chart-type',
                                options=[
                                    {'label': 'Scatter Plot', 'value': 'scatter'},
                                    {'label': 'Line Plot', 'value': 'line'},
                                    {'label': 'Bar Chart', 'value': 'bar'},
                                    {'label': 'Box Plot', 'value': 'box'},
                                    {'label': 'Histogram', 'value': 'histogram'}
                                ],
                                value='scatter',
                                clearable=False
                            )
                        ]),

                        # Plot machine
                        html.Div([
                            html.Label("Plotting engine", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                            dcc.Dropdown(
                                id='plot-engine',
                                options=[
                                    {'label': 'Express', 'value': 'express'},
                                    {'label': 'Graph objects', 'value': 'graph_objects'}
                                ],
                                value='express',
                                clearable=False
                            )
                        ]),

                        html.Div([
                                html.Label("Color template", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                                dcc.Dropdown(id='color-column', placeholder="Optional category...")
                                ])
                    ]),
                ]),

        # Container for controls (hidden until file is loaded successfully)
        html.Div(id='controls-container', style={'display': 'none', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '25px', 'border': '1px solid #E2E8F0'}, children=[
            html.H3("Configure Plot Parameters", style={'marginTop': '0', 'color': '#34495E', 'marginBottom': '15px'}),
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(220px, 1fr))', 'gap': '15px'}, children=[

                # X-Axis Selector
                html.Div([
                    html.Label("Select X-Axis Column", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Dropdown(id='xaxis-column', placeholder="Choose column...")
                ]),

                # Y-Axis Selector (Multiple variables allowed)
                html.Div([
                    html.Label("Select Y-Axis Column(s)", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Dropdown(id='yaxis-columns', multi=True, placeholder="Choose columns...")
                ]),

                # Y2-Axis Selector (Multiple variables allowed)
                #TODO greyout selection if incompatible chart type
                html.Div([
                    html.Label("Select Y2-Axis Column(s)", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Dropdown(id='y2axis-columns', multi=True, placeholder="Choose columns...")
                ])
            ]),
                        # Row 2: Secondary Features & Toggles
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(220px, 1fr))', 'gap': '15px', 'alignItems': 'center'}, children=[
                

                html.Div(id='barmode-wrapper', children=[
                    html.Label("Bar Display Mode", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.RadioItems(
                        id='bar-mode',
                        options=[{'label': ' Grouped', 'value': 'group'}, {'label': ' Stacked', 'value': 'stack'}],
                        value='group',
                        inputStyle={'marginRight': '5px', 'marginLeft': '10px'}
                    )
                ]),

                html.Div(id='trendline-wrapper', children=[
                    html.Label("Linear Trendline", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Checklist(
                        id='trendline-toggle',
                        options=[{'label': ' Add OLS Trendline', 'value': 'ols'}],
                        value=[]
                    )
                ]),

                html.Div([
                    html.Label("Axis Scaling", style={'fontWeight': 'bold', 'color': '#4A5568', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Checklist(
                        id='log-scale-toggle',
                        options=[
                            {'label': ' Log X-Axis', 'value': 'log_x'},
                            {'label': ' Log Y-Axis', 'value': 'log_y'}
                        ],
                        value=[],
                        inputStyle={'marginRight': '5px'}
                    )
                ])
            ])
        ], className='dbc'),

        # Graph Canvas Area
        dcc.Loading(
            id="loading-graph",
            type="circle",
            children=[
                html.Div(id='graph-container', children=[
                    dcc.Graph(id='indicator-graphic', style={'height': '550px'})
                ], style={'display': 'none'})
            ]
        ),

        # Hidden storage layer to hold structured dataframe data across callback requests
        dcc.Store(id='stored-data')
    ])
])

], 
fluid=True,
className='dbc'
)

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "Unsupported file format. Please upload a CSV, XLS, or XLSX file."
        return df, None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

# Callback 1: Handles upload parse, populates control dropdowns, and triggers control visibility
@app.callback(
    [Output('stored-data', 'data'),
     Output('xaxis-column', 'options'),
     Output('yaxis-columns', 'options'),
     Output('y2axis-columns', 'options'),
     Output('top-controls-container', 'style'),
     Output('controls-container', 'style'),
     Output('feedback-message', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_outputs(contents, filename):
    if contents is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, {'display': 'none'}, ''

    df, err = parse_contents(contents, filename)
    if err:
        error_banner = html.Div(err, style={'padding': '15px', 'color': '#C53030', 'borderRadius': '6px', 'border': '1px solid #FEB2B2'})
        return None, [], [], [], {'display': 'none'}, {'display': 'none'}, error_banner

    columns = [{'label': str(col), 'value': str(col)} for col in df.columns]
    success_banner = html.Div(f"✓ File successfully uploaded: {filename} ({df.shape[0]} rows, {df.shape[1]} columns)", 
                              style={'padding': '12px 15px', 'backgroundColor': '#C6F6D5', 'color': '#22543D', 'borderRadius': '6px', 'border': '1px solid #9AE6B4', 'fontWeight': '500'})

    return df.to_dict('records'), columns, columns, columns, {'display': 'block', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '25px', 'border': '1px solid #E2E8F0'}, {'display': 'block', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '25px', 'border': '1px solid #E2E8F0'}, success_banner

# Callback 2: Dynamic UI Toggle State based on Chart Type selection
@app.callback(
    [Output('y2axis-columns', 'disabled'),
     Output('barmode-wrapper', 'style'),
     Output('trendline-wrapper', 'style'),
     Output('yaxis-columns', 'placeholder')],
    Input('chart-type', 'value')
)
def toggle_control_visibility(chart_type):
    y2_disabled = chart_type in ['histogram', 'box']
    barmode_style = {'display': 'block'} if chart_type == 'bar' else {'display': 'none'}
    trendline_style = {'display': 'block'} if chart_type in ['scatter', 'line'] else {'display': 'none'}
    y_placeholder = "Optional for Histogram..." if chart_type == 'histogram' else "Choose column(s)..."
    
    return y2_disabled, barmode_style, trendline_style, y_placeholder

# Callback 3: Generates dynamic plot when controls are modified
@app.callback(
    [Output('graph-container', 'style'),
     Output('indicator-graphic', 'figure')],
    [Input('stored-data', 'data'),
     Input('chart-type', 'value'),
     Input('xaxis-column', 'value'),
     Input('yaxis-columns', 'value'),
     Input('y2axis-columns', 'value'),
    Input('color-column', 'value'),
     Input('bar-mode', 'value'),
     Input('trendline-toggle', 'value'),
     Input('log-scale-toggle', 'value')]
)
def update_graph(data, chart_type, xaxis_col, yaxis_cols, y2axis_cols, color, bar_mode, trendline, log_scale):
    if data is None or not xaxis_col or not yaxis_cols:
        # Hide chart window if details are missing
        empty_fig = px.scatter(title="Configure your X and Y axes in the panel above to generate visual metrics.")
        empty_fig.update_layout(font_color='#7F8C8D')
        return {'display': 'none'}, empty_fig

    df = pd.DataFrame(data)

    # Cast selection variables securely to lists
    if isinstance(yaxis_cols, str):
        yaxis_cols = [yaxis_cols]

    # Dynamically build configurations depending on plotting style choice
    if chart_type == 'scatter':
        fig = px.scatter(df, x=xaxis_col, y=yaxis_cols, title=f"{', '.join(yaxis_cols)} vs {xaxis_col}")
    elif chart_type == 'line':
        fig = px.line(df, x=xaxis_col, y=yaxis_cols, title=f"{', '.join(yaxis_cols)} vs {xaxis_col}")
    elif chart_type == 'bar':
        fig = px.bar(df, x=xaxis_col, y=yaxis_cols, barmode='group', title=f"{', '.join(yaxis_cols)} Grouped Comparison")
    elif chart_type == 'box':
        fig = px.box(df, x=xaxis_col, y=yaxis_cols, title=f"Distribution (Box Plot)")
    elif chart_type == 'histogram':
        fig = px.histogram(df, x=xaxis_col, y=yaxis_cols, barmode='overlay', title="Histogram Distribution")
    else:
        fig = px.scatter(df, x=xaxis_col, y=yaxis_cols)

    # Style modifications for crisp presentation
    fig.update_layout(
        margin={'l': 50, 'r': 30, 't': 50, 'b': 50},
        hovermode='closest',
        transition_duration=300,
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF'

        #TODO add dark mode support for plotly figures
    )
    fig.update_xaxes(showgrid=True, gridcolor='#E2E8F0', linecolor='#CBD5E0')
    fig.update_yaxes(showgrid=True, gridcolor='#E2E8F0', linecolor='#CBD5E0')

    return {'display': 'block'}, fig

# ── Clientside callback: sets data-bs-theme on <html> and logs to console ─────
app.clientside_callback(
    """
    function(is_dark) {
        console.log('[theme] switch fired, is_dark =', is_dark, typeof is_dark);
        var theme = is_dark ? 'dark' : 'light';
        document.documentElement.setAttribute('data-bs-theme', theme);
        console.log('[theme] set data-bs-theme =', document.documentElement.getAttribute('data-bs-theme'));
        return 'JS set data-bs-theme = ' + theme;
    }
    """,
    Output("theme-store", "data"),
    Input("theme-switch", "value"),
)

if __name__ == '__main__':
    app.run(debug=True, port=8050)