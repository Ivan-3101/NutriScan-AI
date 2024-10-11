import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def assess_ingredient_safety(ingredient, quantity):
    prompt = f"""
    As a food safety and health expert, analyze the following ingredient and its quantity:

    Ingredient: {ingredient}
    Quantity: {quantity}

    Based on this information, please provide:
    1. Whether the quantity is safe for consumption.
    2. Potential health risks if this quantity is regularly consumed.
    3. Safe limits for this ingredient and recommended adjustments if needed.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def predict_health_risks(ingredients_with_quantities):
    analysis = []
    for ingredient, quantity in ingredients_with_quantities:
        safety_analysis = assess_ingredient_safety(ingredient, quantity)
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
        template='plotly_white'  # Add a clean template
    )
    return fig

def main():
    st.set_page_config(page_title="AI-Powered Food Safety Checker", layout="wide")

    # Add a title with better styling
    st.title("🌿 AI-Powered Food Safety and Ingredient Quantity Checker")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Main input area for food item and ingredients
    food_item = st.text_input("Enter the food item:")
    
    # Initialize session state for ingredients
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = []
        st.session_state.quantities = []

    # Ingredient input
    ingredient = st.text_input("Ingredient (e.g., sugar):")
    quantity = st.text_input("Quantity (grams):")  # Direct input for quantity

    # Add ingredient and quantity to the session state
    if st.button("Add Ingredient"):
        if ingredient and quantity:
            st.session_state.ingredients.append(ingredient)
            st.session_state.quantities.append(quantity + "g")  # Append 'g' to the quantity for display
            st.success(f"Added {ingredient}: {quantity}g")
        else:
            st.warning("Please enter both ingredient and quantity.")

    # Display added ingredients
    if st.session_state.ingredients:
        st.subheader("📝 Added Ingredients:")
        for ing, qty in zip(st.session_state.ingredients, st.session_state.quantities):
            st.write(f"- {ing}: {qty}")

    # Analyze all ingredients
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

    # Add a footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("Developed with ❤️ for food safety and health awareness.")

if __name__ == "__main__":
    main()
