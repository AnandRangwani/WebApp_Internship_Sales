import folium
from streamlit_folium import st_folium, folium_static
from branca.element import Figure
from geopy.geocoders import Nominatim
import streamlit as st
import datetime,requests
from plotly import graph_objects as go
import pandas as pd

weakness=pd.read_excel("Weakness.xlsx") # Please use Caching here to read the excel file to avoid reading file everytime on rerunning.

st.sidebar.header("FINDING POTENTIAL MARKETS")

with st.sidebar.expander("Competitor's Analysis"):

    competitor=st.radio(label="Select The Competitor", options=["Maaza", "Frooti", "Real Koolerz", "Swing PaperBoat", "Appy","Slice"])
    
    if competitor=="Maaza":
        df=weakness[["Maaza","Maaza_DTM"]].dropna()

    elif competitor=="Frooti":
        df=weakness[["Frooti","Frooti_DTM"]].dropna()
    
    elif competitor=="Swing PaperBoat":
        df=weakness[["Swing","Swing_DTM"]].dropna()
        competitor="Swing"

    elif competitor=="Real Koolerz":
        df=weakness[["Koolerz","Koolerz_DTM"]].dropna()
        competitor="Koolerz"
    
    elif competitor=="Appy":
        df=weakness[["Appy","Appy_DTM"]].dropna()
    
    elif competitor=="Slice":
        df=weakness[["Slice","Slice_DTM"]].dropna()
    

spot_weakness_button=st.sidebar.checkbox("Spot Weak Loactions")

fig2=Figure(width=550,height=350)


geolocator = Nominatim(user_agent="MyApp")


@st.cache_resource
def create_map(competitor):

    m2=folium.Map(location=[23.2599, 77.4126],zoom_start=6,min_zoom=2,max_zoom=8)


    for market in df.iloc[:,0].values:

        if market=="Surat":  # Because 'geolocator' is not giving correct coordintes of "Surat".
            market_="Surat, Gujarat"
        else:
            market_=market

        location = geolocator.geocode(market_)

        folium.Marker(location=[location.latitude, location.longitude],popup=f"Nearest Factory {df.loc[df[competitor]==market,competitor+'_DTM'].values[0]} Km",tooltip=market).add_to(m2)

    folium.TileLayer('Stamen Toner').add_to(m2)

    return m2

    

if spot_weakness_button:
    map_obj=create_map(competitor)
    objs=st_folium(map_obj, width=725, returned_objects=['last_object_clicked_tooltip'])

else:
    objs=dict()
    objs["last_object_clicked_tooltip"]=None




########################################################################################################################################




city_name_map=objs["last_object_clicked_tooltip"]
map_button=st.button(f"GET TEMPERATURE FORECAST OF {city_name_map}")
city_name_input=st.text_input("Enter City Name to Get Temperature Forecast")

show_temp=False
if map_button and city_name_map is not None:
    city=city_name_map
    show_temp=True
elif len(city_name_input)>0:
    city=city_name_input
    show_temp=True
else:
    show_temp=False
    city="Delhi"



temp_unit=" °C"

api="9b833c0ea6426b70902aa7a4b1da285c"

    
if show_temp==True:

    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}"
    response=requests.get(url)
    x=response.json()

    st.header(f"{city} Temperature Forecast")
    try:
        lon=x["coord"]["lon"]
        lat=x["coord"]["lat"]
        ex="current,minutely,hourly"
        url2=f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={ex}&appid={api}'
        res=requests.get(url2)
        y=res.json()

        maxtemp=[]
        mintemp=[]
        humd=[]
        desc=[]
        cloud=[]
        rain=[]
        dates=[]

        cel=273.15
        
        for item in y["daily"]:
            
            maxtemp.append(round(item["temp"]["max"]-cel,2))
            mintemp.append(round(item["temp"]["min"]-cel,2))
            
            humd.append(str(item["humidity"])+' %')
            
            cloud.append(str(item["clouds"])+' %')
            rain.append(str(int(item["pop"]*100))+'%')

            desc.append(item["weather"][0]["description"].title())

            d1=datetime.date.fromtimestamp(item["dt"])
            dates.append(d1.strftime('%d %b'))
            
        
        def linegraph():
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=mintemp, name='Minimum '))
            fig.add_trace(go.Scatter(x=dates, y=maxtemp, name='Maximimum ',marker_color='crimson'))
            fig.update_layout(xaxis_title="Dates",yaxis_title="Temperature",font=dict(color="white"))
            st.plotly_chart(fig)
            
        icon=x["weather"][0]["icon"]
        current_weather=x["weather"][0]["description"].title()
        
        temp=str(round(x["main"]["temp"]-cel,2))
        
        
        col1, col2= st.columns(2)
        col1.metric("CURRENT TEMPERATURE",temp+temp_unit)
        col2.metric("WEATHER",current_weather)
        st.subheader(" ")
        
        linegraph()

        table1=go.Figure(data=[go.Table(header=dict(
                  values = [
                  '<b>DATES</b>',
                  '<b>MAX TEMP<br>(in'+temp_unit+')</b>',
                  '<b>MIN TEMP<br>(in'+temp_unit+')</b>',
                  '<b>CHANCES OF RAIN</b>',
                  '<b>CLOUD COVERAGE</b>',
                  '<b>HUMIDITY</b>'],
                  line_color='black', fill_color='royalblue',  font=dict(color='white', size=14),height=32),
        cells=dict(values=[dates,maxtemp,mintemp,rain,cloud,humd],
        line_color='black',fill_color=['paleturquoise',['palegreen', '#fdbe72']*7], font_size=14,height=32
            ))])

        table1.update_layout(margin=dict(l=10,r=10,b=10,t=10),height=328)
        st.write(table1)
        
 
    except KeyError:
        st.error(" Invalid city!!  Please try again !!")



