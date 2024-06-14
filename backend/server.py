from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
from typing_extensions import override
from openai import AssistantEventHandler

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI()
app = Flask(__name__)
@app.route('/get-question', methods=['POST'])
def get_question():
    try:
        assistant = client.beta.assistants.create(
          name="Interview Quiz",
          instructions="You are a quiz. You prompt me with a unique interview question each time to test my knowledge as a Senior DevOps engineer.",
          tools=[{"type": "code_interpreter"}],
          model="gpt-4-turbo",
        )

        thread = client.beta.threads.create()

        message = client.beta.threads.messages.create(
          thread_id=thread.id,
          role="user",
          content="Please prompt me with a question that I might encounter in a technical interview for a role as a Senior DevOps engineer. Please only repeat the same question once every 50 questions or so."
        )

        class EventHandler(AssistantEventHandler):
            def __init__(self):
                super().__init__()
                self.text_created = None
                self.full_text = ""  # Initialize to store the full response text
            
            @override
            def on_text_created(self, text) -> None:
                print(f"\nassistant > {text}", end="", flush=True)
              
            @override
            def on_text_delta(self, delta, snapshot):
                self.full_text += delta.value  # Append delta to the full text
                print(delta.value, end="", flush=True)
              
            def on_tool_call_created(self, tool_call):
                print(f"\nassistant > {tool_call.type}\n", flush=True)
          
            def on_tool_call_delta(self, delta, snapshot):
                if delta.type == 'code_interpreter':
                    if delta.code_interpreter.input:
                        print(delta.code_interpreter.input, end="", flush=True)
                    if delta.code_interpreter.outputs:
                        print(f"\n\noutput >", flush=True)
                        for output in delta.code_interpreter.outputs:
                            if output.type == "logs":
                                print(f"\n{output.logs}", flush=True)

        # Create an instance of the event handler
        event_handler = EventHandler()

        # Your existing code to stream the response
        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Please address the user as Lizzle. The user has a premium account.",
            event_handler=event_handler,
        ) as stream:
            stream.until_done()

        # question = 'hiii'

        return jsonify({'question': event_handler.full_text})

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)