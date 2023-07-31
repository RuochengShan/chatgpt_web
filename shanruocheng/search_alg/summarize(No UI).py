import openai
openai.organization = "YOUR ORGANIZATION ID FROM https://platform.openai.com/account/org-settings"
openai.api_key = "YOUR API KEY FROM https://platform.openai.com/account/api-keys"

def ask_bot_stream(prompt, stream=True):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": "You are a news article summarizer. You convert a news article into an English summary of a few bullet points. Then you give a bullet point of the article's keywords. Then you give separate bullet point lists of names of important people, countries, and instutions that the article focused on."},
        ],
        temperature=0,
        stream=stream
    )
    if stream:
        for chunk in response:
            if 'content' in chunk['choices'][0]['delta']:
                print(chunk['choices'][0]['delta']['content'], end='')
    else:
        print(response['choices'][0]['message']['content'])
