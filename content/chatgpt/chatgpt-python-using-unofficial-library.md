Title: ChatGPT Python: using an unofficial library
Date: 2023-01-12 22:44
Author: Sam Stoelinga
Category: ChatGPT
Tags: chatgpt, python
Slug: chatgpt-python-using-an-unofficial-library


<iframe width="560" height="315" src="https://www.youtube.com/embed/Im6mh2ZFWx8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

ChatGPT at the time of writing this blog does not have an official API nor
libraries published. Luckily, many folks have inspected the API calls made
when using the ChatGPT web UI and created unofficial Python clients.

This blog post, will show you how to use the unofficial chatGPT python library
by [acheong08](https://github.com/acheong08/ChatGPT).

The blog post contains the following sections:

1. Installing ChatGPT python library
2. Configuring authentication
3. Creating a small Python application that uses the library

## 1. Installing the ChatGPT Python Library

Create a new directory named `chatgpt-python` and create a virtualenv in `.venv` directory:
```sh
mkdir chatgpt-python
cd chatgpt-python
python3 -m venv .venv
source .venv/bin/activate
```

Install revChatGPT using pip:
```sh
pip3 install --upgrade revChatGPT
```

## 2. Configuring authentication
The unofficial library requires a session token to authenticate to ChatGPT.

Here are the steps to get the session token:
1. Go to https://chat.openai.com and login with your OpenAI account
2. Open the Chrome Developer Tools e.g. by pressing Ctrl + Shift + I
3. Click on the application tab
4. Copy the value for the `__Secure-next-auth.session-token` cookie

You should now have the session token in your clipboard.

Create a file named `chatgpt.json` with the following content
(don't forget to paste your session token):
```json
{
  "session_token": "<COPY_PASTE_YOUR_SESSION_TOKEN_HERE>"
}
```

## 3. Using the ChatGPT python library
Create a chatbot instance:
```python
import json
from revChatGPT.ChatGPT import Chatbot

conf = json.load(open("chatgpt.json"))

chatbot = Chatbot(conf, conversation_id=None, parent_id=None)
```

Let's ask the ChatGPT something using Python:
```python
response = chatbot.ask("How to use ChatGPT using python")
print(response)
```

You should see something like this:
```
{
  'message': 'You can use the OpenAI Python SDK to interact with the ChatGPT model. Here is an example of how you might use the SDK to generate text using the model:\n\n1. First, you will need to install the SDK by running `pip install openai`.\n\n2. Next, you will need to import the `openai` module and set up an API key. You can get an API key from the OpenAI website.\n```\nimport openai\nopenai.api_key = "YOUR_API_KEY"\n```\n3. To generate text using the model, you can use the `openai.Completion.create()` function. \nThis function takes several parameters, including the `prompt` (the text you want the model to complete), the `model` (the name of the model you want to use), and the `max_tokens` (the maximum number of tokens the model should generate).\n```\nresponse = openai.Completion.create(\n    prompt=\'What is the meaning of\',\n    model=\'text-davinci-002\',\n    max_tokens=2048,\n)\nprint(response.choices[0].text)\n```\nThis will output the generated text from the model.\n\nYou can also use GPT-3 fine-tuning and retrain the model with your own dataset using Hugging face\'s transformers library.\n\nYou can also find more information on the OpenAI website, which has documentation and examples for using the SDK.\n',
  'conversation_id': '<SNIP>',
  'parent_id': '<SNIP>'
}
```
