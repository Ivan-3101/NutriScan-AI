import streamlit as st
import requests
import json
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import re

# Configuration
OCR_API_KEY = "K82784981688957"
GEMINI_API_KEY = "AIzaSyBqjWUIbvOOMErYs_o5V3T4Z0f4Od6jeyY"

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Custom CSS to improve the app's appearance
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; }
    .stImage { margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

def ocr_space_file(uploaded_file, api_key=OCR_API_KEY, language='eng'):
    """Extract text from image using OCR.space API."""
    url = 'https://api.ocr.space/parse/image'
    payload = {'apikey': api_key, 'language': language, 'isOverlayRequired': False}
    
    if uploaded_file.size == 0:
        st.error("The uploaded file is empty. Please try uploading the file again.")
        return None
    
    try:
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(url, files=files, data=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            st.error(f"OCR Error: {result.get('ErrorMessage', 'Unknown error')}")
            return None
        
        parsed_results = result.get('ParsedResults', [])
        if not parsed_results:
            st.warning("No text was extracted from the image.")
            return None
        
        return parsed_results[0].get('ParsedText')
    
    except requests.exceptions.RequestException as e:
        st.error(f"Request Error: {str(e)}")
    except json.JSONDecodeError as e:
        st.error(f"JSON Decode Error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
    
    return None

def analyze_ingredients(ingredients):
    """Analyze ingredients using Gemini API and return analysis and ingredient counts."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    Analyze the following list of ingredients:
    {ingredients}
    
    Provide information on:
    1. Safety for consumption
    2. Health benefits or concerns
    3. Potential allergens
    4. Nutritional value
    5. Any other relevant details
    
    Also, categorize each ingredient as either 'healthy' or 'potentially concerning'.
    At the end, provide a count of healthy ingredients and potentially concerning ingredients in the format:
    HEALTHY_COUNT: X
    CONCERNING_COUNT: Y
    """
    response = model.generate_content(prompt)
    analysis = response.text
    
    # Extract counts from the analysis
    healthy_count = 0
    concerning_count = 0
    
    # Use regex to find the counts
    healthy_match = re.search(r'HEALTHY_COUNT:\s*(\d+)', analysis)
    concerning_match = re.search(r'CONCERNING_COUNT:\s*(\d+)', analysis)
    
    if healthy_match:
        healthy_count = int(healthy_match.group(1))
    if concerning_match:
        concerning_count = int(concerning_match.group(1))
    
    # If no counts are found, estimate based on the analysis
    if healthy_count == 0 and concerning_count == 0:
        healthy_count = analysis.lower().count('healthy')
        concerning_count = analysis.lower().count('concerning')
    
    # Ensure at least one count is non-zero
    if healthy_count == 0 and concerning_count == 0:
        healthy_count = 1
    
    return analysis, healthy_count, concerning_count

def create_pie_chart(healthy_count, concerning_count):
    """Create a pie chart of healthy vs. potentially concerning ingredients."""
    labels = 'Healthy', 'Potentially Concerning'
    sizes = [healthy_count, concerning_count]
    colors = ['#66b3ff', '#ff9999']
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    
    return fig

def main():
    st.write("Upload an image of ingredients to analyze their health impact and safety.")
    
    uploaded_file = st.file_uploader("Choose an image of ingredients", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
            except Exception as e:
                st.error(f"Error opening image: {str(e)}")
        
        with col2:
            if st.button("🔍 Analyze Ingredients", key="analyze_button"):
                with st.spinner("Extracting text from image..."):
                    ingredients_text = ocr_space_file(uploaded_file)
                
                if ingredients_text:
                    st.subheader("📋 Extracted Ingredients:")
                    st.write(ingredients_text)
                    
                    with st.spinner("Analyzing ingredients..."):
                        analysis, healthy_count, concerning_count = analyze_ingredients(ingredients_text)
                    st.subheader("🧪 Ingredient Analysis:")
                    st.write(analysis)
                    
                    st.subheader("📊 Ingredient Health Proportion:")
                    st.write(f"Healthy Ingredients: {healthy_count}")
                    st.write(f"Potentially Concerning Ingredients: {concerning_count}")
                    
                    pie_chart = create_pie_chart(healthy_count, concerning_count)
                    st.pyplot(pie_chart)
                else:
                    st.error("Failed to extract text from the image. Please try again with a clearer image.")

if __name__ == "__main__":
    main()