import pandas as pd
import plotly.graph_objects as go
# pip install dash (version 2.0.0 or higher)
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# -- Import and clean data (importing csv into pandas)
df = pd.read_csv('web_mines_proba.csv')
labels = [-1, 0, 1]

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
        # dbc.Col(
        #     dcc.Checklist(id="label",
        #                   value=[x for x in df['mines_outcome']],
        #                   options=[{'label': str(x), 'value': x} for x in labels])

        # )
    ]),


    dbc.Row(html.Br()),

    dbc.Row(dcc.Graph(id='map', figure={}))

])


# ------------------------------------------------------------------------------
@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='model', component_property='value'),
     Input(component_id='layer', component_property='value')]
    #  Input('label', 'value')
)
def update_graph(option_slctd, layer):

    mapbox_access_token = 'pk.eyJ1IjoicWl3YW5nYWFhIiwiYSI6ImNremtyNmxkNzR5aGwyb25mOWxocmxvOGoifQ.7ELp2wgswTdQZS_RsnW1PA'

    dff = df.copy()

    scl = [0, "rgb(150,0,90)"], [0.125, "rgb(0, 0, 200)"], [0.25, "rgb(0, 25, 255)"],\
        [0.375, "rgb(0, 152, 255)"], [0.5, "rgb(44, 255, 150)"], [0.625, "rgb(151, 255, 0)"],\
        [0.75, "rgb(255, 234, 0)"], [0.875, "rgb(255, 111, 0)"], [
        1, "rgb(255, 0, 0)"]
    # Plotly Express
    locations = [go.Scattermapbox(
        lat=dff['LATITUD_Y'],
        lon=dff['LONGITUD_X'],
        hovertext=dff["{}".format(option_slctd)],
        # text = df['Globvalue'].astype(str) + ' inches',
        marker=dict(
            color=dff["{}".format(option_slctd)],
            colorscale=scl,
            reversescale=True,
            opacity=0.7,
            size=10,
            colorbar=dict(
                titleside="right",
                outlinecolor="rgba(68, 68, 68, 0)",
                ticks="outside",
                showticksuffix="last",
                dtick=0.1
            )
        )
    )]

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
                lat=5.9,
                lon=-75
            ),
            pitch=40,
            zoom=8
        ),
    )

    return{
        'data': locations,
        'layout': layout
    }


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
