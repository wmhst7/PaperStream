import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
import base64
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# Initialize chat session if not already done
if "chat_session" not in st.session_state:
    st.session_state.chat_session = chat
    st.session_state.messages = []

# Streamlit page configuration
st.set_page_config(page_title="PaperStream", page_icon="📄", layout="wide")

# Page Navigation
page = st.sidebar.selectbox("Navigate", ["Home", "Visualize Data"])

if page == "Home":
    st.title("PaperStream")
    col1, col2 = st.columns([7, 3])

    with col1:
        uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
        all_text = ""
        if uploaded_file is not None:
            base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
            pdf_display = f"<iframe src='data:application/pdf;base64,{base64_pdf}' width='100%' height='100%' style='height:85vh;' type='application/pdf'></iframe>"
            st.markdown(pdf_display, unsafe_allow_html=True)

            uploaded_file.seek(0)
            reader = PdfReader(uploaded_file)
            all_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text() is not None])

    with col2:
        st.header("Interact with Paper")
        st.subheader("Summary of the Paper")
        with st.spinner('Generating summary ...'):
            if st.button("Summarize"):
                summary_query = f"Summarize the following text: {all_text}"
                summary_response = st.session_state.chat_session.send_message(summary_query)
                st.write(summary_response.text)

        st.subheader("Chat with Paper")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        query = st.chat_input("Ask a question about the paper")
        if query:
            with st.chat_message("user"):
                st.markdown(query)
            with st.spinner('Generating answer ...'):
                response = model.generate_content(all_text + query)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "user", "content": query})
                st.session_state.messages.append({"role": "assistant", "content": response.text})

elif page == "Visualize Data":
    st.title("Visualizations")
    if 'all_text' in st.session_state and st.session_state.all_text:
        text = st.session_state.all_text
        wordcloud = WordCloud(width = 800, height = 400).generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.error("Upload and process a PDF on the Home page first to generate visualizations.")
