import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image
import io
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import requests
from PIL import Image
from io import BytesIO
import zipfile

# Load environment variables
load_dotenv()

# Function to unzip and load the model
@st.cache_resource
def load_model():
    zip_file = 'food101_mobilenetv2.zip'
    model_dir = 'food101_mobilenetv2'
    
    # Unzip the file if it's not already extracted
    if not os.path.exists(model_dir):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(model_dir)
    
    model_path = os.path.join(model_dir, 'food101_mobilenetv2.h5')  # Adjust the path if necessary
    return tf.keras.models.load_model(model_path)

model = load_model()

# List of Food-101 classes
food_classes = [
    'apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare',
    'beet_salad', 'beignets', 'bibimbap', 'bread_pudding', 'breakfast_burrito',
    'bruschetta', 'caesar_salad', 'cannoli', 'caprese_salad', 'carrot_cake',
    'ceviche', 'cheesecake', 'cheese_plate', 'chicken_curry', 'chicken_quesadilla',
    'chicken_wings', 'chocolate_cake', 'chocolate_mousse', 'churros', 'clam_chowder',
    'club_sandwich', 'crab_cakes', 'creme_brulee', 'croque_madame', 'cup_cakes',
    'deviled_eggs', 'donuts', 'dumplings', 'edamame', 'eggs_benedict', 'escargots',
    'falafel', 'filet_mignon', 'fish_and_chips', 'foie_gras', 'french_fries',
    'french_onion_soup', 'french_toast', 'fried_calamari', 'fried_rice', 'frozen_yogurt',
    'garlic_bread', 'gnocchi', 'greek_salad', 'grilled_cheese_sandwich', 'grilled_salmon',
    'guacamole', 'gyoza', 'hamburger', 'hot_and_sour_soup', 'hot_dog', 'huevos_rancheros',
    'hummus', 'ice_cream', 'lasagna', 'lobster_bisque', 'lobster_roll_sandwich',
    'macaroni_and_cheese', 'macarons', 'miso_soup', 'mussels', 'nachos', 'omelette',
    'onion_rings', 'oysters', 'pad_thai', 'paella', 'pancakes', 'panna_cotta', 'peking_duck',
    'pho', 'pizza', 'pork_chop', 'poutine', 'prime_rib', 'pulled_pork_sandwich', 'ramen',
    'ravioli', 'red_velvet_cake', 'risotto', 'samosa', 'sashimi', 'scallops', 'seaweed_salad',
    'shrimp_and_grits', 'spaghetti_bolognese', 'spaghetti_carbonara', 'spring_rolls',
    'steak', 'strawberry_shortcake', 'sushi', 'tacos', 'takoyaki', 'tiramisu', 'tuna_tartare',
    'waffles'
]
IMG_SIZE = 224  # Image size expected by the model

