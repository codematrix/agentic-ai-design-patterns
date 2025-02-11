# NOTES:
# Prompt chaining is a technique where you can chain multiple prompts together to get a more detailed response.

from __future__ import annotations

import os
import asyncio
from typing import Optional
from rich.prompt import Prompt
from colorama import Fore
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.usage import Usage
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

load_dotenv()

open_ai_model = OpenAIModel("gpt-4o-mini")
groq_model_llama = GroqModel("llama-3.3-70b-versatile")
groq_model_mixtral = GroqModel("mixtral-8x7b-32768")

class CityDetailsResponse(BaseModel):
    city: Optional[str] = Field(default=None, description="The city yield from the prompt")
    country: Optional[str] = Field(default=None, description="The country where the city resides")
    region: Optional[str] = Field(default=None, description="The region where the city resides")    
    country_capital: Optional[str] = Field(default=None, description="The capital city for the country")
    region_capital: Optional[str] = Field(default=None, description="The capital city for the country")    
    
class CityDetailResponse(BaseModel):
    city_details: Optional[CityDetailsResponse] = None
    summarized_history: Optional[str] = None

class CityInsightsState(BaseModel):
    prompt: Optional[str] = None
    city_details: Optional[CityDetailsResponse] = None
    brief_history: Optional[str] = None
    summarized: Optional[str] = None
    usage: Usage = Usage()

class CityInsights:
    class CityDetails(BaseNode[CityInsightsState]):
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,      
                result_type=CityDetailsResponse,                
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
                
        async def run(self, ctx: GraphRunContext[CityInsightsState]) -> CityInsights.CityHistory | End[None]:
            capital_result = await self.agent.run(
                ctx.state.prompt,
                usage=ctx.state.usage                
            )            
            
            ctx.state.city_details = capital_result.data
        
            if ctx.state.city_details.city is None:
                return End(None)
            
            return CityInsights.CityHistory()  

    class CityHistory(BaseNode[CityInsightsState]):
        def __init__(self):
            self.agent = Agent(
                model=groq_model_llama,
                system_prompt="You're an assistant that provides history about a city."             
            )       
            
        async def run(self, ctx: GraphRunContext[CityInsightsState]) -> CityInsights.SummarizeResult:
            capital_history_result = await self.agent.run(
                f"Provide a brief history for the city '{ctx.state.city_details.city}'",
                usage=ctx.state.usage                
            )

            ctx.state.brief_history = capital_history_result.data         
                               
            return CityInsights.SummarizeResult()

    class SummarizeResult(BaseNode[CityInsightsState]):
        def __init__(self):
            self.agent = Agent(                
                model=groq_model_mixtral,
                system_prompt="You're an assistant that streamlines large text in a summarized way." 
            )
        
        async def run(self, ctx: GraphRunContext[CityInsightsState]) -> End[None]:
            summarized_result = await self.agent.run(
                f"Streamline and summarize this text: '{ctx.state.brief_history}'",
                usage=ctx.state.usage          
            )
            
            ctx.state.summarized = summarized_result.data
            
            return End(None)           
                
    def __init__(self):
        self.graph = Graph(nodes=[
            CityInsights.CityDetails, 
            CityInsights.CityHistory, 
            CityInsights.SummarizeResult
        ])
    
    async def get_details_async(self, prompt: str) -> CityDetailResponse:
        graphState = CityInsightsState()
        graphState.prompt = prompt
        
        await self.graph.run(CityInsights.CityDetails(), state=graphState)
        return CityDetailResponse(
            city_details=graphState.city_details if graphState.city_details else None,  
            summarized_history=graphState.summarized
        )   
        
async def main_async():
    Prompt.prompt_suffix = "> "    
    
    city_service = CityInsights()
                
    while True:
        print(Fore.RESET)
        if prompt := Prompt.ask():
            print()

            if prompt == "exit":
                break

            if prompt == "clear":
                os.system("cls")
                continue 
            
            try:                
                result = await city_service.get_details_async(prompt)
                if result.city_details.city is None:
                    print(Fore.YELLOW + "Cannot find any city related details based on you query. Please provide a known city name.\n\n")
                    continue              

                print(Fore.LIGHTCYAN_EX + result.city_details.model_dump_json(indent=2) + "\n")                                
                print(Fore.LIGHTGREEN_EX + result.summarized_history)
                print(Fore.RESET + "-" * 50)                            
                                
            except Exception as e:
                print(Fore.MAGENTA + f"Error: {e}")                
    
if __name__ == "__main__":
    os.system("cls")
    asyncio.run(main_async())
