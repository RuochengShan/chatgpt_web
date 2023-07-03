import openai, html, json
import gradio as gr
#openai.organization = "YOUR ORG ID"
openai.api_key = "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"

primary_nations = ["Panama", "Argentina", "Bahamas", "Barbados", "Belize", "Bolivia", "Brazil", "Chile", "Colombia", "Costa Rica", "Dominican Republic", "Ecuador", "El Salvador", "Guatemala", "Guyana", "Haiti", "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama", "Paraguay", "Peru", "Suriname", "Trinidad", "Tobago", "Uruguay", "Venezuela"]

primary_sectors = ["Agriculture", "Skills Development", "Integration and Trade", "Housing and Urban Development", "Health", "Labor", "Transportation", "Support to SMEs and Financial Access/Supervision", "Citizen Security and Justice", "Tourism", "Social Protection and Poverty", "Water and Sanitation", "Innovation, Science and Technology", "Gender and Diversity", "Decentralization and Subnational Governments", "Environment and Biodiversity", "Climate Change", "Energy", "Fiscal Management", "Early Childhood Development", "Transparency and Integrity", "Extractive Industries"]

def escape_text(txt):
    return html.escape(txt).replace("$","&#36;")

rate_function = [{
    "name": "rate_article",
    "description": "Rate the user's input article by two integers",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "List of keywords of the article in English"
            },
            "people": {
                "type": "string",
                "description": "List of names of important people in English"
            },
            "institutions": {
                "type": "string",
                "description": "List of names of important institutions in English"
            },
            "primary_sector": {
                "type": "string",
                "enum": primary_sectors,
                "description": "The sector closest to the topic of the article"
            },
            "primary_nation": {
                "type": "string",
                "enum": primary_nations,
                "description": "The English name of the nation that is most relevant to the article"
            },
            "sector_relevance": {
                "type": "string",
                "description": "On a scale from 1 to 10, is the article relevant to any of primary_sector?"
            },
            "nation_relevance": {
                "type": "string",
                "description": "On a scale from 1 to 10, is the article relevant to Latin America and the Caribbean?"
            }
        },
        "required": ["nation_relevance","sector_relevance"]
    }
}]

def rate_ChatGPT(prompt):
    return openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo-0613',
        messages = [
            {"role": "user", "content": prompt},
        ],
        functions = rate_function,
        function_call = {"name": "rate_article"},
        temperature=0
)

def ask_ChatGPT(prompt, stream=True):
    return openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": "You are a news article summarizer. You convert a news article into an English summary of a few bullet points."},
        ],
        temperature=0,
        stream=stream
)

def write_article_metadata(prompt_msg):
    response_message = rate_ChatGPT(prompt_msg)["choices"][0]["message"]
    output_msg = ""
    if "function_call" in response_message:
        function_args = json.loads(response_message["function_call"]["arguments"])

        primary_nation = ""
        if "primary_nation" in function_args:
            primary_nation = function_args['primary_nation']
        if primary_nation != "" and primary_nation not in primary_nations:
            nation_relevance = 1
        else:
            nation_relevance = function_args['nation_relevance']
        output_msg += f"- Regional Relevance: {nation_relevance}/10"
        if primary_nation != "" and primary_nation != "Latin America and the Caribbean":
            output_msg += f" (Most relevant to {primary_nation})"
        output_msg += "\n"

        primary_sector = ""
        if "primary_sector" in function_args:
            primary_sector = function_args['primary_sector']
        if primary_sector != "" and primary_sector not in primary_sectors:
            sector_relevance = 1
        else:
            sector_relevance = function_args['sector_relevance']
        output_msg += f"- Sector Relevance: {sector_relevance}/10"
        if primary_sector != "":
            output_msg += f" (Most relevant to {primary_sector})"
        output_msg += "\n"

        if "keywords" in function_args and function_args['keywords'] != "":
            output_msg += f"- Keywords: {function_args['keywords']}\n"
        if "people" in function_args and function_args['people'] != "":
            output_msg += f"- People: {function_args['people']}\n"
        if "institutions" in function_args and function_args['institutions'] != "":
            output_msg += f"- Institutions: {function_args['institutions']}\n"
    return f"\n{output_msg}\n"

def user(txt, history):
    if history==None:
        history = []
    return [
      gr.Textbox.update(value="", interactive=False),
      history + ([(escape_text(txt), "")] if txt else []),
      gr.Button.update(interactive=False)]

def bot(history):
    for summary_chunk in ask_ChatGPT(history[-1][0]):
        if 'content' in summary_chunk['choices'][0]['delta']:
            history[-1][1] += str(summary_chunk['choices'][0]['delta']['content'])
            yield history
    history[-1][1] += write_article_metadata(history[-1][1])
    history[-1][1] = escape_text(history[-1][1])
    print(history[-1])
    yield history

def finish():
    return [gr.Textbox.update(value="", interactive=True), gr.Button.update(interactive=True)]

if __name__ == "__main__":
    with gr.Blocks(title="News Summarizer", css="style.css") as demo:
        chatbotComp = gr.Chatbot(
            elem_id="chatbot",
            show_label=False
        )
        textbox = gr.Textbox(
            elem_id="textbox",
            placeholder="Copy your article here",
            label="Input",
            interactive=True
        )
        sendbtn = gr.Button(
            elem_id="sendbtn",
            variant="primary",
            value="SEND",
            interactive=True
        ).style(size="lg")
        textbox\
            .submit(user,
                [textbox, chatbotComp],
                [textbox, chatbotComp, sendbtn])\
            .then(bot, chatbotComp, chatbotComp)\
            .then(finish, [], [textbox, sendbtn])
        sendbtn\
            .click(user,
                [textbox, chatbotComp],
                [textbox, chatbotComp, sendbtn])\
            .then(bot, chatbotComp, chatbotComp)\
            .then(finish, [], [textbox, sendbtn])

        demo.queue(concurrency_count=5, api_open=False)
        demo.launch(
            #server_name="192.168.0.10",
            #server_port=7861
        )