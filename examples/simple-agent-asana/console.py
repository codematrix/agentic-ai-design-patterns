# NOTES:
# This simple agent basically uses the Asana API to manage tasks and projects by means of Tools.

import os
import sys
from datetime import datetime
from colorama import Fore
from dotenv import load_dotenv
from rich.prompt import Prompt
from pydantic_ai import Agent
from pydantic_ai.result import StreamedRunResult
from pydantic_ai.messages import TextPart
from asana_tools import AsanaTools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from utils.message_history import MessageHistory

load_dotenv()

tools = AsanaTools()

async def stream_result_async(result: StreamedRunResult): 
    async for message in result.stream_text(delta=True):  
        yield message 


async def main_async():            
    agent = Agent(
        model="openai:gpt-4o-mini",
        tools=tools.get_tools(),        
        system_prompt=(
            "You are a personal assistant to help manage project tasks. "
            "Anytime the user requests a list of projects or tasks, always retrieve it using tools. "
            f"The current date is: {datetime.now().date()}"
        )
    )
    
    # load for a database
    message_history = MessageHistory()
    Prompt.prompt_suffix = "> "
     
    while True:
        print()
        if prompt := Prompt.ask(Fore.RESET):
            print()

            if prompt == "exit":
                break

            if prompt == "clear":
                os.system("cls")
                continue
            
            try:
                response_content = ""
                async with agent.run_stream(prompt, message_history=message_history.get_all_messages()) as result:
                    async for chunk in stream_result_async(result):
                        response_content += chunk
                        print(Fore.LIGHTGREEN_EX + chunk, end="")
                        
                print()
                            
                message_history.assign(result.all_messages())            
                message_history.append(TextPart(content=response_content))        
            except Exception as e:
                print(e)

if __name__ == "__main__":
    import asyncio
    os.system("cls")
    asyncio.run(main_async())
    
