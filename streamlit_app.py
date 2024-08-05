import streamlit as st
import os
import getpass
import time
from chatbot_helper import generate, get_docs
from llama_index.core.llms import ChatMessage
# from groq import Groq
from pinecone import Pinecone
from llama_index.llms.groq import Groq
from semantic_router.encoders import HuggingFaceEncoder

st.title("🤖 Welcome in :blue[_fam_ _properties_] ChatBot :sunglasses:")

index_name = "fam-rag"
docs = []

encoder = HuggingFaceEncoder(name="dwzhu/e5-base-4k")

# groq_client = Groq(api_key="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")

llm = Groq(model="llama3-70b-8192", api_key= st.secrets['GROQ_API_KEY'])

# configure client
pc = Pinecone(api_key= st.secrets['PINECONE_API_KEY'])

index = pc.Index(index_name)
time.sleep(1)


if "messages" not in st.session_state:
    st.session_state.messages = [
    
        ChatMessage(role="system", content="You are a real state assistant that helps users find best properties in Dubai that fit there requirement")
]

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    if message.role != "system":
        with st.chat_message(message.role):
            st.markdown(message.content)

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.    

    # Generate a response using the OpenAI API.
    # stream = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": m["role"], "content": m["content"]}
    #         for m in st.session_state.messages
    #     ],
    #     stream=True,
    # ) 
    with st.chat_message("user"):
        st.markdown(prompt)
    
    if not prompt.__contains__("Yes") or not prompt.__contains__("No"):
        docs = get_docs(prompt, 3,encoder, index)
        docs = [str(i) for i in docs]

        # result = generate(prompt, docs, groq_client, st.session_state.messages)

    docs = "\n---\n".join(docs)
    
    system_message =f'''
        You are a real state assistant act as that and help users find best properties in Dubai that fit there requirement using the
        context and chat history provided below. 
        please be precise when you answer the user and get the answer from your history if the question is not related to the context.
        if you ask the user a yes/no question do not use the provided context for response, use chat history for answer instead.
    
        if the context or the chat history may not have the answer of the question get the answer from chat history if not related please
        ask user to provide you more information
        \n\n
        CONTEXT:\n
        {docs}
        '''
    for i, k in enumerate(st.session_state.messages):
        if k.role =="system":
            st.session_state.messages[i].content = system_message

    st.session_state.messages.append(ChatMessage(role= "user", content=prompt))

    # generate response
    # chat_response = groq_client.chat.completions.create(
    #     model="llama3-70b-8192",
    #     messages=[
    #         {"role": m["role"], "content": m["content"]}
    #         for m in st.session_state.messages
    #     ],
    #     stream=True
    # )
    resp = llm.stream_chat(st.session_state.messages)
    print(st.session_state.messages)

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    print(resp)
    res = [i.delta for i in resp ]
    with st.chat_message("assistant"):
        response = st.write_stream(res)

    st.session_state.messages.append(ChatMessage(role= "assistant", content= "".join([i for i in response])))
