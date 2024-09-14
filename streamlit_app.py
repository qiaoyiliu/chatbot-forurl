import streamlit as st
from openai import OpenAI
from anthropic import Anthropic  # Assuming this is the correct Anthropic client
from mistral import Mistral  # Assuming this is the correct Mistral client

# Title
st.title("💬 Multi-LLM Chatbot")

# Sidebar to choose LLM
selected_llm = st.sidebar.selectbox(
    "Choose an LLM model:",
    ("gpt-4o-mini", "gpt-4o", "claude-3-haiku", "claude-3-opus", "mistral-small", "mistral-medium")
)

# Ask for API keys based on selected LLM
if selected_llm in ['gpt-4o-mini', 'gpt-4o']:
    api_key = st.secrets['OPENAI_API_KEY']
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        st.warning("Please provide OpenAI API key")

elif selected_llm in ['claude-3-haiku', 'claude-3-opus']:
    api_key = st.secrets['ANTHROPIC_API_KEY']
    if api_key:
        client = Anthropic(api_key=api_key)
    else:
        st.warning("Please provide Anthropic API key")

elif selected_llm in ['mistral-small', 'mistral-medium']:
    api_key = st.secrets['MISTRAL_API_KEY']
    if api_key:
        client = Mistral(api_key=api_key)
    else:
        st.warning("Please provide Mistral API key")

# Initialize session state for messages
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Display existing chat messages
for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input field
if prompt := st.chat_input("What is up?"):
    # Append user input to session state
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for the LLM API call
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state['messages']]

    # Call the selected LLM
    if selected_llm == "gpt-4o-mini":
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=250,
            messages=messages,
            stream=True,
            temperature=0.5,
        )
        st.write_stream(stream)

    elif selected_llm == "gpt-4o":
        stream = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=250,
            messages=messages,
            stream=True,
            temperature=0.5,
        )
        st.write_stream(stream)

    elif selected_llm == 'claude-3-haiku':
        message = client.messages.create(
            model='claude-3-haiku-20240307',
            max_tokens=256,
            messages=messages,
            temperature=0.5,
        )
        data = message.content[0].text
        st.write(data)

    elif selected_llm == 'claude-3-opus':
        message = client.messages.create(
            model='claude-3-opus-20240229',
            max_tokens=256,
            messages=messages,
            temperature=0.5,
        )
        data = message.content[0].text
        st.write(data)

    elif selected_llm == 'mistral-small':
        response = client.chat.complete(
            model='mistral-small-latest',
            max_tokens=250,
            messages=messages,
            temperature=0.5,
        )
        data = response.choices[0].message.content
        st.write(data)

    elif selected_llm == 'mistral-medium':
        response = client.chat.complete(
            model='mistral-medium-latest',
            max_tokens=250,
            messages=messages,
            temperature=0.5,
        )
        data = response.choices[0].message.content
        st.write(data)

    # Store the LLM response in session state
    st.session_state['messages'].append({"role": "assistant", "content": data})
