import pandas as pd
import numpy as np
import geopandas as gpd
import geojson
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import date
from plotly.subplots import make_subplots

# https://coolors.co/cf777e-69140e-a44200-d58936-fff94f

'''
TODO:
- RELATÓRIO!!! :)
- Meter tudo numa DB???
- Separar por mais ficheiros, está a ficar pesado :\\

- Mapas:
---- Labels mapas (https://plotly.com/python/hover-text-and-formatting/    https://plotly.com/python/legend/) ===== DONE
---- Atualizar o mapa da esquerda quando se carrega num neighbourhood ===== DONE
---- Meter um botão para alternar entre escala logaritmica e linear (muda slider e mapa da esquerda) ===== DONE
---- Tratar dos problemas dos sliders (ou simplesmente tirar) ===== DONE
---- Interação no mapa das esquerda para quando se carrega num neighbourhood, atualiza a linha temporal ===== TRYING
---- Bloquear botão que está a ser usado ===== TRYING

- Visualizaçao temporal:
---- Date picker e botao, ficam os 2 mamados em cima ===== DONE
---- Corrigir o style do botao ===== DONE
---- Centrar / mudar a disposiçao do date picker e botao ===== TRYING

- Visualizaçao extra:
---- Ordenar a legenda (https://plotly.com/python/reference/layout/#layout-legend) (acho que vou ter de inserir as coisas por ordem :) ) ===== DONE
---- Meter a legenda centrada ou em baixo do pie chart ===== DONE
---- Corrigir labels todas ===== DONE
'''

'''
DUVIDAS:
- Ter escalas linear e logaritmica nos mapas, faz sentido ou não? FAZ SE MUDAR O ESQUEMA DE CORES
- Cores para as linhas (usar o site do coolors e fixar 2 tons de verde e ver o que sai) AFINAL ESTA BOM EHEH
'''

# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

is_log = True
marks_log = {i: f'{i}' for i in range(8)}
marks_lin = {i: str(i) for i in range(0, 601, 100)}

## Data Cleaning
def corrige_precos(df, column):
    df[column] = df[column].fillna(0)
    df[column] = df[column].astype(str)
    df[column] = df[column].str.replace(',', '')
    df[column] = df[column].str.replace('$', '')
    df[column] = df[column].astype(float)

def corrige_datas(df, column):
    df[column] = pd.to_datetime(df[column], format="%Y-%m-%d")

def corrige_int(df, column):
    df[column] = df[column].astype(int)

def corrige_nan(df, column):
    df[column] = df[column].fillna(0)


## Reading Data
def read_data():
    print("--------------------------------\nReading all_data file")
    tudo = pd.read_csv("all_data.csv")

    print("Reading neighbourhoods_grouped file")
    neighbourhood_grouped = pd.read_csv("neighbourhood_grouped.csv")

    print("Reading houses file")
    houses = pd.read_csv("houses.csv")

    print("Reading neighbourhoods file")
    neighbourhoods = pd.read_csv("neighbourhoods.csv")

    print("Reading neighbourhoods.geojson file")
    geojson_airbnb = gpd.read_file("neighbourhoods.geojson")

    print("Reading all_data_unique file")
    tudo_unico = pd.read_csv("all_data_unique.csv")

    print("Reading bounding_boxes file")
    bb = pd.read_csv("bounding_boxes.csv")
    bb = bb.set_index("neighbourhood")

    return tudo, neighbourhood_grouped, houses, geojson_airbnb, neighbourhoods, tudo_unico, bb

tudo, neighbourhood_grouped, houses, geojson_airbnb, neighbourhoods, tudo_unico, bb = read_data()

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

