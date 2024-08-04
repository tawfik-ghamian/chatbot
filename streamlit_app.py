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
st.title("_Streamlit_ is ")


index_name = "fam-rag"
docs = []

encoder = HuggingFaceEncoder(name="dwzhu/e5-base-4k")

# groq_client = Groq(api_key="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")
llm = Groq(model="llama3-70b-8192", api_key="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")

# configure client
pc = Pinecone(api_key="595c294f-e189-4051-9023-35461b30dc47")

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
    
    if not prompt.__contains__(" yes ") or not prompt.__contains__(" no "):
        docs = get_docs(prompt, 10,encoder, index)
        docs = [str(i) for i in docs]

        # result = generate(prompt, docs, groq_client, st.session_state.messages)

    docs = "\n---\n".join(docs)
    
    system_message =f'''
        You are a real state assistant that helps users find best properties in Dubai that fit there requirement using the
        context provided below that is you information.
        when you make any mistake please don't tell the user anything about it. 
        please be precise when you answer the user and search in your history for the answer.
    
        if the context or the chat history may not have the answer of the question please
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

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    print(resp)
    res = [i.delta for i in resp ]
    with st.chat_message("assistant"):
        response = st.write_stream(res)

    st.session_state.messages.append(ChatMessage(role= "assistant", content= "".join([i for i in response])))
