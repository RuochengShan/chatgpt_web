import gradio as gr
from revChatGPT.V3 import Chatbot
import time, secrets
# import hashlib

access_token = "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"
# auths_padding = ''
# auth_sha256_digests = []
user_info = {"lzy": "lzy0123"}


chatbot = None
debug = False

def parse_text(text):
    lines = text.split("\n")
    for i,line in enumerate(lines):
        if "```" in line:
            items = line.split('`')
            if items[-1]:
                lines[i] = f'<pre><code class="{items[-1]}">'
            else:
                lines[i] = f'</code></pre>'
        else:
            if i>0:
                lines[i] = '<br/>'+line.replace("<", "&lt;").replace(">", "&gt;")
    return "".join(lines)

def ask_bot_stream(prompt, convo_id):
    msg = ""
    if chatbot and not debug:
        for data in chatbot.ask_stream(prompt=prompt, convo_id=convo_id):
            if data == b'':
                continue
            yield data
    elif debug:
        for data in prompt.split():
            time.sleep(0.1)
            yield data + " "
    else:
        msg = "The chatbot is not set up properly! Try to login again."
        yield msg

def gettokencountstr(convo_id):
    if not chatbot:
        return ""
    if convo_id not in chatbot.conversation:
        return f".../{chatbot.max_tokens}"
    return f"{chatbot.get_token_count(convo_id=convo_id)}/{chatbot.max_tokens}"

def gettextboxlabelupd(tokencountStr):
    return gr.Textbox.update(label=(f"Input (Session Limit: {tokencountStr})" if tokencountStr else f"Input"))

with gr.Blocks(title="ChatGPT", css="style.css") as demo:
    chatbot = Chatbot(api_key=access_token, max_tokens=3000)
    chatbotComp = gr.Chatbot(elem_id="chatbot", show_label=False)
    def user(txt, history, convo):
        if history==None:
            history = []
        return ["",
            history + ([(parse_text(txt), "")] if txt else []),
            gr.Textbox.update(value=convo or secrets.token_hex(16), interactive=False)]\
            + [gr.Button.update(interactive=False)] * 2
    def bot(history, convo):
        tokencountStr = gettokencountstr(convo_id=convo)
        if len(history)<1 or history[-1][1] != "":
            yield gettextboxlabelupd(tokencountStr), history
            return
        for data in ask_bot_stream(history[-1][0], convo_id=convo):
            history[-1][1] += str(data)
            yield gettextboxlabelupd(tokencountStr), history
        history[-1][1] = parse_text(history[-1][1])
        tokencountStr = gettokencountstr(convo_id=convo)
        print(f"{convo}: {tokencountStr}")
        print(history)
        yield gettextboxlabelupd(tokencountStr), history
    def finish(history):
        return [gr.Textbox.update(interactive=True)] + [gr.Button.update(interactive=True)] * 2
    def reset(history, convo):
        if chatbot and not debug:
            chatbot.reset(convo_id=convo, system_prompt="You are ChatGPT, a large language model trained by OpenAI. Respond conversationally")
        return [], gr.Textbox.update(value=secrets.token_hex(16))

    textbox = gr.Textbox(elem_id="textbox", placeholder="Type your message here", label="Input", interactive=True)
    sendbtn = gr.Button(elem_id="sendbtn", variant="primary", value="SEND", interactive=True).style(size="lg")
    with gr.Row().style(equal_height=True):
        convoComp = gr.Textbox(placeholder="Enter your conversation ID here (leave it blank if you don't have one)", show_label=False)
        resetbtn = gr.Button("Reset conversation")

    textbox\
        .submit(user,
            [textbox, chatbotComp, convoComp],
            [textbox, chatbotComp, convoComp, sendbtn, resetbtn])\
        .then(bot, [chatbotComp, convoComp], [textbox, chatbotComp])\
        .then(finish, chatbotComp, [convoComp, sendbtn, resetbtn])
    sendbtn\
        .click(user,
            [textbox, chatbotComp, convoComp],
            [textbox, chatbotComp, convoComp, sendbtn, resetbtn])\
        .then(bot, [chatbotComp, convoComp], [textbox, chatbotComp])\
        .then(finish, chatbotComp, [convoComp, sendbtn, resetbtn])
    resetbtn\
        .click(reset, [chatbotComp, convoComp], [chatbotComp, convoComp])

    # def auth_sha256(username, password):
    #    return hashlib.sha256(f"{username}{auths_padding}{password}".encode('utf-8')).digest() in auth_sha256_digests

    def user_password(username, password):
        if not username in user_info:
            return False
        if user_info[username] == password:
            return True
        else:
            return False
    demo.queue(concurrency_count=5, api_open=False)
    demo.launch(
            server_name="0.0.0.0",
            auth=user_password
        )