@app.callback(
    [Output(component_id='mapa-limites', component_property='figure'),
    Output(component_id='price-slider-log', component_property='disabled'),
    Output(component_id='price-slider-lin', component_property='disabled')],
    [Input(component_id='price-slider-log', component_property='value'),
    Input(component_id='price-slider-lin', component_property='value'),
    Input(component_id='button_log', component_property='n_clicks_timestamp'),
    Input(component_id='button_lin', component_property='n_clicks_timestamp'),
    Input(component_id='mapa-limites', component_property='clickData')]
)
def grafico_mapa_limites(value_log, value_lin, button_log, button_lin, clickData):
    global is_log

    ctx = dash.callback_context.triggered[0]['prop_id']
    if ctx != "mapa-limites.clickData":
        clickData = None

    log = None
    lin = None

    print(f"> Range price (log): [{value_log[0]}, {value_log[1]}]")
    print(f"> Range price (lin): [{value_lin[0]}, {value_lin[1]}]")
    print(f'> Is_log: {is_log}')
    aux = neighbourhood_grouped

    if button_log > button_lin:
        is_log = True
    elif button_lin > button_log:
        is_log = False

    if is_log:
        log = False
        lin = True
        if clickData is None:
            fig_map = px.choropleth_mapbox(
                aux[aux['new_price'].between(value_log[0], value_log[1])],
                color="new_price",
                geojson=geojson_airbnb,
                featureidkey="properties.neighbourhood",
                locations="neighbourhood_cleansed",
                mapbox_style="carto-positron",
                center={'lat': 41.1, 'lon': -8.47},
                zoom=8,
                title='Average Price of Neighbourhoods',
                color_continuous_scale=px.colors.sequential.Inferno
            )

            fig_map.layout.coloraxis.colorbar.title = 'Log Price'
            fig_map.update_traces(hovertemplate='<b>Neighbourhood:</b> %{properties.neighbourhood}<br><b>Annual Average Price:</b> %{text}€<extra></extra>', text=np.round(aux.new_price, 2))
        
        else:
            local = clickData['points'][0]['location']

            fig_map = px.choropleth_mapbox(
                aux[aux['new_price'].between(value_log[0], value_log[1])],
                color="new_price",
                geojson=geojson_airbnb,
                featureidkey="properties.neighbourhood",
                locations="neighbourhood_cleansed",
                mapbox_style="carto-positron",
                center={'lat': bb.loc[local]["center_lat"], 'lon': bb.loc[local]["center_lon"]},
                zoom=11,
                title='Average Price of Neighbourhoods',
                color_continuous_scale=px.colors.sequential.Inferno
            )

            fig_map.layout.coloraxis.colorbar.title = 'Log Price'
            fig_map.update_traces(hovertemplate='<b>Neighbourhood:</b> %{properties.neighbourhood}<br><b>Annual Average Price:</b> %{text}€<extra></extra>', text=np.round(aux.new_price, 2))


    elif not is_log:
        log = True
        lin = False

        if clickData is None:
            fig_map = px.choropleth_mapbox(
                aux[aux['price'].between(value_lin[0], value_lin[1])],
                color="price",
                geojson=geojson_airbnb,
                featureidkey="properties.neighbourhood",
                locations="neighbourhood_cleansed",
                mapbox_style="carto-positron",
                center={'lat': 41.1, 'lon': -8.47},
                zoom=8,
                title='Average Price of Neighbourhoods',
                color_continuous_scale=px.colors.sequential.Oranges[::-1]
            )

            fig_map.layout.coloraxis.colorbar.title = 'Lin Price'
            fig_map.update_traces(hovertemplate='<b>Neighbourhood:</b> %{properties.neighbourhood}<br><b>Annual Average Price:</b> %{text}€<extra></extra>', text=np.round(aux.price, 2))
        else:
            local = clickData['points'][0]['location']

            fig_map = px.choropleth_mapbox(
                aux[aux['price'].between(value_lin[0], value_lin[1])],
                color="price",
                geojson=geojson_airbnb,
                featureidkey="properties.neighbourhood",
                locations="neighbourhood_cleansed",
                mapbox_style="carto-positron",
                center={'lat': bb.loc[local]["center_lat"], 'lon': bb.loc[local]["center_lon"]},
                zoom=11,
                title='Average Price of Neighbourhoods',
                color_continuous_scale=px.colors.sequential.Oranges[::-1]
            )

            fig_map.layout.coloraxis.colorbar.title = 'Lin Price'
            fig_map.update_traces(hovertemplate='<b>Neighbourhood:</b> %{properties.neighbourhood}<br><b>Annual Average Price:</b> %{text}€<extra></extra>', text=np.round(aux.price, 2))

    fig_map.update_layout(title_x=0.5, hoverlabel_bgcolor="white", margin=dict(t=75))

    return fig_map, log, lin


