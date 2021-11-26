import pandas as pd
import numpy as np
import geopandas as gpd
import geojson
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date
from plotly.subplots import make_subplots

# https://coolors.co/cf777e-69140e-a44200-d58936-fff94f

# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


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
    calendar_columns = ["listing_id", "date", "available", "price", "adjusted_price", "minimum_nights", "maximum_nights"]
    listings_columns = ["id",
                    "listing_url",
                    "scrape_id",
                    "last_scraped",
                    "name",
                    "summary",
                    "space",
                    "description",
                    "experiences_offered",
                    "neighborhood_overview",
                    "notes",
                    "transit",
                    "access",
                    "interaction",
                    "house_rules",
                    "thumbnail_url",
                    "medium_url",
                    "picture_url",
                    "xl_picture_url",
                    "host_id",
                    "host_url",
                    "host_name",
                    "host_since",
                    "host_location",
                    "host_about",
                    "host_response_time",
                    "host_response_rate",
                    "host_acceptance_rate",
                    "host_is_superhost",
                    "host_thumbnail_url",
                    "host_picture_url",
                    "host_neighbourhood",
                    "host_listings_count",
                    "host_total_listings_count",
                    "host_verifications",
                    "host_has_profile_pic",
                    "host_identity_verified",
                    "street",
                    "neighbourhood",
                    "neighbourhood_cleansed",
                    "neighbourhood_group_cleansed",
                    "city",
                    "state",
                    "zipcode",
                    "market",
                    "smart_location",
                    "country_code",
                    "country",
                    "latitude",
                    "longitude",
                    "is_location_exact",
                    "property_type",
                    "room_type",
                    "accommodates",
                    "bathrooms",
                    "bedrooms",
                    "beds",
                    "bed_type",
                    "amenities",
                    "square_feet",
                    "price",
                    "weekly_price",
                    "monthly_price",
                    "security_deposit",
                    "cleaning_fee",
                    "guests_included",
                    "extra_people",
                    "minimum_nights",
                    "maximum_nights",
                    "minimum_minimum_nights",
                    "maximum_minimum_nights",
                    "minimum_maximum_nights",
                    "maximum_maximum_nights",
                    "minimum_nights_avg_ntm",
                    "maximum_nights_avg_ntm",
                    "calendar_updated",
                    "has_availability",
                    "availability_30",
                    "availability_60",
                    "availability_90",
                    "availability_365",
                    "calendar_last_scraped",
                    "number_of_reviews",
                    "number_of_reviews_ltm",
                    "first_review",
                    "last_review",
                    "review_scores_rating",
                    "review_scores_accuracy",
                    "review_scores_cleanliness",
                    "review_scores_checkin",
                    "review_scores_communication",
                    "review_scores_location",
                    "review_scores_value",
                    "requires_license",
                    "license",
                    "jurisdiction_names",
                    "instant_bookable",
                    "is_business_travel_ready",
                    "cancellation_policy",
                    "require_guest_profile_picture",
                    "require_guest_phone_verification",
                    "calculated_host_listings_count",
                    "calculated_host_listings_count_entire_homes",
                    "calculated_host_listings_count_private_rooms",
                    "calculated_host_listings_count_shared_rooms",
                    "reviews_per_month"
    ]
    save = [
        "id",
        "neighbourhood_cleansed",
        "neighbourhood_group_cleansed",
        "latitude",
        "longitude",
        "accommodates",
        "bathrooms",
        "bedrooms",
        "beds",
        "security_deposit",
        "cleaning_fee",
        "extra_people",
        "guests_included"
    ]
    dates = ["27-2", "21-3", "23-4", "28-5", "23-6", "25-7", "27-8", "19-9", "21-10", "8-11", "19-12", "16-1", "13-2"] # 13
    intervals = {
        dates[0]: ["2020-03-09", "2020-03-20"],
        dates[1]: ["2020-03-21", "2020-04-22"],
        dates[2]: ["2020-04-23", "2020-05-27"],
        dates[3]: ["2020-05-28", "2020-06-22"],
        dates[4]: ["2020-06-23", "2020-07-24"],
        dates[5]: ["2020-07-25", "2020-08-26"],
        dates[6]: ["2020-08-27", "2020-09-18"],
        dates[7]: ["2020-09-19", "2020-10-20"],
        dates[8]: ["2020-10-21", "2020-11-07"],
        dates[9]: ["2020-11-08", "2020-12-18"],
        dates[10]: ["2020-12-19", "2021-01-15"],
        dates[11]: ["2021-01-16", "2021-02-12"],
        dates[12]: ["2021-02-13", "2021-03-09"]
    }

    try:
        print("--------------------------------\nReading: all_data.csv")
        tudo = pd.read_csv("all_data.csv")
    except:
        try:
            print("Reading: all_calendar.csv")
            calendar = pd.read_csv("data/calendar/all_calendar.csv")
            print("Reading: all_listings.csv")
            listings = pd.read_csv("data/listings/all_listings.csv")
            
            print("About to merge calendar & listings data")
            tudo = pd.merge(calendar, listings, on="listing_id")
            print("Going to write the merged data to a file")
            tudo.to_csv("all_data.csv", index=False)
            print("Done! :)")
        except:
            calendar = pd.DataFrame(columns=calendar_columns)
            listings = pd.DataFrame(columns=save)
            
            for i in range(len(dates)):
                file_path_calendars = "data/calendar/(" + str(i + 1) + ") calendar_" + dates[i] + ".csv/calendar.csv"
                df_cal = pd.read_csv(file_path_calendars)
                df_cal = df_cal[df_cal["date"] >= intervals[dates[i]][0]]
                df_cal = df_cal[df_cal["date"] <= intervals[dates[i]][1]]
                calendar = pd.concat([calendar, df_cal], ignore_index=True)
                print("Done reading:", file_path_calendars)
                
                file_path_listings = "data/listings/(" + str(i + 1) + ") listings_" + dates[i] + ".csv/listings.csv"
                df_lis = pd.read_csv(file_path_listings)
                df_lis.drop(df_lis.columns.difference(save), 1, inplace=True)
                listings = pd.concat([listings, df_lis], ignore_index=True)
                print("Done reading:", file_path_listings, end="\n-----------------------------------------\n")
            
            print("Last touches on calendar & listings")
            
            corrige_int(listings, "accommodates")
            corrige_nan(listings, "bathrooms")
            corrige_nan(listings, "bedrooms")
            corrige_nan(listings, "beds")
            corrige_precos(listings, "security_deposit")
            corrige_precos(listings, "cleaning_fee")
            corrige_precos(listings, "guests_included")
            corrige_precos(listings, "extra_people")
            
            final_aux = []
            a = listings["id"].unique()
            for i in range(len(a)):
                print(i)
                final_aux.append(listings[listings["id"] == a[i]].iloc[0].T)

            final_listings = pd.DataFrame(final_aux, columns=save)
            ajuda_2 = final_listings["id"]
            final_listings = final_listings.drop(columns=["id"])
            final_listings["listing_id"] = ajuda_2
            
            corrige_precos(calendar, "price")
            corrige_nan(calendar, "minimum_nights")
            corrige_nan(calendar, "maximum_nights")
            corrige_precos(calendar, "adjusted_price")
            corrige_datas(calendar, "date")

            print("About to write calendar data to a file")
            calendar.to_csv("data/calendar/all_calendar.csv", index=False)
            print("About to write listings data to a file")
            final_listings.to_csv("data/listings/all_listings.csv", index=False)
            print("Done! :)")
            
            print("About to merge calendar & listings data")
            tudo = pd.merge(calendar, final_listings, on="listing_id")
            print("Going to write the merged data to a file")
            tudo.to_csv("all_data.csv", index=False)
            print("Done! :)")

    # available --> {"t": True, "f": False}

    print("Reading neighbourhoods file")
    neighbourhoods = pd.read_csv("neighbourhoods.csv")

    print("Reading neighbourhoods.geojson file")
    file = open("neighbourhoods.geojson", encoding='utf-8')
    geojson_airbnb = geojson.load(file)
    file.close()

    print("Reading all_data_unique file")
    tudo_unico = pd.read_csv("all_data_unique.csv")

    return tudo, neighbourhoods, geojson_airbnb, tudo_unico

