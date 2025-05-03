import os
import json

from colorama import Fore, Style, init
from dotenv import load_dotenv
import openai
from pydantic import BaseModel

class ListeningLevels(BaseModel):
    level: str

from system_prompts import ACTOR_PROMPT
from system_prompts import GRADER_PROMPT

init(autoreset=True)

load_dotenv(dotenv_path=".env.local")

# Set your API key
api_key = os.environ.get("OPENAI_API_KEY") 

class ActiveListeningBot:
    """
    AI chat with two LLM's, an actor and a grader.
    """

    def __init__(self, streaming=False):

        # Initialize the actor_llm
        self.actor_llm = openai.OpenAI(api_key=api_key)
        self.grader_llm = openai.OpenAI(api_key=api_key)

        # Initialize chat
        self.grader_response_id = None
        self.actor_response_id = None
        self.grader_assessment = None
        self.prev_actor_message = None
        self.initialize_chat()

    def initialize_chat(self):

        print_color("Starting chat with OpenAI (type 'exit' to quit)", "black", bold=True)

        # Initialize the conversation for the grader.
        grader_response = self.grader_llm.responses.parse(
            model="gpt-4o",
            input=[{"role": "system", "content": GRADER_PROMPT}],
            text_format=ListeningLevels,
            )
        self.grader_response_id = grader_response.id
        grader_message = grader_response.output_text
        print_color(f"Grader:  {grader_message}", "magenta")

        # Initialize the conversation for the actor.
        actor_response = self.actor_llm.responses.create(
            model="gpt-3.5-turbo",
            input=[{"role": "system", "content": ACTOR_PROMPT}],
            # stream=True,
        )
        self.actor_response_id = actor_response.id
        actor_message = actor_response.output_text
        self.prev_actor_message = actor_message
        print_color(f"Actor: {actor_message}", "blue")

    def process_message(self, user_input):

        # Get user input
        # print_color(f"User: {user_input}", "green")

        # Get actor response
        actor_input = [{
            "role": "user",
            "content": (
                f"User: {user_input}"
            )
        }, {
            "role": "system",
            "content": "Remember to never ask the user questions. Only answer theirs depending on the level of depth in the conversation. Don't explicitly mention the level."
        }]
        if self.grader_assessment is not None:
            actor_input[0]["content"] += (
                "\n"
                f"LEVEL: {self.grader_assessment.level}\n"
                # f"LEVEL_DESCRIPTION: {grader_assessment["level_description"]}"
            )
        actor_response = self.actor_llm.responses.create(
            model="gpt-3.5-turbo",
            input=actor_input,
            stream=True,
            previous_response_id=self.actor_response_id,
        )
        self.actor_response_id = next(iter(actor_response)).response.id

        # # Feed the user message and the actor message into the grader.
        # grader_input = [{
        #     "role": "user",
        #     "content": (
        #         f"Actor: {self.prev_actor_message}\n"
        #         f"User: {user_input}\n"
        #         f"Note: Please provide your assessment in JSON format."
        #     ),
        # }]
        # grader_response = self.grader_llm.responses.parse(
        #     model="gpt-4o",
        #     input=grader_input,
        #     previous_response_id=self.grader_response_id,
        #     text_format=ListeningLevels,
        #     )
        # grader_message = grader_response.output_text
        # self.grader_response_id = grader_response.id
        # print_color(f"Grader: {grader_message}", "magenta")
        # self.grader_assessment = grader_response.output_parsed
        # # grader_assessment = json.loads(grader_message)  # convert raw text to json

        # self.prev_actor_message = actor_message
        return actor_response


def convert_stream_to_deltas(streaming_response):
    for event in streaming_response:
        event_type = getattr(event, 'type', '')

        if event_type == 'response.output_text.delta':
            delta = getattr(event, 'delta', '')
            yield delta


def get_full_output(streaming_response):
    """
    Extract the full output from a streaming response from chat completions.
    """
    for event in streaming_response:

        event_type = getattr(event, 'type', '')
        if event_type == 'response.output_text.done':
            full_output = getattr(event, 'text', '')
            return full_output


def chat_with_gpt():

    listening_llm = ActiveListeningBot()
    while True:

        # Get user input
        user_input = input(Fore.GREEN + "You: " + Style.RESET_ALL)
        if user_input.lower() == "exit":
            break

        # Produce actor response; this will print the actor's responding message.
        streaming_response = listening_llm.process_message(user_input)
        actor_message = get_full_output(streaming_response)
        print_color(f"Assistant: {actor_message}", "blue")


def print_color(text, color, bold=False):
    color_map = {
        "black": Fore.BLACK,
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW, 
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
    }
    
    color_code = color_map.get(color.lower(), Fore.RESET)
    style = Style.BRIGHT if bold else Style.NORMAL

    print(style + color_code + text + Style.RESET_ALL)   


# Uncomment the line below to run the interactive chat
if __name__ == "__main__":
    # chat_with_gpt()
    chat_with_gpt2()