@app.callback(
    Output(component_id='mapa-pontos', component_property='figure'),
    [Input(component_id='mapa-limites', component_property='clickData'),
    Input(component_id='button_log', component_property='n_clicks_timestamp'),
    Input(component_id='button_lin', component_property='n_clicks_timestamp'),
    Input(component_id='price-slider-log', component_property='value'),
    Input(component_id='price-slider-lin', component_property='value'),]
)
def grafico_mapa_pontos(clickData, button_log, button_lin, value_log, value_lin):
    global is_log

    ctx = dash.callback_context.triggered[0]['prop_id']
    if ctx != "mapa-limites.clickData":
        clickData = None

    print("> Click Data:", clickData)
    casas = houses

    if button_log > button_lin:
        is_log = True
    elif button_lin > button_log:
        is_log = False

    if is_log:
        if clickData is None:
            fig_map_pontos = px.scatter_mapbox(
                casas[casas['new_price'].between(value_log[0], value_log[1])],
                color='new_price',
                lat="latitude",
                lon="longitude",
                hover_name="listing_id",
                center={'lat': 41.1, 'lon': -8.47},
                zoom=8,
                mapbox_style="carto-positron",
                title='Average Price of Listings',
                color_continuous_scale=px.colors.sequential.Inferno
            )
        else:
            local = clickData['points'][0]['location']

            fig_map_pontos = px.scatter_mapbox(
                casas[casas['new_price'].between(value_log[0], value_log[1])],
                color='new_price',
                lat="latitude",
                lon="longitude",
                hover_name="listing_id",
                center={'lat': bb.loc[local]["center_lat"], 'lon': bb.loc[local]["center_lon"]},
                zoom=11,
                mapbox_style="carto-positron",
                title='Average Price of Listings',
                color_continuous_scale=px.colors.sequential.Inferno
            )

        fig_map_pontos.layout.coloraxis.colorbar.title = 'Log Price'
        fig_map_pontos.update_traces(marker_size=11, hovertemplate='%{text}', text=[f'<b>Listing ID:</b> {i}<br><b>Annual Average Price:</b> {j}€<br><b>Coordinates</b>: ({k:.5f} N, {l:.5f} W)<extra></extra>' for i, j, k, l in zip(casas["listing_id"], np.round(casas["new_price"], 2), casas["latitude"], casas["longitude"])])
    
    elif not is_log:
        if clickData is None:
            fig_map_pontos = px.scatter_mapbox(
                casas[casas['price'].between(value_lin[0], value_lin[1])],
                color='price',
                lat="latitude",
                lon="longitude",
                hover_name="listing_id",
                center={'lat': 41.1, 'lon': -8.47},
                zoom=8,
                mapbox_style="carto-positron",
                title='Average Price of Listings',
                color_continuous_scale=px.colors.sequential.Oranges[::-1]
            )
        else:
            local = clickData['points'][0]['location']

            fig_map_pontos = px.scatter_mapbox(
                casas[casas['price'].between(value_lin[0], value_lin[1])],
                color='price',
                lat="latitude",
                lon="longitude",
                hover_name="listing_id",
                center={'lat': bb.loc[local]["center_lat"], 'lon': bb.loc[local]["center_lon"]},
                zoom=11,
                mapbox_style="carto-positron",
                title='Average Price of Listings',
                color_continuous_scale=px.colors.sequential.Oranges[::-1]
            )

        fig_map_pontos.layout.coloraxis.colorbar.title = 'Lin Price'
        fig_map_pontos.update_traces(marker_size=11, hovertemplate='%{text}', text=[f'<b>Listing ID:</b> {i}<br><b>Annual Average Price:</b> {j}€<br><b>Coordinates</b>: ({k:.5f} N, {l:.5f} W)<extra></extra>' for i, j, k, l in zip(casas["listing_id"], np.round(casas["price"], 2), casas["latitude"], casas["longitude"])])

    fig_map_pontos.update_layout(title_x=0.5, hoverlabel_bgcolor="white", margin=dict(t=75))

    return fig_map_pontos


