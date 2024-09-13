import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Initialize session state for messages, URL summaries, and API key
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'url_summaries' not in st.session_state:
    st.session_state['url_summaries'] = []

# Sidebar for API key and URL input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
selected_option = st.sidebar.selectbox("Choose Option", ['Default Chatbot', 'Upload 1 URL', 'Upload 2 URLs'])

# Function to retrieve content from URL
def fetch_url_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Error fetching content from URL: {e}"

# Function to summarize the URL content
def summarize_content(content):
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=f"Summarize the following content: {content}",
        max_tokens=150,
    )
    return response.choices[0].text.strip()

# Function to chat with memory (summary + chat history)
def chat_with_memory(user_input):
    prompt = "\n".join([msg['content'] for msg in st.session_state['messages']]) + "\nSummary: " + "\n".join(st.session_state['url_summaries']) + "\nUser: " + user_input
    response = openai.Completion.create(
        engine="gpt-4o-mini",
        prompt=prompt,
        max_tokens=200,
    )
    return response.choices[0].text.strip()

# Main Chatbot Logic
if api_key:
    st.title("Chatbot with URL Summarization")

    if selected_option == 'Upload 1 URL' or selected_option == 'Upload 2 URLs':
        url_1 = st.text_input("Enter URL 1")
        if selected_option == 'Upload 2 URLs':
            url_2 = st.text_input("Enter URL 2")

        if st.button("Fetch and Summarize URLs"):
            if url_1:
                content_1 = fetch_url_content(url_1)
                summary_1 = summarize_content(content_1)
                st.session_state['url_summaries'].append(summary_1)
                st.write("Summary of URL 1:", summary_1)
            
            if selected_option == 'Upload 2 URLs' and url_2:
                content_2 = fetch_url_content(url_2)
                summary_2 = summarize_content(content_2)
                st.session_state['url_summaries'].append(summary_2)
                st.write("Summary of URL 2:", summary_2)

    # Chat section
    user_input = st.text_input("Ask your question")
    if user_input:
        # Add the user's message to session state
        st.session_state['messages'].append({"role": "user", "content": user_input})
        # Get chatbot response using the memory (summary + previous conversation)
        response = chat_with_memory(user_input)
        st.session_state['messages'].append({"role": "assistant", "content": response})
        st.write(f"Assistant: {response}")
else:
    st.warning("Please enter your OpenAI API key.")
