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

    # Sidebar selection for URL upload option (1 or 2 URLs)
    url_option = st.sidebar.radio(
        "Choose the number of URLs to summarize:",
        ("1 URL", "2 URLs")
    )

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'url_summary_1' not in st.session_state:
        st.session_state['url_summary_1'] = None
    if 'url_summary_2' not in st.session_state:
        st.session_state['url_summary_2'] = None
    if 'summary_added' not in st.session_state:
        st.session_state['summary_added'] = False

    # First URL
    question_url_1 = st.text_area(
        "Insert the first URL:",
        placeholder="Copy the first URL here",
    )
    
    if question_url_1 and not st.session_state['summary_added']:
        st.session_state['url_summary_1'] = summarize_url(question_url_1)
        if st.session_state['url_summary_1']:
            st.session_state['messages'].insert(0, {  # Insert the first summary at the start
                "role": "system",
                "content": f"Summary of the first URL: {st.session_state['url_summary_1']}"
            })
            st.session_state['summary_added'] = True  # Mark the first summary as added

    # Handle second URL if the user selected "2 URLs"
    if url_option == "2 URLs":
        question_url_2 = st.text_area(
            "Insert the second URL:",
            placeholder="Copy the second URL here",
        )
        if question_url_2 and not st.session_state.get('summary_added_2', False):
            st.session_state['url_summary_2'] = summarize_url(question_url_2)
            if st.session_state['url_summary_2']:
                st.session_state['messages'].insert(1, {  # Insert the second summary after the first
                    "role": "system",
                    "content": f"Summary of the second URL: {st.session_state['url_summary_2']}"
                })
                st.session_state['summary_added_2'] = True  # Mark the second summary as added
    
    # Sidebar for memory management options.
    memory_option = st.sidebar.radio(
        "Choose how to store memory:",
        ("Last 5 questions", "Summary of entire conversation", "Last 5,000 tokens")
    )

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

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
            user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
            assistant_messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"]
            system_messages = [msg for msg in st.session_state.messages if msg["role"] == "system"]

            # Trim only user and assistant messages, keeping the system messages (URL summaries)
            st.session_state.messages = system_messages + user_messages[-5:] + assistant_messages[-5:]
        
        elif memory_option == "Summary of entire conversation":
            # Summarize the conversation and keep only the summary.
            conversation_summary = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages if msg["role"] != "system"]
            )
            st.session_state.messages = system_messages + [{"role": "system", "content": conversation_summary}]
        
        elif memory_option == "Last 5,000 tokens":
            # Ensure that the conversation doesn't exceed 5,000 tokens (simplified).
            conversation_text = "\n".join([msg["content"] for msg in st.session_state.messages if msg["role"] != "system"])
            if len(conversation_text) > 5000:
                st.session_state.messages = st.session_state.messages[-100:]
            # Keep the system messages (URL summaries)
            st.session_state.messages = system_messages + st.session_state.messages

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
