# NOTES: ?????????????????????
# In this example we are using a supervisor multi-agent design pattern.
# We have a supervisor that delegates requests to specialist that can the user's query
# If specialist can handle the query, the supervisor will provide a general response back to the user
#
# Issuing with shared history across multi-agent using Pydantic Agents. The concern is system prompts, regardless of prompt type (static and/or dynamic).
# Scenario:
#  I have four agents used in call centre chat app: Supervisor, Technical Support Specialist, Billing/Account Specialist and Product/Services Specialist
#
#  Steps to repro: 
#  1. Supervisor agent setups a system prompt
#  2. Based on the query, the model will return which specialist can handle the user's prompt
#  3. The Supervisor routes to the Specialist
#  4. The Specialist has its own Agent and system prompt. However, the system prompt doesn't get applied because an existing system prompt (supervisor's) already exists.
#  5. Because the Specialist's system prompt doesn't get applied, the Specialist agent's model expectation fails.
#  
#  How I solved this was to remove the system prompt from the history, prior to calling the Specialist agent. 
#  Im OK with this as I'm not sure how we can solve this unless there's a way never to add system prompts to history, some sort of flag or something.


from __future__ import annotations

import os
import asyncio
# import logfire
from typing import Callable
from rich.prompt import Prompt
from colorama import Fore
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.result import StreamedRunResult
from pydantic_ai.messages import TextPart
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.usage import Usage

from examples.supervisor.call_centre_tools import CallCentreTools, CallCentreToolStates
from utils.message_history import MessageHistory

load_dotenv()
# logfire.configure()

open_ai_model = OpenAIModel("gpt-4o-mini")

async def stream_result_async(result: StreamedRunResult): 
    async for message in result.stream_text(delta=True):  
        yield message 
class CallCentreResponse:    
    def __init__(self, response: str, usage: Usage):
        self.response = response        
        self.usage = usage             
    
class CallCentre:    
    class States(BaseModel):                
        history: MessageHistory = MessageHistory()
        usage: Usage = Usage()
        class Config:
            arbitrary_types_allowed = True          
                
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
            async for chunk in stream_result_async(result):
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
 

# Things to consider
# consider streaming the tools response however
# if we get streaming working, we may want to update the graph version 
    
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
