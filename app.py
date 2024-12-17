import streamlit as st
import replicate
import os
import PyPDF2
from io import BytesIO
import pyperclip
from streamlit_option_menu import option_menu
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

### GLOBAL VARIABLES ###
language_map= {'English': 'en'}

temperate_options= {
    "More Creative": 1.5,
    "Balanced": 0.7,
    "Precise": 0.1
}
length_options= {
    'Shorter': 0.25,
    'Balanced': 1.0,
    'Longer': 2.0
}
### END OF GLOBAL VARIABLES ###

### HELPER FUNCTIONS ###
def generate_propertybot_response(prompt_input):
    # Example of setting a new assistant name and dialogue context
    string_dialogue = """
    You are a friendly and knowledgeable assistant named PropertyBot. You assist users with information about real estate, property buying, market trends, and advice for homebuyers and investors.
    You provide helpful responses to users about properties, including details on prices, locations, amenities, and market advice.
    Your goal is to make users feel confident in their property-related decisions.

    Here’s the context for the conversation:
    If available, I will provide property listings, real estate market analysis, and help with home search preferences. You should use this information to guide the user to find the best property options.

    Current User Preferences:
    """

    # If the user uploaded any property-related file, include it in the context:
    if st.session_state.file_content != '':
        string_dialogue += f'Additional File Content: {" ".join(st.session_state.file_content.split()[:1500])}\n\n'

    # Append all user messages to the context:
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += f"User: {dict_message['content']}\n\n"
        else:
            string_dialogue += f"PropertyBot: {dict_message['content']}\n\n"
    
    output = replicate.run(llm, 
                           input= {
                               "prompt": f"{string_dialogue}\n\nUser: {prompt_input}\n\nPropertyBot: ",
                               "temperature": temperate_options[selected_temperature_option],
                               "top_p": 0.9,
                               "max_tokens": max_length,
                               "repetition_penalty": 1,
                               "length_penalty": length_options[selected_length_option]
                           })
    return output

def clear_chat_history():
    st.session_state.messages= []

def clear_file_content():
    st.session_state.file_content= ''
    
def regenerate_response():
    print ('Regenerating response...')
    if st.session_state.messages[-1]['role'] == 'assistant':
        st.session_state.messages.pop()
        with st.spinner("Thinking..."):
            response= generate_llama2_response(prompt)
            response_placeholder= st.empty()
            full_response= ''
            for item in response:
                full_response+= item
                response_placeholder.markdown(full_response)
            response_placeholder.markdown(full_response)
        if language != 'English':
            full_response= translate_output(full_response)
        message= {"role": "assistant", "content": full_response, "Index": len(st.session_state.messages)+1}
        st.session_state.messages.append(message)
        st.rerun()

def chat_function_bar():
    col1, col2= st.columns(2)
    with col1:
        if st.button('📋 Copy response to clipboard', use_container_width= True, help= 'Copy response to clipboard'):
            try:
                pyperclip.copy(st.session_state.messages[-1]['content'])
            except:
                st.error('Error copying text, this is most likely caused by incompatibility issues with your browser. You can try to Ctrl+A and Ctrl+C instead.')
    with col2:
        if st.button('🔂 Regenerate response', use_container_width= True, help= 'Regenerate response from llama model. You can further adjust model parameter(s) then, proceed to regenerate the last response.'):
            regenerate_response()
    st.markdown('')
##### Page Configurations
st.set_page_config(page_title= "SurgiSense | Surgi Chatbot",
                   layout= 'wide',
                   page_icon= '	:medical_symbol:')
st.logo('assets/SurgiSense Logo.png', link= 'https://npdscpproject.wixsite.com/surgisense')

##### Setting session state information
if not hasattr(st.session_state, 'file_content'):
    st.session_state.file_content= ''
if "messages" not in st.session_state.keys():
    st.session_state.messages= []
if not hasattr(st.session_state, 'edit_prompt'):
    st.session_state.edit_prompt= False

st.subheader('SurgiSense, the Medical Chat Bot', help= 'Please use this model to assist and complement your processes rather than solely depending and assuming from it.')
st.markdown('The medical chatbot for all your medical query needs! It is a probabilistic model so it may not always be correct.', unsafe_allow_html= True)
st.divider()

with st.sidebar:
    st.title('Llama 2 LLM models from Meta.')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        print ('Token in secrets')
        st.success('Surgi Chatbot Online', icon= '✅')
        replicate_api= st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api= st.text_input('Enter Replicate API token:', type= 'password', help= 'Replicate API is needed to use this service. If you do not have one, please sign in to https://replicate.com/ using your GitHub account and retrieve your API Token from there.')
        if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
            st.warning('Please enter your credentials!', icon= '⚠️')
        else:
            st.success('Surgi Chatbot Online', icon= '✅')
    os.environ['REPLICATE_API_TOKEN']= replicate_api

