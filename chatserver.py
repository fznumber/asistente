from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
from assistant import get_groq_assistant  # type: ignore


app = Flask(__name__)

@app.route("/", methods=["POST"])

# chatbot logic
def bot():

    llm_model = "mixtral-8x7b-32768"
    embeddings_model = "nomic-embed-text"
    rag_assistant = get_groq_assistant(llm_model=llm_model, embeddings_model=embeddings_model)
    
    # ffrom = request.values.get('From')
    user_msg = request.values.get('Body', '').lower()

    response = MessagingResponse()
    output = ""

    for delta in rag_assistant.run(user_msg):
        output += delta 

    # response.message(output)
    msg = response.message("")
    msg.media("https://static.vecteezy.com/system/resources/previews/019/843/301/original/kaspa-kas-coin-icon-isolated-on-white-background-vector.jpg")

    return str(response)


if __name__ == "__main__":
	app.run()

