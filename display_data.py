import streamlit as st
import pandas as pd

st.markdown("<h1 style='text-align: center;'>Environmental Dashboard</h1>", unsafe_allow_html=True)

data = pd.read_csv("data.csv").tail(1)

Temperature = int(data['Temperature (F)'].iloc[0])
Pressure = int(data['Pressure (hPa)'].iloc[0])
Humidity = int(data['Humidity (%)'].iloc[0])
Gas = int(data['Gas (KOhms)'].iloc[0])
Altitude = int(data['Altitude (ft)'].iloc[0])

spacer1, col1, col2, col3, spacer2 = st.columns([1, 2, 2, 2, 1]) # Create columns for the metrics with spacers on the sides for better layout
with col1:
    st.metric(label="Temperature (F)", value=str(Temperature) + " °F")
with col2:
    st.metric(label="Pressure (hPa)", value=str(Pressure) + " hPa")
with col3:
    st.metric(label="Humidity (%)", value=str(Humidity) + " %")

spacer3, col4, col5, spacer4 = st.columns([1, 2, 2, 1]) # Create columns for the metrics with spacers on the sides for better layout
with col4:
    st.metric(label="Gas (KOhms)", value=str(Gas) + " KOhms")
with col5:
    st.metric(label="Altitude (ft)", value=str(Altitude) + " ft")