@app.callback(
    Output(component_id='linha', component_property='figure'),
    [Input(component_id='date-picker', component_property='start_date'),
    Input(component_id='date-picker', component_property='end_date'),
    Input(component_id='mapa-pontos', component_property='clickData')]
)
def grafico_linha(start_date, end_date, clickData):
    print("> clickData:", clickData)
    print("> Start date:", start_date)
    print("> End date:", end_date)

    skrt = tudo.groupby("date")["price"].mean()  # Sacar média diaria de todas as casas
    skrt = skrt.reset_index()

    x = skrt[(skrt["date"] <= end_date) & (skrt["date"] >= start_date)]["date"]

    if clickData is not None:
        value = clickData['points'][0]['hovertext']

        fig = make_subplots(rows=2, cols=1)
        poasd = tudo[tudo["listing_id"] == value]  # Sacar id

        spot = poasd.iloc[0]["neighbourhood_cleansed"]  # Sacar o neighbourhood

        tyu = tudo.groupby(["date", "neighbourhood_cleansed"])[["price"]].mean()  # Juntar por data e neighbourhood e ver a média
        tyu = tyu.reset_index()
        # display(tyu[tyu["neighbourhood_cleansed"] == spot]["price"])  # Ver apenas pelo neighbourhood e preço
    
        fig.add_trace(
            go.Scatter(
                x=x,
                y=skrt["price"],
                mode='lines',
                name='Annual average price',
                hovertemplate="%{y:.2f}€"
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=tyu[tyu["neighbourhood_cleansed"] == spot]["price"],
                mode='lines',
                name='Average neighbourhood (' + spot + ') price',
                hovertemplate="%{y:.2f}€"
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=poasd["price"],
                mode='lines',
                name="Daily price of listing " + str(value),
                hovertemplate="%{y:.2f}€"
            ),
            row=1, col=1
        )

        pdn = tyu[tyu["neighbourhood_cleansed"] == spot][["price", "date"]]
        pdy = skrt[["price", "date"]]

        dados_std = []
        for i in pdn["date"]:
            row_pdn = np.array(pdn.loc[pdn["date"] == i, ["price"]])[0]
            row_pdy = np.array(pdy.loc[pdy["date"] == i, ["price"]])[0]
            dados_std.append([
                i,
                (row_pdy - row_pdn).tolist()[0]
            ])

        std = pd.DataFrame(dados_std, columns=["date", "price"])

        fig.add_trace(
            go.Scatter(
                x=x,
                y=std["price"],
                mode='lines',
                name="Difference between annual average and neighbourhood average",
                hovertemplate="%{y:.2f}€"
            ),
            row=2, col=1
        )

        fig.add_hline(
            y=0,
            line_dash='dot',
            row=2, col=1
        )

        fig.update_layout(
            title="Daily Average Prices",
            title_x=0.5,
            showlegend=False,
            xaxis={
                'fixedrange': True
            },
            yaxis={
                'title': 'Price',
                'fixedrange': True
            },
            xaxis2={
                'title': 'Date',
                'fixedrange': True
            },
            yaxis2={
                'title': 'Difference',
                'fixedrange': True
            },
            hovermode='x unified',
            margin=dict(t=75)
        )
    else:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=skrt["price"],
                mode='lines',
                name='Annual average price',
                hovertemplate="%{y:.2f}€"
            )
        )

        fig.update_layout(
            title="Daily Average Prices",
            title_x=0.5,
            showlegend=False,
            xaxis={
                'title': 'Date',
                'fixedrange': True
            },
            yaxis={
                'title': 'Price',
                'fixedrange': True 
            },
            hovermode='x unified',
            margin=dict(t=75)
        )

    return fig


