import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
import base64


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

# Streamlit app main interface
st.title("PaperStream")

# Layout configuration
col1, col2 = st.columns([7, 3])

with col1:
    # Upload PDF and show in viewer
    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
    all_text = ""
    if uploaded_file is not None:
        # Display PDF using an iframe to show all pages
        base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
        pdf_display = f"<iframe src='data:application/pdf;base64,{base64_pdf}' width='100%' height='100%' style='height:85vh;' type='application/pdf'></iframe>"
        st.markdown(pdf_display, unsafe_allow_html=True)

        # Reset file pointer and extract text
        uploaded_file.seek(0)
        reader = PdfReader(uploaded_file)
        all_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text() is not None])

with col2:
    st.header("Interact with Paper")

    # Document summarization
    st.subheader("Summary of the Paper")
    with st.spinner('Generating summary ...'):
        if st.button("Summarize"):
            summary_query = f"Summarize the following text: {all_text}"
            summary_response = st.session_state.chat_session.send_message(summary_query)
            st.write(summary_response.text)

    # Chat interaction
    st.subheader("Chat with Paper")
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])        

    # Accept user input
    query = st.chat_input("Ask a question about the paper")

    # Calling the Function when Input is Provided
    if query:
        with st.chat_message("user"):
            st.markdown(query)

        with st.spinner('Generating answer ...'):
            response = model.generate_content(all_text + query)
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "user", "content": query})
            st.session_state.messages.append({"role": "assistant", "content": response.text})
