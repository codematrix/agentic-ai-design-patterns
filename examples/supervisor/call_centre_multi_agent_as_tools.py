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

from examples.supervisor.call_centre_tools import CallCentreTools
from utils.message_history import MessageHistory

load_dotenv()

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
        self.state = CallCentre.States()         
        
        self.supervisor = Agent(
            model=open_ai_model,      
            tools=CallCentreTools(open_ai_model, self.state.usage).get_tools(),            
            result_retries=2,
                                     
            system_prompt=("""
                You're a call-centre supervisor. When you receive a user's prompt, decide the specialist that is best suited to handle the response. 
                
                You have the following specialists on your team:
                - general
                - technical support 
                - products/services
                - billing/accounts

                Instructions:
                1. Decide the specialist that is best suited to handle the response. 
                2. If you can't determine a suitable specialist, then assume a general specialist
                3. If the specialist is:
                    - general: Then respond as best as you can, even though it has noting to do with the call-centre.
                    - not general: Then use the appropriate tool to obtain the response as final. Do not amend to the tool's final response.
                """.strip()            
            )  
        )                             
                    
    async def ask_async(self, prompt: str, stream_parts: Callable[[str], None]) -> CallCentreResponse:
        result = await self.supervisor.run(
            prompt,
            message_history=self.state.history.get_all_messages(),
            usage=self.state.usage                
        )       
             
        final_response = ""
        async with self.supervisor.run_stream(
            prompt, 
            message_history=self.state.history.get_all_messages(),
            usage=self.state.usage 
        ) as result:
            async for chunk in stream_result_async(result):
                final_response += chunk
                stream_parts(chunk)
        
        self.state.history.assign(result.all_messages())
        self.state.history.append(TextPart(content=final_response))   
        
        # print()
        # print(self.state.history.to_json(indent=2))   

        return CallCentreResponse(     
            response=final_response,
            usage=self.state.usage
        )    
    
    def reset(self):
        self.initialize()
 

# Things to consider
# not sure why tools are being called twice 
# consider streaming the tools response however, need to worry about the double tool calling 
    
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
