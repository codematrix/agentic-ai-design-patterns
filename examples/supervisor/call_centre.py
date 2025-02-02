# NOTES:
# TODO

from __future__ import annotations

import os
import asyncio
from enum import Enum
from typing import Optional
from rich.prompt import Prompt
from colorama import Fore
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.usage import Usage
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

load_dotenv()

open_ai_model = OpenAIModel("gpt-4o-mini")

class Route(Enum):
    Supervisor = 1
    BillingAccount = 2
    TechnicalSupport = 3
    ProductServices = 4
    
class CallCentreResponse(BaseModel):
    pass

class CallCentreState(BaseModel):
    prompt: Optional[str] = None
    usage: Usage = Usage()    

class CallCentre:
    class Supervisor(BaseNode[CallCentreState]):
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,      
                #result_type=CityDetailsResponse,                
                system_prompt=("""
                    You're an assistant that provides regional details about a city.

                    Expected Output:
                    - City: The city the user request
                    - Country: The country where the city resides
                    - Region: The region where the city resides
                    - Country_Capital: The capital city for the country
                    - Region_Capital: The capital city for the region
                """)
            ) 
        
        async def run(self, ctx: GraphRunContext[CallCentreState]) -> End[None]:            
            result = await self.agent.run(
                ctx.state.prompt,
                usage=ctx.state.usage                
            )            
            
            return End(None)
    
    class BillingAccounts(BaseNode[CallCentreState]):
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,   
                system_prompt="You're an assistant that provides history about a city."             
        )       
            
        async def run(self, ctx: GraphRunContext[CallCentreState]) -> CallCentre.Supervisor:
            result = await self.agent.run(
                ctx.state.prompt,
                usage=ctx.state.usage                
            )            
            
            return CallCentre.Supervisor()  


    class TechnicalSupport(BaseNode[CallCentreState]):
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,   
                system_prompt="You're an assistant that provides history about a city."             
        )       

        async def run(self, ctx: GraphRunContext[CallCentreState]) -> CallCentre.Supervisor:
            result = await self.agent.run(
                ctx.state.prompt,
                usage=ctx.state.usage                
            )            
            
            return CallCentre.Supervisor()  


    class ProductServices(BaseNode[CallCentreState]):
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,   
                system_prompt="You're an assistant that provides history about a city."             
        )       
        
        async def run(self, ctx: GraphRunContext[CallCentreState]) -> CallCentre.Supervisor:
            result = await self.agent.run(
                ctx.state.prompt,
                usage=ctx.state.usage                
            )            
            
            return CallCentre.Supervisor()  

    
    def __init__(self):
        self.reset_state()
        
        self.graph = Graph(nodes=[
            CallCentre.Supervisor, 
            CallCentre.BillingAccounts, 
            CallCentre.TechnicalSupport,
            CallCentre.ProductServices,
        ])                
        
    async def ask_async(self, prompt: str):
        self.state.prompt = prompt        
        await self.graph.run(CallCentre.Supervisor(), state=self.state)

        # TODO:
        # return CityDetailResponse(
        #     city_details=graphState.city_details if graphState.city_details else None,  
        #     summarized_history=graphState.summarized
        # )          
        
    def reset_state(self):
        self.state = CallCentreState()
    

async def main_async():
    Prompt.prompt_suffix = "> "    
    
    call_centre = CallCentreState()
                
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
                call_centre.reset_state()
                continue 
            
            
            try:                
                result = await call_centre.ask_async(prompt)
            #     if result.city_details.city is None:
            #         print(Fore.YELLOW + "Cannot find any city related details based on you query. Please provide a known city name.\n\n")
            #         continue              

            #     print(Fore.LIGHTCYAN_EX + result.city_details.model_dump_json(indent=2) + "\n")                                
            #     print(Fore.LIGHTGREEN_EX + result.summarized_history)
            #     print(Fore.RESET + "-" * 50)                            
                                
            except Exception as e:
                print(Fore.MAGENTA + f"Error: {e}")                

if __name__ == "__main__":
    os.system("cls")
    asyncio.run(main_async())
