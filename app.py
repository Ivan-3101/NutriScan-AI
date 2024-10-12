import streamlit as st
import healthy
import ingredients
import disease
import diet_recommender
import ocr
# Move this line to the top, outside of any function
st.set_page_config(page_title="Food Safety & Health Analyzer", page_icon="🍽️")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Healthy Food Analysis", "Ingredient Analysis","Disease Prediction", "Diet Recommendation","Packed Food Analysis"])

    if page == "Healthy Food Analysis":
        st.title("🥗 Healthy Food Analysis")
        healthy.main()
    elif page == "Ingredient Analysis":
        st.title("🧪 Ingredient Analysis")
        ingredients.main()
    elif page == "Disease Prediction":
        st.title("🩺 Disease Prediction")
        disease.main()
    elif page == "Packed Food Analysis":
        st.title("🔎 Packed Food Analysis")
        ocr.main()
    else:
        st.title("🍽️ AI-Powered Personalized Diet Recommender")
        diet_recommender.main()

if __name__ == "__main__":
    main()