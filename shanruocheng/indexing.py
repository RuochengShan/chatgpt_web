import os
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
import json

os.environ["OPENAI_API_KEY"] = "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"

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
# indexing for all files
documents = []
failed = []
for dir in os.listdir("static/pdf"):
    sub_documents = []
    for file in os.listdir("static/pdf/"+dir):
        file_name = file.replace(".pdf", "")
        print(dir, file_name)

        pdf_path = "static/pdf/"+ dir + "/"+ file
        loader = PyPDFLoader(pdf_path)
    
        doc = loader.load()

        documents.extend(doc)
        sub_documents.extend(doc)
        
        text1 = text_splitter.split_documents(doc)
        db1 = FAISS.from_documents(text1, embedding=OpenAIEmbeddings())
        # try:
        #     db1.save_local("db_index/single_file_index/{}".format(file_name))
        # except:
        #     failed.append(dir+"/"+file_name)
    
    sub_documents = text_splitter.split_documents(sub_documents)
    db2 = FAISS.from_documents(sub_documents, embedding=OpenAIEmbeddings())
    db2.save_local("db_index/category_index/{}".format(dir))

documents = text_splitter.split_documents(documents)
db = FAISS.from_documents(documents, embedding=OpenAIEmbeddings())
db.save_local("db_index/faiss_index_all")

# with open("failed.json", "w") as f:
#     json.dump(failed, f)
