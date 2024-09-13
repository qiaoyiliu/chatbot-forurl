import streamlit as st
import requests
from bs4 import BeautifulSoup

# Initialize session state for memory
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'url_summary' not in st.session_state:
    st.session_state['url_summary'] = None

# Function to summarize the URL content
def summarize_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    content = ' '.join([para.text for para in paragraphs[:5]])  # Limit the content summarized
    return content

# Sidebar to upload URL
st.sidebar.title("Chatbot with URL Upload")
url = st.sidebar.text_input("Enter a URL")

# If URL is uploaded
if url:
    if st.sidebar.button("Summarize URL"):
        st.session_state['url_summary'] = summarize_url(url)
        st.sidebar.success("URL successfully summarized!")

# Chatbot interface
st.title("Chatbot")
st.write("This chatbot summarizes a URL and allows interaction with memory.")

# If there's a summary, display it
if st.session_state['url_summary']:
    st.write("URL Summary:")
    st.write(st.session_state['url_summary'])

# Chat input
user_input = st.text_input("Ask a question")
if user_input:
    st.session_state['messages'].append(f"User: {user_input}")
    response = "This is a placeholder response."  # Replace with your chatbot logic
    st.session_state['messages'].append(f"Bot: {response}")

# Display chat history
for message in st.session_state['messages']:
    st.write(message)
