import plotly.express as px
import streamlit as st
import pandas as pd

df = pd.read_csv("coucou.csv")

st.title("Event explorer")
show_organisers = st.sidebar.checkbox("Show organisers")
text_filter = st.sidebar.text_input("Filter events based on title")


filtered = df[df.title.str.contains(text_filter, case=False)]
st.text(
    f"There are {len(filtered)} events with the word '{text_filter}' in their title"
)

args = {}
if show_organisers:
    args["color"] = "organiser"
graph = px.histogram(filtered, x="start_date", **args)
graph


filtered
