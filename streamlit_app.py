import streamlit as st
import replicate
import os
import csv
import uuid

CSV_PATH = 'feedback.csv'

# Check if CSV file exists, if not, create one
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Conversation Unique ID', 'Entire Conversation', 'Feedback'])

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Replicate Credentials
with st.sidebar:
    st.title('GenContentHUB')
    st.write('This chatbot is created using the open-source Llama 2 LLM model from Meta.')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        # st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Response Settings')
    system_message = st.sidebar.radio('Tone of chat', ['Friendly', 'Formal', 'Casual', 'Assertive', 'Sarcastic'], index=0, key='response_type')
    
     # If the previous selection is stored and it's different from the current selection
    if "previous_selection" in st.session_state and st.session_state.previous_selection != system_message:
        clear_chat_history()

    # Store the current selection for the next run
    st.session_state.previous_selection = system_message
    
    st.sidebar.subheader('Number of Slogans')
    number_of_slogans = st.sidebar.slider('Choose the number of slogans you want', min_value=1, max_value=5, value=1, step=1)
    
    # If the previous slogan count is stored and it's different from the current selection
    if "previous_slogan_count" in st.session_state and st.session_state.previous_slogan_count != number_of_slogans:
        clear_chat_history()

    # Store the current slogan count for the next run
    st.session_state.previous_slogan_count = number_of_slogans
    
    # Feedback mechanism in the sidebar
    st.sidebar.header("Feedback")
    st.sidebar.write("Are the responses helpful?")
    col1, col2= st.columns(2)
    thumbs_up = col1.button("👍 Yes")
    thumbs_down = col2.button("👎 No")

    if thumbs_up or thumbs_down:
        feedback_option = "Positive" if thumbs_up else "Negative"
        
        entire_conversation = "\n".join([msg["content"] for msg in st.session_state.messages])
        
        with open(CSV_PATH, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([st.session_state.conversation_id, entire_conversation, feedback_option])
        
        st.sidebar.success("Feedback saved successfully!")
        # Generate a new unique ID for the next conversation
        st.session_state.conversation_id = str(uuid.uuid4())


        
    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=1024, value=1024, step=8)
    
    st.button("Clear chat history", on_click=clear_chat_history)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today with?"}]

# Generate a unique ID when the conversation starts
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Clear chat history and generate a new ID for the conversation
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.session_state.conversation_id = str(uuid.uuid4())


# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = f"You are an AI assistant designed to create slogans.\n\n Generate exactly {number_of_slogans} slogans.\n\n"
    
    if system_message == "Friendly":
    # Friendly: Warm and welcoming responses.
        string_dialogue += "Generate Friendly Slogans, Embrace warmth and approachability in your slogans.\n\n"
        
    elif system_message == "Formal":
        # Formal: Professional and respectful slogans.
        string_dialogue += "Generate Formal Slogans, Ensure your slogans are straightforward, avoiding slang and casual phrases.\n\n"
        
    elif system_message == "Casual":
        # Casual: Conversational and relaxed slogans.
        string_dialogue += "Generate Casual Slogans, Approach as if speaking to a friend and use colloquial language if appropriate.\n\n"
        
    elif system_message == "Assertive":
        # Assertive: Direct and confident responses without aggression.
        string_dialogue += "Generate Assertive Slogans, Be direct and confident, ensuring clarity without coming off as aggressive.\n\n"
        
    elif system_message == "Sarcastic":
        # Sarcastic: Ironic and mocking responses.
        string_dialogue += "Generate Sarcastic Slogans, Use irony and perhaps say one thing but imply another. Emojis can help set the tone! 😒\n\n"


    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output


# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)