@app.callback(
    Output(component_id='extra', component_property='figure'),
    Input(component_id='dropdown-pies', component_property='value')
)
def grafico_bar(value):
    print("> Bar chart:", value)
    cores = [
        'rgb(0,68,27)', 
        'rgb(0,88,35)',
        'rgb(0,109,44)',
        'rgb(8,116,50)',
        'rgb(17,124,56)',
        'rgb(35,139,69)',
        'rgb(42,147,75)',
        'rgb(50,155,81)',
        'rgb(65,171,93)',
        'rgb(77,177,99)',
        'rgb(90,183,105)',
        'rgb(116,196,118)',
        'rgb(127,201,127)',
        'rgb(138,206,136)',
        'rgb(149,211,145)',
        'rgb(161,217,155)',
        'rgb(180,225,173)',
        'rgb(189,229,182)',
        'rgb(199,233,192)',
        'rgb(214,239,208)',
        'rgb(221,242,216)',
        'rgb(229,245,224)',
        'rgb(238,248,234)',
        'rgb(247,252,245)',
    ]
    if value == "Accommodates" or value == "Bathrooms" or value == "Bedrooms" or value == "Beds":
        texto = value.lower()

        tudo_unico_mean = tudo_unico.groupby(texto).mean()
        tudo_unico_mean = tudo_unico_mean.reset_index()
        tudo_unico_mean = tudo_unico_mean.sort_values(by=["price"])
        tudo_unico_mean[texto] = tudo_unico_mean[texto].astype(int)
        tudo_unico_mean[texto] = tudo_unico_mean[texto].astype(str)

        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'xy'}, {'type':'domain'}]], column_widths=[0.6, 0.4], subplot_titles=('Average Price of Listing per no. of ' + value, "Relative Frequency of " + value))

        fig.add_trace(go.Bar(x=tudo_unico_mean['price'], y=tudo_unico_mean[texto], orientation='h', text=tudo_unico_mean['price'], name="Price", marker_color=cores, showlegend=False), row=1, col=1)

        fig.update_traces(texttemplate='%{text:.2f}€', textposition='auto', hovertemplate='<b>%{y} ' + texto + ':</b> %{x:.2f}€<extra></extra>', hoverlabel_bgcolor="white", row=1, col=1)
        fig.update_xaxes(title_text='Price', row=1, col=1)
        fig.update_yaxes(title_text='Number of ' + texto, row=1, col=1)

        tudo_unico_count = tudo_unico.groupby(texto)["price"].count()
        tudo_unico_count = tudo_unico_count.reset_index()
        tudo_unico_count["count"] = tudo_unico_count["price"]
        tudo_unico_count[texto] = tudo_unico_count[texto].astype(int)
        tudo_unico_count = tudo_unico_count.sort_values(by=[texto])
        tudo_unico_count[texto] = tudo_unico_count[texto].astype(str)

        fig.add_trace(go.Pie(labels=tudo_unico_count[texto], values=tudo_unico_count['count'], name=texto, marker_colors=cores, sort=False), row=1, col=2)
        fig.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}: %{value}<br>(%{percent})', hovertemplate='<b>%{label}:</b> %{value}<br>(%{percent})<extra></extra>', hoverlabel_bgcolor="white", row=1, col=2)
        
        fig.update_layout(legend_y=0.5)

        return fig
    else:
        texto = value.lower()
        texto = texto.replace(" ", "_")

        tudo_unico_mean = tudo_unico.groupby("neighbourhood_cleansed").mean()
        tudo_unico_mean = tudo_unico_mean.reset_index()
        tudo_unico_mean = tudo_unico_mean.sort_values(by=[texto])

        fig = go.Figure(go.Bar(x=tudo_unico_mean[texto], y=tudo_unico_mean["neighbourhood_cleansed"], orientation='h', text=tudo_unico_mean[texto], marker_color=cores[0]))
        # fig.update_yaxis(type='category')
        fig.update_traces(texttemplate='%{text:.2f}€', textposition='auto', hovertemplate='<b>' + value + ' for %{y}:</b> %{x:.2f}€<extra></extra>', hoverlabel_bgcolor="white")
        fig.update_layout(title_text='Average Price of ' + value + ' per Neighbourhood', yaxis_title='Neighbourhood', xaxis_title='Price')
        return fig

