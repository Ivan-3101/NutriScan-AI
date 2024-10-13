import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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

def get_ai_recommendations(user_info, calorie_target):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    As a nutritionist, provide personalized diet recommendations for a person with the following profile:

    Age: {user_info['age']}
    Gender: {user_info['gender']}
    Weight: {user_info['weight']} kg
    Height: {user_info['height']} cm
    Activity Level: {user_info['activity_level']}
    Goal: {user_info['goal']}
    Daily Calorie Target: {calorie_target:.0f} calories
    Health Issues: {user_info['health_issues']}

    Please provide:
    1. A brief explanation of the diet strategy based on their goal and health issues.
    2. Recommended foods for Breakfast, Snack, Lunch, and Dinner, taking into account their health issues and goals.
    3. Any specific nutritional advice or considerations based on their health issues and goals.
    4. Two practical tips for maintaining this diet and working towards their goal.
    5. A sample one-day meal plan that fits their calorie target and aligns with their goals and health considerations.

    Format the response in Markdown for easy reading.
    """
    response = model.generate_content(prompt)
    return response.text

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
            
            ai_recommendation = get_ai_recommendations(user_info, calorie_target)

            st.subheader("Your Personalized AI Diet Recommendation")
            st.write(f"Estimated Daily Energy Expenditure: {tdee:.0f} calories")
            st.markdown(ai_recommendation)

        st.info("Note: While this AI-generated plan is personalized based on your input, it's always recommended to consult with a registered dietitian or healthcare provider for professional advice, especially if you have specific health concerns.")

if __name__ == "__main__":
    main()