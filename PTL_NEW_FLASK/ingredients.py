import streamlit as st
import os
import requests
from dotenv import load_dotenv
import plotly.graph_objects as go

# Load environment variables
load_dotenv()
API_URL = os.getenv("FLASK_API_URL", "https://ingredients-api-idgp.onrender.com/assess_ingredient")  # Replace with actual API URL if different

def assess_ingredient_safety(ingredient, quantity):
    """Call the Flask API to get the ingredient safety analysis."""
    try:
        response = requests.post(
            API_URL,
            json={"ingredient": ingredient, "quantity": quantity}
        )
        if response.status_code == 200:
            return response.json().get('prediction', 'No prediction available')
        else:
            st.error("API call failed: " + response.json().get('error', 'Unknown error occurred'))
            return None
    except Exception as e:
        st.error(f"Error calling API: {e}")
        return None

def predict_health_risks(ingredients_with_quantities):
    analysis = []
    for ingredient, quantity in ingredients_with_quantities:
        safety_analysis = assess_ingredient_safety(ingredient, quantity)
        if safety_analysis:
            analysis.append({"ingredient": ingredient, "quantity": quantity, "analysis": safety_analysis})
    return analysis

def create_safety_chart(analysis):
    ingredients = [item['ingredient'] for item in analysis]
    safety_scores = [len(item['analysis'].split()) for item in analysis]  # Using word count as a proxy for safety score

    fig = go.Figure(data=[go.Bar(x=ingredients, y=safety_scores, marker_color='skyblue')])
    fig.update_layout(
        title="Ingredient Safety Analysis",
        xaxis_title="Ingredients",
        yaxis_title="Safety Score (word count)",
        height=400,
        xaxis_tickangle=-45,
        template='plotly_white'
    )
    return fig

def main():
    st.markdown("<hr>", unsafe_allow_html=True)
    food_item = st.text_input("Enter the food item:")

    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = []
        st.session_state.quantities = []

    ingredient = st.text_input("Ingredient (e.g., sugar):")
    quantity = st.text_input("Quantity (grams):")  # Direct input for quantity

    if st.button("Add Ingredient"):
        if ingredient and quantity:
            st.session_state.ingredients.append(ingredient)
            st.session_state.quantities.append(quantity + "g")  # Append 'g' to the quantity for display
            st.success(f"Added {ingredient}: {quantity}g")
        else:
            st.warning("Please enter both ingredient and quantity.")

    if st.session_state.ingredients:
        st.subheader("📝 Added Ingredients:")
        for ing, qty in zip(st.session_state.ingredients, st.session_state.quantities):
            st.write(f"- {ing}: {qty}")

    if st.button("Analyze All"):
        if food_item and st.session_state.ingredients:
            ingredients_with_quantities = list(zip(st.session_state.ingredients, st.session_state.quantities))
            st.info("Analyzing ingredient quantities and health impacts...")
            analysis = predict_health_risks(ingredients_with_quantities)

            st.subheader("🔍 Health and Safety Assessment:")
            for item in analysis:
                with st.expander(f"{item['ingredient']} ({item['quantity']})"):
                    st.write(item['analysis'])

            st.subheader("📊 Safety Analysis Chart")
            safety_chart = create_safety_chart(analysis)
            st.plotly_chart(safety_chart, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("Developed with ❤️ for food safety and health awareness.")

if __name__ == "__main__":
    main()