tudo, neighbourhoods, geojson_airbnb, tudo_unico = read_data()

app = dash.Dash(__name__)


@app.callback(
    Output(component_id='mapa-limites', component_property='figure'),
    Input(component_id='price-slider', component_property='value')
)
def grafico_mapa_limites(value):
    print(f"> Range price: [{value[0]}, {value[1]}]")
    aux = tudo.groupby(["neighbourhood_cleansed"]).mean()
    aux = aux.reset_index()

    fig_map = px.choropleth_mapbox(
        aux[aux['price'].between(value[0], value[1])],
        color="price",
        geojson=geojson_airbnb,
        featureidkey="properties.neighbourhood",
        locations="neighbourhood_cleansed",
        center={'lat': 41.1, 'lon': -8.628613},
        mapbox_style="carto-positron",
        zoom=7,
        title='Average Price of Neighbourhoods'
    )
    return fig_map


@app.callback(
    Output(component_id='mapa-pontos', component_property='figure'),
    Input(component_id='price-slider', component_property='value')
)
def grafico_mapa_pontos(value):
    casas = tudo.groupby("listing_id")[["price", "latitude", "longitude"]].mean()
    casas = casas.reset_index()

    fig_map_pontos = px.scatter_mapbox(
        casas[casas['price'].between(value[0], value[1])],
        color='price',
        lat="latitude",
        lon="longitude",
        hover_name="listing_id",
        center={'lat': 41.1, 'lon': -8.628613},
        zoom=7,
        mapbox_style="carto-positron",
        title='Average Price of Listings'
    )
    return fig_map_pontos


