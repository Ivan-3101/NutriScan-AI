import streamlit as st
import requests
import os
from dotenv import load_dotenv
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from charts import *

# Load environment variables
load_dotenv()

# Flask API URL
API_URL = os.getenv("FLASK_API_URL", "https://genai-api.onrender.com/predict_health_risks")

def call_flask_api(food_item, ingredients, consumption_frequency):
    """Call the Flask API to get health risk prediction."""
    payload = {
        "food_item": food_item,
        "ingredients": ingredients,
        "consumption_frequency": consumption_frequency
    }
    response = requests.post(API_URL, json=payload)
    
    if response.status_code == 200:
        return response.json().get('prediction')
    else:
        st.error("Error calling API: " + response.json().get('error', 'Unknown error occurred.'))
        return None

def main():
    st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px 24px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">Analyze your food for potential health risks and impacts.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        food_item = st.text_input("Enter the food item:", value="Pizza")

        ingredients_input = st.text_area("Enter the ingredients (one per line):", 
                                         value="Wheat flour\nTomato sauce\nCheese\nPepperoni\nOlive oil")
        ingredients = [ing.strip() for ing in ingredients_input.split('\n') if ing.strip()]

    with col2:
        consumption_frequency = st.selectbox(
            "How often is this food consumed?",
            ("Rarely", "Occasionally", "Regularly", "Frequently", "Daily")
        )

        st.write("") # Add some space
        st.write("") # Add some space
        analyze_button = st.button("Analyze Food Safety")

    if analyze_button:
        if food_item and ingredients:
            st.subheader("📊 Detailed Analysis Results")
            st.write("---")
            
            with st.spinner("Analyzing food safety and health risks..."):
                prediction = call_flask_api(food_item, ingredients, consumption_frequency)

            if prediction:
                # Extract risk score and health impacts
                risk_score = 100 - extract_risk_score(prediction)  # Adjusted for higher sentiment being lower risk
                health_impacts = extract_health_impacts(prediction)

                # Display graphs side by side
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(create_risk_gauge(risk_score), use_container_width=True)

                with col2:
                    if health_impacts:
                        st.plotly_chart(create_health_impact_radar(health_impacts), use_container_width=True)
                    else:
                        st.warning("No specific health impact ratings were found in the analysis.")

                # Display text analysis
                st.subheader("📊 Detailed Analysis Results")
                st.markdown("### 🚨 Health Risk Prediction:")
                st.markdown(prediction)

        else:
            st.warning("⚠️ Please enter both a food item and at least one ingredient.")

    st.sidebar.header("About this App")
    st.sidebar.info(
        "This AI-powered application analyzes food items and their ingredients "
        "to predict potential health risks and impacts. It considers the frequency "
        "of consumption to provide a more accurate assessment. Always consult with "
        "a healthcare professional for personalized medical advice."
    )
    st.sidebar.header("How to Use")
    st.sidebar.markdown(
        "1. Enter a food item\n"
        "2. List the ingredients\n"
        "3. Select consumption frequency\n"
        "4. Click 'Analyze Food Safety'\n"
        "5. Review the AI-generated health risk analysis and visualizations"
    )

if __name__ == "__main__":
    main()
