from flask import Flask, render_template, request
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

os.environ["OPENAI_API_KEY"] = "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"
#os.chdir("D:\src\idb_2023_summer\shanruocheng")


app = Flask(__name__)
pdf_dir = "static/pdf"
index_dir = "db_index/faiss_index_all"
embeddings = OpenAIEmbeddings()
docsearch = FAISS.load_local(index_dir, embeddings)
qa_chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")
qa_all = RetrievalQA(combine_documents_chain=qa_chain, retriever=docsearch.as_retriever(), return_source_documents=True, max_tokens_limit=3000)


def decode(s):
    return s.replace("%20", " ")

@app.route('/')
def index():
    table_contents = []
    table_headers = ("Category", "File Name")
    for dir in os.listdir("static/pdf"):
        for file in os.listdir("static/pdf/"+dir):
            category = dir
            file_name = file.replace(".pdf", "")
            file_path = "static/pdf/{}/{}".format(dir, file)
            d = {"category": category, "name": file_name, "URL": file_path}
            table_contents.append(d)
    return render_template("index.html", table_headers=table_headers, table_contents=table_contents)


@app.route("/open_pdf/<file>", methods=["POST"])
def open_pdf(file):
    a = 1
    print(111111111111)
    try:
        return render_template("pdf_view.html", pdf=file)
    # pdf_path = f"/static/pdf/{file_name}".format(file_name=file_name)
    except:
        return render_template("pdf_view.html", pdf="")
    

@app.route("/collection_search", methods=["POST"])
def collection_search():
    query = request.form["user_query"]
    if "pre_packaged_query" in request.form:
        query = request.form["pre_packaged_query"]

    category = "Category"
    if category != "Category":
        docsearch2 = FAISS.load_local("db_index/category_index/{}".format(category), embeddings)
        qa_chain2 = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")
        qa2 = RetrievalQA(combine_documents_chain=qa_chain2, retriever=docsearch2.as_retriever(), return_source_documents=True)
        answers = qa2({"query": query})
    else:
        answers = qa_all({"query": query})

    table_contents = []
    result = answers["result"]
    for info in answers["source_documents"]:
        row = {}
        content = info.page_content
        source = info.metadata["source"]
        page_num = info.metadata["page"]
        page = '#page={}'.format(page_num)
        name = source.replace("static/pdf/", "")
        row["content"] = content
        row["source"] = source+page
        row["name"] = name
        table_contents.append(row)
    return render_template("collection_search_tmp.html", table_contents=table_contents, result=result)


@app.route("/to_page", methods=["POST"])
def to_page():
    page_num = request.form["page"]
    page = "#page={}".format(page_num)
    return render_template("home.html", pdf="/static/pdf/IDB Group Strategy with Panama 2021-2024 public_ENG.pdf"+page)


@app.route("/pre_search", methods=["POST"])
def pre_search():
    page_num = request.form["pre_query"]
    page = "#page={}".format(page_num)
    return render_template("home.html", pdf="/static/pdf/IDB Group Strategy with Panama 2021-2024 public_ENG.pdf"+page)


@app.route("/dynamic_search", methods=["POST"])
def dynamic_search():
    page_num = request.form["query"]
    page = "#page={}".format(page_num)
    return render_template("home.html", pdf="/static/pdf/IDB Group Strategy with Panama 2021-2024 public_ENG.pdf" + page)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
