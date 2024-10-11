import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
from textblob import TextBlob
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from PTL.Components.charts import *

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def predict_health_risks(food_item, ingredients, consumption_frequency):
    prompt = f"""
    As a food safety and health expert, analyze the following food item and its ingredients:

    Food Item: {food_item}
    Ingredients: {', '.join(ingredients)}
    Consumption Frequency: {consumption_frequency}

    Based on this information, please provide:
    1. Potential health risks associated with consuming this food item, especially if consumed in unhealthy amounts.
    3. Any concerning ingredients and their specific health impacts.
    4. How the consumption frequency might affect the likelihood or severity of these health risks.
    5. Rate the impact (0-10 scale) of this food on the following health aspects:
       - Cardiovascular health: [score]
       - Blood sugar levels: [score]
       - Weight management: [score]
       - Digestive health: [score]
       - Nutrient balance: [score]
    6. Most likely diseases
    Present your analysis in a structured, easy-to-read format with bullet points or numbered lists where appropriate.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def extract_health_impacts(text):
    impact_pattern = r'(\w+(?:\s+\w+)*)\s*:\s*(\d+)'
    impacts = re.findall(impact_pattern, text)
    return {aspect: int(score) for aspect, score in impacts if int(score) <= 10}


def main():
    st.set_page_config(page_title="Food Safety Analyzer", page_icon="🍽️", layout="wide")

    st.title("🍽️ AI-Powered Food Safety and Health Risk Predictor")

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
                prediction = predict_health_risks(food_item, ingredients, consumption_frequency)
            
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