# Custom CSS to enhance the app's appearance with dark theme
st.markdown("""
<style>
    .reportview-container {
        background: #0E1117;
        color: #FAFAFA;
    }
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    h1, h2, h3 {
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        background-color: #262730;
        color: #FAFAFA;
        border-color: #4CAF50;
        border-radius: 5px;
    }
    .stPlotlyChart {
        background-color: #262730;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 4px 4px 0 0;
        padding: 10px 24px;
        color: #FAFAFA;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

def preprocess_image(img):
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img, dtype='float32')
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Normalize the image
    return img_array

def predict_food(img):
    preprocessed_img = preprocess_image(img)
    predictions = model.predict(preprocessed_img)
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    predicted_food_name = food_classes[predicted_class_index]
    confidence = predictions[0][predicted_class_index]
    return predicted_food_name, confidence

def analyze_food(food_name):
    # Replace the direct function call with an API request
    api_url = "https://home-api-z0vu.onrender.com/analyze_food"  # Update this URL if your Flask API is hosted elsewhere
    response = requests.post(api_url, json={"food_name": food_name})
    
    if response.status_code == 200:
        return response.json()['analysis']
    else:
        st.error(f"API Error: {response.status_code} - {response.text}")
        return None

def parse_analysis(analysis):
    if analysis is None:
        return [], [], "Unknown"
    
    lines = analysis.split('\n')
    ingredients = lines[0].split(': ')[1].split('|')
    health_scores = [int(score) for score in lines[1].split(': ')[1].split('|')]
    overall_health = lines[2].split(': ')[1]
    return ingredients, health_scores, overall_health


def create_health_chart(ingredients, health_scores):
    colors = ['#EF4444' if score < 4 else '#F59E0B' if score < 7 else '#10B981' for score in health_scores]
    fig = go.Figure(data=[go.Bar(
        x=ingredients,
        y=health_scores,
        marker_color=colors,
        text=health_scores,
        textposition='auto',
    )])
    fig.update_layout(
        title={
            'text': "Ingredient Health Scores",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Ingredients",
        yaxis_title="Health Score (0-10)",
        yaxis=dict(range=[0, 10]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=14, color="#FAFAFA"),
    )
    return fig

def get_food_image(food_name):
    api_key = "eA4LaKMKCBIKFvv6ktiOBaxBTFmA9BMzybaJUoHAWSotmh0agkhF0wzQ"
    if not api_key:
        st.warning("Pexels API key not found. Please check your .env file.")
        return None

    url = f"https://api.pexels.com/v1/search?query={food_name}&per_page=1"
    headers = {"Authorization": api_key}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        if data['photos']:
            image_url = data['photos'][0]['src']['medium']
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            img = Image.open(BytesIO(image_response.content))
            return img
        else:
            st.info(f"No images found for '{food_name}' on Pexels.")
            return None
    except requests.RequestException as e:
        st.error(f"Error retrieving image: {str(e)}")
        return None

def get_health_category(score):
    if score >= 7:
        return "Healthy", "#10B981"
    elif 4 <= score < 7:
        return "Moderate", "#F59E0B"
    else:
        return "Unhealthy", "#EF4444"

def display_food_analysis(food_name):
    st.subheader(f"Analyzing: {food_name}")
    
    with st.spinner("Analyzing food safety and health risks..."):
        try:
            analysis = analyze_food(food_name)
            ingredients, health_scores, overall_health = parse_analysis(analysis)

            col1, col2 = st.columns([1, 2])

            # with col1:
            #     # Display food image
            #     food_image = get_food_image(food_name)
            #     if food_image:
            #         st.image(food_image, caption=f"Image of {food_name}", use_column_width=True)
            #     else:
            #         st.image("https://via.placeholder.com/400x300?text=No+Image+Found", caption="Placeholder Image",
            #                 use_column_width=True)

            #     # Display overall health assessment
            #     st.subheader("Overall Health Assessment:")
            #     if overall_health.lower() == 'safe':
            #         st.success(f"✅ {food_name} is considered SAFE based on its ingredients.")
            #     else:
            #         st.error(f"⚠️ {food_name} is considered UNSAFE based on its ingredients.")

            # with col2:
            # Display health chart
            st.plotly_chart(create_health_chart(ingredients, health_scores), use_container_width=True)

            # Display ingredient details with hyperlinks
            st.subheader("Ingredient Details:")
            for ingredient, score in zip(ingredients, health_scores):
                health_category, color = get_health_category(score)
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: {color}40;">
                    <span style="font-weight: bold;">
                        <a href='https://en.wikipedia.org/wiki/{ingredient.replace(' ', '_')}' target='_blank' style="color: {color};">{ingredient}</a>
                    </span>: 
                    <span style="color: {color};">{health_category}</span> (Score: {score}/10)
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

def main():
    st.title("🍽️ Food Image Classifier and Health Analyzer")
    st.write("Upload an image, use your webcam to classify food, or enter a food name for analysis!")

    tab1, tab2 = st.tabs(["🖼️ Image Classification", "✍️ Manual Entry"])

    with tab1:
        st.header("Image Classification")
        # File uploader
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image.', use_column_width=True)
            st.write("")
            with st.spinner("Classifying..."):
                label, confidence = predict_food(image)
            st.success(f"Prediction: {label}")
            st.info(f"Confidence: {confidence:.2f}")
            
            if st.button("Analyze This Food", key="analyze_uploaded"):
                display_food_analysis(label)

        # Webcam capture
        st.subheader("Or use your webcam:")
        picture = st.camera_input("Take a picture")
        if picture:
            image = Image.open(picture)
            st.image(image, caption='Captured Image.', use_column_width=True)
            st.write("")
            with st.spinner("Classifying..."):
                label, confidence = predict_food(image)
            st.success(f"Prediction: {label}")
            st.info(f"Confidence: {confidence:.2f}")
            
            if st.button("Analyze This Food", key="analyze_webcam"):
                display_food_analysis(label)

    with tab2:
        st.header("Manual Food Entry")
        food_name = st.text_input("Enter a food item:", "cake")
        if st.button("Analyze Food", key="analyze_manual"):
            if food_name:
                # Generate and display the food image
                food_image = get_food_image(food_name)
                if food_image:
                    st.image(food_image, caption=f"Image of {food_name}", use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/400x300?text=No+Image+Found", caption="Placeholder Image",
                            use_column_width=True)
                
                # Display the food analysis
                display_food_analysis(food_name)
            else:
                st.warning("Please enter a food item to analyze.")

    st.markdown("---")
    st.write("Thank you for using the Food Image Classifier and Health Analyzer!")

if __name__ == '__main__':
    main()
