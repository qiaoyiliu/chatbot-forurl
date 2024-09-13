import streamlit as st
import requests
from bs4 import BeautifulSoup

# Initialize session state for messages and URL summary
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'url_summary' not in st.session_state:
    st.session_state['url_summary'] = None

# Function to summarize URL content
def summarize_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.text for para in paragraphs[:5]])  # Take first 5 paragraphs
        return content[:1000]  # Limit summary to 1000 characters
    except Exception as e:
        return "There was an error fetching the URL content."

# Sidebar to upload URL
st.sidebar.title("Chatbot with URL Upload")
url = st.sidebar.text_input("Enter a URL")

# Summarize and store URL content
if url:
    if st.sidebar.button("Summarize URL"):
        st.session_state['url_summary'] = summarize_url(url)
        st.sidebar.success("URL successfully summarized!")

# Display chatbot and interactions
st.title("Chatbot")
st.write("This chatbot can summarize a URL and answer questions based on the URL content.")

# If URL summary is available, show it
if st.session_state['url_summary']:
    st.write("Summary of the URL:")
    st.write(st.session_state['url_summary'])

# Chat input and response
user_input = st.text_input("Ask a question", key="input_box")
if user_input:
    # Append user input to messages
    st.session_state['messages'].append(f"User: {user_input}")

    # Chatbot logic to respond to various questions
    if "where is yellowstone" in user_input.lower():
        response = "Yellowstone is primarily located in Wyoming, USA, with parts extending into Montana and Idaho."
    elif st.session_state['url_summary']:
        # If URL summary exists, use it to answer more questions
        response = f"I'm using the URL summary to respond: {st.session_state['url_summary'][:150]}..."
    else:
        response = "I don't have enough information to answer that question right now."

    # Append bot response to messages
    st.session_state['messages'].append(f"Bot: {response}")

# Display conversation history
for message in st.session_state['messages']:
    st.write(message)
