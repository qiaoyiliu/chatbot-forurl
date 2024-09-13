import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import deque

# Initialize session state for messages, URL summary, and short-term memory
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'url_summary' not in st.session_state:
    st.session_state['url_summary'] = None
if 'recent_chats' not in st.session_state:
    st.session_state['recent_chats'] = deque(maxlen=5)  # Store last 5 chats

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

# Function to respond to user input
def generate_response(user_input):
    # Check if the question is related to the URL summary
    if st.session_state['url_summary'] and user_input.lower() in st.session_state['url_summary'].lower():
        return f"I'm using the URL summary to respond: {st.session_state['url_summary'][:150]}..."
    
    # Check if the question is related to recent chats
    for previous_input in st.session_state['recent_chats']:
        if user_input.lower() in previous_input.lower():
            return f"I remember from our earlier conversation: {previous_input[:150]}..."
    
    # Default response
    return "I don't have enough information to answer that question right now."

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
st.write("This chatbot can summarize a URL and answer questions based on the URL content or recent conversation.")

# If URL summary is available, show it
if st.session_state['url_summary']:
    st.write("Summary of the URL:")
    st.write(st.session_state['url_summary'])

# Chat input and response
user_input = st.text_input("Ask a question", key="input_box")
if user_input:
    # Append user input to messages and recent chats
    st.session_state['messages'].append(f"User: {user_input}")
    st.session_state['recent_chats'].append(user_input)

    # Generate a response
    response = generate_response(user_input)

    # Append bot response to messages
    st.session_state['messages'].append(f"Bot: {response}")

# Display conversation history
for message in st.session_state['messages']:
    st.write(message)
