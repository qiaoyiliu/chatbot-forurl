# Show title and description.
import streamlit as st
from openai import OpenAI
from bs4 import BeautifulSoup
import requests

st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-4o-mini model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

def summarize_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.text for para in paragraphs[:5]])  # Take first 5 paragraphs
        return content[:1000]  # Limit summary to 1000 characters
    except Exception as e:
        return "There was an error fetching the URL content."

# Ask user for their OpenAI API key via st.text_input.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    question_url = st.text_area(
        "Or insert an URL:",
        placeholder="Copy URL here",
    )

    st.session_state['url_summary'] = summarize_url(question_url)
    if st.session_state['url_summary']:
        st.session_state['messages'].append({
            "role": "assistant",
            "content": f"Summary of the URL: {st.session_state['url_summary']}"
        })
    
    # Sidebar for memory management options.
    memory_option = st.sidebar.radio(
        "Choose how to store memory:",
        ("Last 5 questions", "Summary of entire conversation", "Last 5,000 tokens")
    )

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input field for user messages.
    if prompt := st.chat_input("What is up?"):
        
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Adjust memory based on the user's selection.
        if memory_option == "Last 5 questions":
            # Keep only the last 5 user and assistant messages.
            st.session_state.messages = st.session_state.messages[-10:]
        elif memory_option == "Summary of entire conversation":
            # Summarize the conversation and keep only the summary.
            conversation_summary = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]
            )
            st.session_state.messages = [{"role": "system", "content": conversation_summary}]
        elif memory_option == "Last 5,000 tokens":
            # Ensure that the conversation doesn't exceed 5,000 tokens (simplified).
            conversation_text = "\n".join([msg["content"] for msg in st.session_state.messages])
            if len(conversation_text) > 5000:
                st.session_state.messages = st.session_state.messages[-100:]

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )

        # Stream the response to the chat.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})