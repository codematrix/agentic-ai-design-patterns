# NOTES:
# In this example we are using a supervisor multi-agent design pattern (non-graph) autonomously
# We have a supervisor that delegates requests to specialist via tools.
# Areas of improvements:#     
#   - Issue:
#       Streaming works great when the supervisor responses immediately for general responses. 
#       However, when a specialist is called via a tool, the response can be lengthy and is not streamed until the supervisor 
#       receives the response from the tool.
#   - Solution:
#       We can create our own stream (queue) and immediate return this to the caller to read stream 
#       from the pending response. This stream, can also be passed to the tools to enrich their response.
#       However, this will require a lot of ceremony and will over complicate the intent of this example. 


from __future__ import annotations

import os
import asyncio
from typing import Callable
from rich.prompt import Prompt
from colorama import Fore
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.messages import TextPart
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.usage import Usage
from call_centre_tools import CallCentreTools, CallCentreToolStates
from _utils.message_history import MessageHistory
from _utils.utils import Utils

load_dotenv()

open_ai_model = OpenAIModel("gpt-4o-mini")
        
class CallCentreResponse:    
    def __init__(self, response: str, usage: Usage):
        self.response = response        
        self.usage = usage             
    
class CallCentre:    
    class States:                
        history: MessageHistory = MessageHistory()
        usage: Usage = Usage()
        
    def __init__(self):
        self.initialize()
         
    def initialize(self):
        self.states = CallCentre.States()
        self.tool_states = CallCentreToolStates(open_ai_model, self.states.usage)         
        
        self.supervisor = Agent(
            model=open_ai_model,      
            tools=CallCentreTools(self.tool_states).get_tools(),             
            result_retries=1,                                     
            system_prompt=("""
                You're a call-centre supervisor. You have the following specialists on your team:                
                - technical support 
                - products/services
                - billing/accounts                                                                

                Instructions:                
                1. Decide which specialist is best suited to handle the user's prompt.
                2. If you can't determine a suitable specialist, then respond back in general friendly way.                
            """)  
        )                             
                    
    async def ask_async(self, prompt: str, stream_parts: Callable[[str], None]) -> CallCentreResponse:
        final_response = ""
        async with self.supervisor.run_stream(
            prompt, 
            message_history=self.states.history.get_all_messages(),
            usage=self.states.usage 
        ) as result:
            async for chunk in Utils.stream_result_async(result):
                final_response += chunk
                stream_parts(chunk)
        
        self.states.history.assign(result.all_messages())
        self.states.history.append(TextPart(content=final_response))   
        
        # print()
        # print(self.state.history.to_json(indent=2))   

        return CallCentreResponse(     
            response=final_response,            
            usage=self.states.usage
        )    
    
    def reset(self):
        self.initialize()
    
async def main_async():
    Prompt.prompt_suffix = "> "
    
    call_centre = CallCentre()
                
    while True:
        print(Fore.RESET)
        if prompt := Prompt.ask():
            print()

            if prompt == "exit":
                break
            
            if prompt == "clear":
                os.system("cls")
                continue 
            
            if prompt == "reset":
                os.system("cls")
                call_centre.reset()
                continue 
            
            try:                
                await call_centre.ask_async(
                    prompt,
                    lambda stream_part: (
                        print(Fore.LIGHTGREEN_EX + stream_part, end="")
                    )
                )                                

            except Exception as e:
                print(Fore.MAGENTA + f"Error: {e}")
            finally:
                print(Fore.RESET)                


# EXAMPLE QUERIES:
#   Hello
#   Who won the last stanley cup?
#   I'm having issues logging into my account
#   Who won the last cup again?
#   What was my last issue?
#   My phone turns off after 5 mins
#   Thanks
#   exit

if __name__ == "__main__":
    os.system("cls")
    asyncio.run(main_async())
