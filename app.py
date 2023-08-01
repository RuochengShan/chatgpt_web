from flask import Flask, request
import openai
import json

app = Flask(__name__)

openai_key = ""
openai.api_key = openai_key

@app.route("/chatCompletion", methods=["POST"])
def chatCompletion():
    data = request.json
    model = data["model"]
    messages = data["messages"]
    temperature = data["temperature"]


    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response

if __name__ == "__main__":
    app.run("0.0.0.0", port=5002)