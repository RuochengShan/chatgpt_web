import streamlit as st
import random
import time
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory


os.environ["OPENAI_API_KEY"] = "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"
pdf_dir = "static/pdf"
index_dir = "db_index/faiss_index_all"
embeddings = OpenAIEmbeddings()
docsearch = FAISS.load_local(index_dir, embeddings)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, k=3)
memory.input_key = "question"
memory.output_key = "answer"
qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), docsearch.as_retriever(), memory=memory, max_tokens_limit=3000, return_source_documents=True)

st.title("IDB DocQA")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to IDB's DocQA app! You can ask me anything about IDB's public Country Strategies and Sector Framework Documents."}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("ask a question about your documents"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        result = qa({"question": prompt})
        assistant_response = result["answer"]
        assistant_response = assistant_response.replace("$", " dollar ")
        print(prompt, assistant_response)
        st.markdown(assistant_response)
        for doc in result["source_documents"]:
            docinfo = doc.metadata
            st.text(docinfo)
        # # Simulate stream of response with milliseconds delay
        # for chunk in assistant_response.split():
        #     full_response = ""
        #     full_response += chunk + " "
        #     time.sleep(0.05)
        #     # Add a blinking cursor to simulate typing
        #     message_placeholder.markdown(full_response + "▌")
        # message_placeholder.markdown(full_response)
# Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})