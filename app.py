import pandas as pd
import plotly.graph_objects as go
# pip install dash (version 2.0.0 or higher)
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import json

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# -- Import and clean data (importing csv into pandas)
df = pd.read_csv('web_mines_proba.csv')

# ------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1("Landmines Risk Prediction in our different models",
                className='text-center text-primary mb-4'), width=12)
    ),

    dbc.Row([
        dbc.Col(html.H5("Choose the model")),
        dbc.Col(html.H5("Choose the map layer")),
        # dbc.Col(html.H5("Show the label"))
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="model",
                         options=[
                             {"label": "LGBM", "value": 'LGBM'},
                             {"label": "LR", "value": 'LR'},
                             {"label": "SVM", "value": 'SVM'}],
                         multi=False,
                         value='LGBM')],
                ),
        dbc.Col([
            dcc.Dropdown(id="layer",
                         options=[
                             {"label": "Street", "value": 'streets'},
                             {"label": "Satellite Streets", "value": 'satellite'},
                             {"label": "Outdoors", "value": 'outdoors'}],
                         multi=False,
                         value='streets'), ],
                ),
    ]),
    html.Hr(),


    dbc.Row(html.H5("Choose the label")),

    dbc.Checklist(
        id="all-or-none",
        options=[{"label": "Select All", "value": "All"}],
        value=["All"],
        labelStyle={"display": "inline-block"},
    ),

    dbc.Checklist(id="recycling_type",
                  value=[x for x in sorted(df['mines_outcome'].unique())],
                  options=[
                      {'value': -1, 'label': 'Unknown'},
                      {'value': 0, 'label': 'Negative'},
                      {'value': 1, 'label': 'Positive'},


                      #  {'value': x, 'label': str(x), 'label_id': str(x)} for x in sorted(df['mines_outcome'].unique())
                  ]),


    html.Hr(),


    # search bar for searching address
    dbc.Row([
        dbc.Textarea(id='address-search-tab1',
                        placeholder='Search for the street or area'),
        dbc.Button('Find', id='search-address-button-tab1', n_clicks=0),
        html.P(id='no-result-alert')
    ]),

    dbc.Row(dcc.Graph(id='map', figure={}))

])


# ------------------------------------------------------------------------------
@app.callback(
    [Output(component_id='map', component_property='figure'),
     Output('no-result-alert', 'children')],
    [Input(component_id='model', component_property='value'),
     Input(component_id='layer', component_property='value'),
     Input('recycling_type', 'value'),
     Input('search-address-button-tab1', 'n_clicks')],
    State('address-search-tab1', 'value')
)
def update_graph(option_slctd, layer, chosen_label, n_clicks, address_search_1):

    mapbox_access_token = 'pk.eyJ1IjoicWl3YW5nYWFhIiwiYSI6ImNremtyNmxkNzR5aGwyb25mOWxocmxvOGoifQ.7ELp2wgswTdQZS_RsnW1PA'

    colorList = ['deepskyblue', 'lime', 'red']
    labelList = [-1, 0, 1]

    for item in zip(labelList, colorList):
        df.loc[df['mines_outcome'] == item[0],
               'colorBasedLabel'] = item[1]

    df_sub = df[(df['mines_outcome'].isin(chosen_label))]

    # scl = [0, "rgb(150,0,90)"], [0.125, "rgb(0, 0, 200)"], [0.25, "rgb(0, 25, 255)"],\
    #     [0.375, "rgb(0, 152, 255)"], [0.5, "rgb(44, 255, 150)"], [0.625, "rgb(151, 255, 0)"],\
    #     [0.75, "rgb(255, 234, 0)"], [0.875, "rgb(255, 111, 0)"], [
    #     1, "rgb(255, 0, 0)"]

    scl = [(0, "red"), (0.5, "yellow"), (1, "rgb(28,238,238)")]
    # Plotly Express
    locations = [go.Scattermapbox(
        lat=df['LATITUD_Y'],
        lon=df['LONGITUD_X'],
        hovertext=df["{}".format(option_slctd)],
        # text = df['Globvalue'].astype(str) + ' inches',
        marker=dict(
            color=df["{}".format(option_slctd)],
            colorscale=scl,
            reversescale=True,
            opacity=0.7,
            size=8,
            colorbar=dict(
                titleside="right",
                outlinecolor="rgba(68, 68, 68, 0)",
                ticks="outside",
                showticksuffix="last",
                dtick=0.1
            )
        )
    ),
        go.Scattermapbox(
        lat=df_sub['LATITUD_Y'],
        lon=df_sub['LONGITUD_X'],
        marker={'size': 10, 'color': df_sub['colorBasedLabel']}

    )]
    if n_clicks == 0:
        layout = go.Layout(
            uirevision='foo',  # preserves state of figure/map after callback activated
            # clickmode='event+select',
            hovermode='closest',
            hoverdistance=2,
            showlegend=False,
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),

            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                style='{}'.format(layer),
                center=dict(
                    lat=5.920689177,
                    lon=-75.10525796
                ),
                pitch=40,
                zoom=9
            ),
        )

        return{
            'data': locations,
            'layout': layout
        }, None

    else:
        # Geocode the lat-lng using Google Maps API
        google_api_key = 'AIzaSyDitOkTVs4g0ibg_Yt04DQqLaUYlxZ1o30'

        # Adding Uniontown PA to make the search more accurate (to generalize)
        address_search = address_search_1 + ' Antioquia, Colombia'

        params = {'key': google_api_key,
                  'address': address_search}

        url = 'https://maps.googleapis.com/maps/api/geocode/json?'

        response = requests.get(url, params)
        result = json.loads(response.text)

        if result['status'] not in ['INVALID_REQUEST', 'ZERO_RESULTS']:

            lat = result['results'][0]['geometry']['location']['lat']
            lon = result['results'][0]['geometry']['location']['lng']

            layout = go.Layout(
                uirevision=address_search,
                hovermode='closest',
                hoverdistance=2,
                showlegend=False,
                autosize=True,
                margin=dict(l=0, r=0, t=0, b=0),

                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=25,
                    style='{}'.format(layer),
                    center=dict(
                        lat=lat,
                        lon=lon
                    ),
                    pitch=40,
                    zoom=15
                ),
            )
            return {
                'data': locations,
                'layout': layout
            }, None

        else:
            layout = go.Layout(
                uirevision='foo',  # preserves state of figure/map after callback activated
                # clickmode='event+select',
                hovermode='closest',
                hoverdistance=2,
                showlegend=False,
                autosize=True,
                margin=dict(l=0, r=0, t=0, b=0),

                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=25,
                    style='{}'.format(layer),
                    center=dict(
                        lat=5.920689177,
                        lon=-75.10525796
                    ),
                    pitch=40,
                    zoom=9
                ),
            )

        return{
            'data': locations,
            'layout': layout
        }, 'Invalid Address!'


@app.callback(
    Output("recycling_type", "value"),
    [Input("all-or-none", "value")],
    [State("recycling_type", "options")],
)
def select_all_none(all_selected, options):
    all_or_none = []
    all_or_none = [option["value"] for option in options if all_selected]
    return all_or_none


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