@app.callback(
    [Output(component_id='date-picker', component_property='start_date'),
    Output(component_id='date-picker', component_property='end_date')],
    Input(component_id='button-reset', component_property='n_clicks')
)
def reset_dates(n_clicks):
    start_date = '2020-03-09'
    end_date = '2021-03-09'
    return start_date, end_date


app.layout = html.Div([
    dbc.Row([
        html.H2("Airbnb's of the region of Porto", style={'margin-top': '8px'}),
    ], align='center', justify='center', className="h-50"),
    html.Div(
        [
            dbc.Row(
                [
                    html.Div([
                        dbc.Row([
                            dbc.Col(dbc.Button('Log', id='button_log', style={'z-index': '1000'}, n_clicks_timestamp=0, color='secondary', outline=True, size='sm'), style={'bottom': '25px'}),
                            dbc.Col(dbc.Button('Lin', id='button_lin', style={'z-index': '1000'}, n_clicks_timestamp=0, color='secondary', outline=True, size='sm'), style={'bottom': '25px'})
                        ], align='center'),
                        dbc.Row([
                            dbc.Col(dcc.RangeSlider(id='price-slider-log', min=0, max=7, step=0.1, value=[0, 10], marks=marks_log, vertical=True, disabled=True, verticalHeight=420, allowCross=False), align='center', style={'bottom': '25px'}),
                            dbc.Col(dcc.RangeSlider(id='price-slider-lin', min=0, max=600, step=1, value=[0, 600], marks=marks_lin, vertical=True, disabled=True, verticalHeight=420, allowCross=False), align='center', style={'bottom': '25px'}),
                        ], align='center'),
                    ], style={'padding': '25px 25px 25px 0px', 'height': '420px', 'width': '140px', 'margin-top': '80px'}),
                    dbc.Col(dcc.Graph(id='mapa-limites', style={'height': '600px'}, config={'displayModeBar': False})),
                    dbc.Col(dcc.Graph(id='mapa-pontos', style={'height': '600px'}, config={'displayModeBar': False})),
                ], 
                style={'height': '550px'}
            ),
        ]
    ),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=date(2020, 3, 9),
                max_date_allowed=date(2021, 3, 9),
                start_date=date(2020, 3, 9),
                end_date=date(2021, 3, 9),
            ),
            dbc.Button('Reset Dates', id='button-reset', style={'z-index': '1000', 'margin': '5px'}, color='secondary', outline=True, size='sm'),
        ])
    ], align='center', justify='end'),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="linha", config={'displayModeBar': False}),
        ], style={'padding-right': '0px', 'padding-left': '0px', 'margin-right': '0px', 'right': '53px', 'width': '1250px'}),
    ], style={'width': '1250px'}),
    dcc.Dropdown(
        id='dropdown-pies',
        options=[
            {'label': x, 'value': x} for x in ["Accommodates", "Bathrooms", "Bedrooms", "Beds", "Security Deposit", "Cleaning Fee", "Extra People"]
        ],
        placeholder='Select feature to analyse',
        value="Accommodates"
    ),
    dcc.Graph(id="extra", style={'height': '1000px'}, config={'displayModeBar': False})
], className="container", id='teste')

if __name__ == '__main__':
    app.run_server(debug=False)