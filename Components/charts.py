import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
from textblob import TextBlob
import plotly.graph_objs as go
import pandas as pd
def create_risk_gauge(risk_score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Overall Health Risk"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkred"},
            'steps' : [
                {'range': [0, 33], 'color': "lightgreen"},
                {'range': [33, 66], 'color': "yellow"},
                {'range': [66, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': risk_score
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def extract_risk_score(text):
    blob = TextBlob(text)
    return min(max((blob.sentiment.polarity + 1) / 2 * 100, 0), 100)


def create_health_impact_radar(impacts):
    categories = list(impacts.keys())
    values = list(impacts.values())
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Health Impacts'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        title="Health Impact Assessment"
    )
    
    return fig

def extract_health_impacts(text):
    impact_pattern = r'(\w+(?:\s+\w+)*)\s*:\s*(\d+)'
    impacts = re.findall(impact_pattern, text)
    return {aspect: int(score) for aspect, score in impacts if int(score) <= 10}