import plotly.express as px
import streamlit as st
import pandas as pd


st.title("Events explorer")

text_filter = st.sidebar.text_input("Filter...")
show_colors = st.sidebar.checkbox("Show colors")


df = pd.read_csv("events.csv")
filtered_df = df[df.title.str.contains(text_filter, case=False)]

st.text(f"There are {len(filtered_df)} events containing '{text_filter}'")

args = {}
if show_colors:
    args["color"] = "organiser"
graph = px.histogram(
    filtered_df, x="start_datetime", title="C'était mieux avant", **args
)
graph

filtered_df
