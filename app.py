import streamlit as st
import healthy
import ingredients
import disease
import diet_recommender
import ocr
# Move this line to the top, outside of any function
st.set_page_config(page_title="Food Safety & Health Analyzer", page_icon="🍽️", layout="wide")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Healthy Food Analysis", "Ingredient Analysis", "Diet Recommendation","Optical Character Recognition","Disease Prediction"])

    if page == "Healthy Food Analysis":
        st.title("🥗 Healthy Food Analysis")
        healthy.main()
    elif page == "Ingredient Analysis":
        st.title("🧪 Ingredient Analysis")
        ingredients.main()
    elif page == "Disease Prediction":
        st.title("🩺 Disease Prediction")
        disease.main()
    elif page == "Optical Character Recognition":
        st.title("🔎 Optical Character Recognition")
        ocr.main()
    else:
        st.title("🍽️ AI-Powered Personalized Diet Recommender")
        diet_recommender.main()

if __name__ == "__main__":
    main()