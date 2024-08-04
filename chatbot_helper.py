def get_docs(question: str, top_k: int, encoder, pinecone_index) -> list[str]:
    # encode query
    xq = encoder([question])
    # search pinecone index
    res = pinecone_index.query(vector=xq, top_k=top_k, include_metadata=True)
    # get doc text
    print(res)
    docs = [x["metadata"] for x in res["matches"]]
    return docs

def generate(query: str, docs: list[str], groq_client, messages):
    docs = "\n---\n".join(docs)
    system_message =f'''
        You are a real state assistant that answers questions about properties in Dubai using the
        context provided below that is you information.
        then please generate the response like this schema
        [ANS]
        ```json
        {{
            answer: HERE THE RESPONSE OF LLM
        }}```
        [\ANS]
        if the context may not have the answer of the question please
        ask user to provide you more information
        \n\n
        CONTEXT:\n
        {docs}
        '''
    
    # generate response
    chat_response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        stream=True
    )
    print(chat_response)
    for chunk in chat_response:
        return chunk.choices[0].delta.content
    # return chat_response.choices[0].message.content