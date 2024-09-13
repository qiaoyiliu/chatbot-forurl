import streamlit as st
import openai
import os
from openai import OpenAI
import pdfplumber
from anthropic import Anthropic
from mistralai import Mistral
import requests
from bs4 import BeautifulSoup

st.title("Joy's URL Question Answering for HW2")
st.write(
    "Insert a URL below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an API key."
)

# Function to read content from URL
def read_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        st.error(f"Error reading {url}: {e}")
        return None

# Function to display and interact with selected LLM
def display(selected_llm):
    client = None

    # Select the appropriate LLM based on sidebar selection
    if selected_llm == 'gpt-4o-mini':
        api_key = st.secrets['OPENAI_API_KEY']
        if api_key:
            client = OpenAI(api_key=api_key)
        else:
            st.warning("Please provide OpenAI API key")
            return
    elif selected_llm == 'claude-3-haiku-20240307':
        api_key = st.secrets['ANTHROPIC_API_KEY']
        if api_key:
            client = Anthropic(api_key=api_key)
        else:
            st.warning("Please provide Anthropic API key")
            return
    elif selected_llm == 'mistral-small-latest':
        api_key = st.secrets['MISTRAL_API_KEY']
        if api_key:
            client = Mistral(api_key=api_key)
        else:
            st.warning("Please provide Mistral API key")
            return
    elif selected_llm == 'gpt-4o-2024-05-13':
        api_key = st.secrets['OPENAI_API_KEY']
        if api_key:
            client = OpenAI(api_key=api_key)
        else:
            st.warning("Please provide OpenAI API key")
            return
    elif selected_llm == 'claude-3-opus-20240229':
        api_key = st.secrets['ANTHROPIC_API_KEY']
        if api_key:
            client = Anthropic(api_key=api_key)
        else:
            st.warning("Please provide Anthropic API key")
            return
    elif selected_llm == 'mistral-medium-latest':
        api_key = st.secrets['MISTRAL_API_KEY']
        if api_key:
            client = Mistral(api_key=api_key)
        else:
            st.warning("Please provide Mistral API key")
            return

    # Input field for URL
    question_url = st.text_area(
        "Insert an URL:",
        placeholder="Copy URL here",
    )

    # Dropdown to select language
    languages = ['English', 'Spanish', 'French']
    selected_language = st.selectbox('Select your language:', languages)
    st.write(f"You have selected: {selected_language}")

    # Input field for question
    question = st.text_area(
        "Now ask a question about the URL content!",
        placeholder="Can you give me a short summary?",
        disabled=not question_url,
    )

    if client is None:
        st.info("Please enter API key to continue.")
    elif question_url and question:
        url_content = read_url_content(question_url)
        if url_content:
            messages = [
                {
                    "role": "user",
                    "content": f"Respond in {selected_language}. Here's a URL: {url_content} \n\n---\n\n {question}",
                }
            ]

            # GPT-4o-mini stream response
            if selected_llm == "gpt-4o-mini":
                stream = client.chat.completions.create(
                    model=selected_llm,
                    max_tokens=250,
                    messages=messages,
                    stream=True,
                    temperature=0.5,
                )
                st.write_stream(stream)

            # GPT-4o-2024-05-13 stream response
            elif selected_llm == 'gpt-4o-2024-05-13':
                stream = client.chat.completions.create(
                    model=selected_llm,
                    max_tokens=250,
                    messages=messages,
                    stream=True,
                    temperature=0.5,
                )
                st.write_stream(stream)

            # Claude-3-opus response
            elif selected_llm == 'claude-3-opus-20240229':
                message = client.messages.create(
                    model=selected_llm,
                    max_tokens=256,
                    messages=messages,
                    temperature=0.5,
                )
                data = message.content[0].text
                st.write(data)

            # Mistral-small-latest response
            elif selected_llm == 'mistral-small-latest':
                response = client.chat.complete(
                    model=selected_llm,
                    max_tokens=250,
                    messages=messages,
                    temperature=0.5,
                )
                data = response.choices[0].message.content
                st.write(data)

            # Mistral-medium-latest response
            elif selected_llm == 'mistral-medium-latest':
                response = client.chat.complete(
                    model=selected_llm,
                    max_tokens=250,
                    messages=messages,
                    temperature=0.5,
                )
                data = response.choices[0].message.content
                st.write(data)

# Sidebar for selecting LLM
llm_options = [
    'gpt-4o-mini',
    'claude-3-haiku-20240307',
    'mistral-small-latest',
    'gpt-4o-2024-05-13',
    'claude-3-opus-20240229',
    'mistral-medium-latest'
]
selected_llm = st.sidebar.selectbox('Select an LLM:', llm_options)

display(selected_llm)