@app.callback(
    Output(component_id='linha', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='date-picker', component_property='start_date'),
    Input(component_id='date-picker', component_property='end_date')]
)
def grafico_linha(value, start_date, end_date):
    print("> Dropdown:", value)
    print("> Start date:", start_date)
    print("> End date:", end_date)

    skrt = tudo.groupby("date")["price"].mean()  # Sacar média diaria de todas as casas
    skrt = skrt.reset_index()

    x = skrt[(skrt["date"] <= end_date) & (skrt["date"] >= start_date)]["date"]

    if value is not None:
        fig = make_subplots(rows=2, cols=1)
        poasd = tudo[tudo["listing_id"] == value]  # Sacar id

        spot = poasd.iloc[0]["neighbourhood_cleansed"]  # Sacar o neighbourhood

        tyu = tudo.groupby(["date", "neighbourhood_cleansed"])[["price"]].mean()  # Juntar por data e neighbourhood e ver a média
        tyu = tyu.reset_index()
        # display(tyu[tyu["neighbourhood_cleansed"] == spot]["price"])  # Ver apenas pelo neighbourhood e preço
    
        fig.add_trace(go.Scatter(x=x, y=skrt["price"], mode='lines', name='Average yearly'), row=1, col=1)
        fig.add_trace(go.Scatter(x=x, y=tyu[tyu["neighbourhood_cleansed"] == spot]["price"], mode='lines', name='Average district ' + spot), row=1, col=1)
        fig.add_trace(go.Scatter(x=x, y=poasd["price"], mode='lines', name="Airbnb no. " + str(value)), row=1, col=1)

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

        # fig.add_trace(go.Bar(x=x, y=std["price"], name="Difference between average yearly and neighbourhood"), row=2, col=1)
        fig.add_trace(go.Scatter(x=x, y=std["price"], mode='lines', name="Difference between average yearly and neighbourhood"), row=2, col=1)

        fig.update_layout(
            title="Average Prices",
            showlegend=True,
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
            }
        )
    else:
        fig = go.Figure()
        # print("nao adicionei nada amigo")
        fig.add_trace(go.Scatter(x=x, y=skrt["price"], mode='lines', name='Average yearly'))

        fig.update_layout(
            title="Average Prices",
            showlegend=True,
            xaxis={
                'title': 'Date',
                'fixedrange': True
            },
            yaxis={
                'title': 'Price',
                'fixedrange': True
            }
        )

    return fig


