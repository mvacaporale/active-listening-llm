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
from utils import compose_stream

init(autoreset=True)

load_dotenv(dotenv_path=".env.local")

# Set your API key
api_key = os.environ.get("OPENAI_API_KEY") 

# Initialize the actor_llm
actor_llm = openai.OpenAI(api_key=api_key)
grader_llm = openai.OpenAI(api_key=api_key)

# For a more interactive experience, you can create a simple chat loop
def chat_with_gpt():
    print_color("Starting chat with OpenAI (type 'exit' to quit)", "black", bold=True)
    
    # Initialize the conversation for the grader.
    grader_response = grader_llm.responses.parse(
        model="gpt-4o",
        input=[{"role": "system", "content": GRADER_PROMPT}],
        text_format=ListeningLevels,
        )
    grader_response_id = grader_response.id
    grader_message = grader_response.output_text
    print_color(f"Grader:  {grader_message}", "magenta")

    # Initialize the conversation for the actor.
    actor_response = actor_llm.responses.create(
        model="gpt-3.5-turbo",
        input=[{"role": "system", "content": ACTOR_PROMPT}],
        # stream=True,
    )
    actor_response_id = actor_response.id
    actor_message = actor_response.output_text
    print_color(f"Actor: {actor_message}", "blue")

    # Initialize grader assessment.
    grader_assessment = None
    prev_actor_message = None

    while True:

        # Get user input
        user_input = input(Fore.GREEN + "You: " + Style.RESET_ALL)
        if user_input.lower() == "exit":
            break
            
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
        if grader_assessment is not None:
            actor_input[0]["content"] += (
                "\n"
                f"LEVEL: {grader_assessment.level}\n"
                # f"LEVEL_DESCRIPTION: {grader_assessment["level_description"]}"
            )
        prev_actor_message = actor_message
        actor_response = actor_llm.responses.create(
            model="gpt-3.5-turbo",
            input=actor_input,
            # stream=True,
            previous_response_id=actor_response_id,
        )
        actor_response_id = actor_response.id
        actor_message = actor_response.output_text

        # Feed the user message and the actor message into the grader.
        grader_input = [{
            "role": "user",
            "content": (
                f"Actor: {prev_actor_message}\n"
                f"User: {user_input}\n"
                f"Note: Please provide your assessment in JSON format."
            ),
        }]
        grader_response = grader_llm.responses.parse(
            model="gpt-4o",
            input=grader_input,
            previous_response_id=grader_response_id,
            text_format=ListeningLevels,
            )
        grader_message = grader_response.output_text
        grader_response_id = grader_response.id
        print_color(f"Grader: {grader_message}", "magenta")
        grader_assessment = grader_response.output_parsed
        # grader_assessment = json.loads(grader_message)  # convert raw text to json

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
    chat_with_gpt()