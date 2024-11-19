
import chainlit as cl
from agents.agent_base import  SimpleAgent
from agents.agent_workpad import create_state_typed_dict
import logging
import os
from datetime import datetime

# Set up basic logging configuration
logging.basicConfig(level=logging.DEBUG)

# Inside the `start` function, where you set up session data
@cl.on_chat_start
async def start():
    # Initialize conversation history
    cl.user_session.set("conversation_history", [])

    # Load and set up system prompt with current timestamp
    try:
        prompt_path = os.path.join(
            os.path.dirname(__file__), 'jar3d_requirements_prompt.md'
        )
        with open(prompt_path, 'r', encoding='utf-8') as file:
            system_prompt = file.read()

        system_prompt += f"\n\n Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        logging.debug("System prompt loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading system prompt: {e}")
        return

    # Initialize agents
    try:
        llm = SimpleAgent(
            name="chat_model",
            server="openai",
            model="gpt-4o",
            temperature=0
        )

        chat_model = llm.get_llm()
        cl.user_session.set("chat_model", chat_model)
        cl.user_session.set("system_prompt", system_prompt)
        logging.debug("Agents initialized and added to session.")
    except Exception as e:
        logging.error(f"Error initializing agents: {e}")
        return

    # Send the initial message
    instructions = "/start"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instructions}
    ]

    try:
        jar3d_intro_hi = chat_model.invoke(messages)
        await cl.Message(content=jar3d_intro_hi, author="Jar3d👩‍💻").send()
    except Exception as e:
        logging.error(f"Error sending initial message: {e}")

@cl.on_message
async def main(message: cl.Message):
    # Retrieve session data
    chat_model = cl.user_session.get("chat_model")
    system_prompt = cl.user_session.get("system_prompt")
    conversation_history = cl.user_session.get("conversation_history", [])

    # Add logic to handle async processing
    conversation_history.append({"role": "user", "content": message.content})

    # Prepare message for the chat model
    messages = [
        {"role": "system", "content": system_prompt},
    ] + conversation_history

    try:
        chat_model_response =  chat_model.invoke(messages)
        await cl.Message(content=chat_model_response, author="Jar3d👩‍💻").send()

        conversation_history.append({"role": "assistant", "content": chat_model_response})
    except Exception as e:
        logging.error(f"Error interacting with chat model: {e}")
        return

    # Update the conversation history in the session
    cl.user_session.set("conversation_history", conversation_history)

    # Process specific commands like /end
    if message.content == "/end":

        # Add your handling of the /end command here...
        pass