@app.callback(
    Output(component_id='extra', component_property='figure'),
    Input(component_id='dropdown-pies', component_property='value')
)
def grafico_bar(value):
    print("> Bar chart:", value)
    if value == "Accommodates" or value == "Bathrooms" or value == "Bedrooms" or value == "Beds":
        texto = value.lower()

        tudo_unico_mean = tudo_unico.groupby(texto).mean()
        tudo_unico_mean = tudo_unico_mean.reset_index()
        tudo_unico_mean = tudo_unico_mean.sort_values(by=["price"])

        fig = make_subplots(rows=2, cols=1, specs=[[{'type':'xy'}], [{'type':'domain'}]])
        fig.add_trace(go.Bar(x=tudo_unico_mean['price'], y=tudo_unico_mean[texto], orientation='h', text=tudo_unico_mean['price'], name="Price"), row=1, col=1)
        fig.update_yaxes(type='category')
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(title_text='Average Price per no. of ' + texto, yaxis_title='Number of ' + texto, xaxis_title='Price')

        tudo_unico_count = tudo_unico.groupby(texto)["price"].count()
        tudo_unico_count = tudo_unico_count.reset_index()
        tudo_unico_count["count"] = tudo_unico_count["price"]

        # fig.add_trace(px.pie(tudo_unico_count, values='count', names=texto, title='Relative Frequency of ' + texto), row=2, col=1)
        fig.add_trace(go.Pie(labels=tudo_unico_count[texto], values=tudo_unico_count['count'], name=texto), row=2, col=1)
        fig.update_traces(textposition='inside', textinfo='percent+label', title="Relative Frequency of " + texto, row=2, col=1)
        return fig
    else:
        texto = value.lower()
        texto = texto.replace(" ", "_")

        tudo_unico_mean = tudo_unico.groupby("neighbourhood_cleansed").mean()
        tudo_unico_mean = tudo_unico_mean.reset_index()
        tudo_unico_mean = tudo_unico_mean.sort_values(by=[texto])

        fig = go.Figure(go.Bar(x=tudo_unico_mean[texto], y=tudo_unico_mean["neighbourhood_cleansed"], orientation='h', text=tudo_unico_mean[texto]))
        fig.update_yaxes(type='category')
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(title_text='Average Price of ' + value + ' per Neighbourhood', yaxis_title='Neighbourhood', xaxis_title='Price')
        return fig

'''@app.callback(
    Output(component_id='circular2', component_property='figure'),
    Input(component_id='dropdown-pies', component_property='value')
)
def grafico_pie2(value):
    if value == "Accommodates" or value == "Bathrooms" or value == "Bedrooms" or value == "Beds":
        texto = value.lower()

        tudo_unico_count = tudo_unico.groupby(texto)["price"].count()
        tudo_unico_count = tudo_unico_count.reset_index()
        tudo_unico_count["count"] = tudo_unico_count["price"]

        fig_2 = px.pie(tudo_unico_count, values='count', names=texto, title='Relative Frequency of ' + texto)
        fig_2.update_traces(textposition='inside', textinfo='percent+label')
        return fig_2
    else:
        return go.Figure()'''

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
    dcc.Graph(id='mapa-limites'),
    dcc.RangeSlider(
        id='price-slider',
        min=0,
        max=20331,
        step=0.5,
        value=[0, 20331],
        marks={
            0: '0€',
            250: '250€',
            500: '500€',
            1000: '1000€',
            2500: '2500€',
            5000: '5000€',
            10000: '10000€',
            20331: '20331€',
        }
    ),
    dcc.Graph(id='mapa-pontos'),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': x, 'value': x} for x in np.sort(tudo_unico["listing_id"])
        ],
        placeholder='Select listing ID'
    ),
    dcc.Graph(id="linha"),
    dcc.DatePickerRange(
        id='date-picker',
        min_date_allowed=date(2020, 3, 9),
        max_date_allowed=date(2021, 3, 9),
        start_date=date(2020, 3, 9),
        end_date=date(2021, 3, 9),
    ),
    html.Button('Reset Dates', id='button-reset'),
    dcc.Dropdown(
        id='dropdown-pies',
        options=[
            {'label': x, 'value': x} for x in ["Accommodates", "Bathrooms", "Bedrooms", "Beds", "Security Deposit", "Cleaning Fee", "Extra People", "Guests Included"]
        ],
        placeholder='Select feature to analyse',
        value="Accommodates"
    ),
    dcc.Graph(id="extra")
])

if __name__ == '__main__':
    app.run_server(debug=True)