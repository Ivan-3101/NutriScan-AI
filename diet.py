import streamlit as st
import pandas as pd
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Flask API URL from environment variable or default
API_URL = os.getenv("FLASK_API_URL", "https://diet-api-uffi.onrender.com/diet_recommendations")

def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_tdee(bmr, activity_level):
    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9
    }
    return bmr * activity_multipliers[activity_level]

def call_flask_api(user_info, calorie_target):
    payload = {
        "user_info": user_info,
        "calorie_target": calorie_target
    }
    response = requests.post(API_URL, json=payload)
    
    if response.status_code == 200:
        return response.json().get('recommendations')
    else:
        st.error("Error calling API: " + response.json().get('error', 'Unknown error occurred.'))
        return None

def main():
    st.write("Enter your details below to get a personalized diet recommendation.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        weight = st.number_input("Weight (kg)", min_value=40.0, max_value=200.0, value=70.0)
        height = st.number_input("Height (cm)", min_value=140.0, max_value=220.0, value=170.0)
    
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity_level = st.selectbox("Activity Level", [
            "Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"
        ])

    goal = st.text_area("What are your specific health and fitness goals?", 
                        "e.g., Lose 10kg, Build muscle, Improve energy levels, Manage diabetes")
    
    health_issues = st.text_area("Do you have any health issues or dietary restrictions?", 
                                 "e.g., Diabetes, Gluten intolerance, Vegetarian, High blood pressure")
    
    if st.button("Generate AI Diet Recommendation"):
        with st.spinner("Generating your personalized diet plan..."):
            bmr = calculate_bmr(weight, height, age, gender)
            tdee = calculate_tdee(bmr, activity_level)
            calorie_target = tdee  # Adjusting calorie target based on goals will be handled by the AI
            
            user_info = {
                "age": age,
                "gender": gender,
                "weight": weight,
                "height": height,
                "activity_level": activity_level,
                "goal": goal,
                "health_issues": health_issues
            }
            
            ai_recommendation = call_flask_api(user_info, calorie_target)

            if ai_recommendation:
                st.subheader("Your Personalized AI Diet Recommendation")
                st.write(f"Estimated Daily Energy Expenditure: {tdee:.0f} calories")
                st.markdown(ai_recommendation)

        st.info("Note: While this AI-generated plan is personalized based on your input, it's always recommended to consult with a registered dietitian or healthcare provider for professional advice, especially if you have specific health concerns.")

if __name__ == "__main__":
    main()
