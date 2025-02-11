# NOTES:
# TODO: ???

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

from utils.message_history import MessageHistory

load_dotenv()

open_ai_model = OpenAIModel("gpt-4o-mini")

class Specialist(Enum):
    General = "general"
    Billing = "billing"
    Account = "account"
    Products = "products"
    Services = "services"
    Technical = "technical"   

class CallCentreResponse(BaseModel):
    specialist: Specialist = Field(default=Specialist.General)
    response: str | None = Field(default=None)
    usage: Usage | None = Field(default=None)    
    
class CallCentre:
    class GraphState(BaseModel):
        prompt: Optional[str] = None
        specialist: Specialist = Field(default=Specialist.General)
        response: CallCentreResponse = None
        history: MessageHistory = MessageHistory()
        usage: Usage = Usage()              
        class Config:
            arbitrary_types_allowed = True          
        
    class Supervisor(BaseNode[GraphState]):
        class Response(BaseModel):
            specialist: Specialist = Specialist.General
            general_response: Optional[str] = None        
        
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,      
                result_type=CallCentre.Supervisor.Response,               
                system_prompt=("""
                    You're a customer service rep that works for a company that sells Cell Phone products and services. Analyze the user's input and select the most appropriate support team from these options: 
                    - Billing
                    - Account
                    - Products
                    - Services
                    - Technical

                    Instructions:
                    1. Use the user's input to determine the most appropriate support team
                    2. If a team cannot be determined, then assume a General query
                    3. The Expected Output Team property can be one of the supported teams or General if a team cannot be determined.
                    4. If General was selected then use the user's original input and provide a response, even though it has nothing to do with the company's products or services.

                    Expected Output: 
                    - Team: The chosen support team or General if no team can handle the response
                    - General Response: Only use this for the model's general response if only General was selected
                """)
            ) 
              
        async def run(self, ctx: GraphRunContext[CallCentre.GraphState]) -> \
            CallCentre.BillingAccountSpecialist | \
            CallCentre.ProductServiceSpecialist | \
            CallCentre.TechnicalSupportSpecialist | \
            End[CallCentreResponse]:  

            if ctx.state.response is None:                    
                result = await self.agent.run(
                    ctx.state.prompt,
                    message_history=ctx.state.history.get_all_messages(),
                    usage=ctx.state.usage                
                )
                
                ctx.state.history.assign(result.all_messages()).remove_part_kind("system-prompt")
                ctx.state.specialist = result.data.specialist                                                                                              
                        
                match result.data.specialist:
                    case Specialist.Account | Specialist.Billing:
                        return CallCentre.BillingAccountSpecialist()
                
                    case Specialist.Products | Specialist.Services:
                        return CallCentre.ProductServiceSpecialist()
                
                    case Specialist.Technical:
                        return CallCentre.TechnicalSupportSpecialist()
            
                # general response
                ctx.state.response = CallCentreResponse(
                    specialist=result.data.specialist, 
                    response=result.data.general_response, 
                    usage=ctx.state.usage
                )
        
            print(Fore.LIGHTGREEN_EX + ctx.state.history.to_json(indent=2))
            return End(ctx.state.response )
    
    class BillingAccountSpecialist(BaseNode[GraphState]):
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,   
                system_prompt="""
                    You are a billing and account support specialist. Follow these guidelines:
                    
                    1. First acknowledge the specific billing issue
                    2. Explain any charges or discrepancies clearly
                    3. List concrete next steps with timeline
                    4. End with payment options if relevant
                """          
        )       
            
        async def run(self, ctx: GraphRunContext[CallCentre.GraphState]) -> CallCentre.Supervisor:            
            result = await self.agent.run(
                ctx.state.prompt,
                message_history=ctx.state.history.get_all_messages(),
                usage=ctx.state.usage                
            )            
            
            ctx.state.history.assign(result.all_messages()).remove_part_kind("system-prompt")
                        
            ctx.state.response = CallCentreResponse(
                specialist=ctx.state.specialist, 
                response=result.data,
                usage=ctx.state.usage
            )            
                             
            return CallCentre.Supervisor()  

    class TechnicalSupportSpecialist(BaseNode[GraphState]):
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,   
                system_prompt="""
                    You are a technical support specialist. Follow these guidelines:
                    
                    1. List exact steps to resolve the issue
                    2. Include system requirements if relevant
                    3. Provide workarounds for common problems
                    4. End with escalation path if needed
                    
                    Use clear, numbered steps and technical details.
                """                          
        )       

        async def run(self, ctx: GraphRunContext[CallCentre.GraphState]) -> CallCentre.Supervisor:
            result = await self.agent.run(
                ctx.state.prompt,
                message_history=ctx.state.history.get_all_messages(),
                usage=ctx.state.usage                
            )            
            
            ctx.state.history.assign(result.all_messages()).remove_part_kind("system-prompt")
            
            ctx.state.response = CallCentreResponse(
                specialist=ctx.state.specialist, 
                response=result.data,
                usage=ctx.state.usage
            )            
            
            return CallCentre.Supervisor()  

    class ProductServiceSpecialist(BaseNode[GraphState]):
        def __init__(self):
            self.agent = Agent(
                model=open_ai_model,   
                system_prompt="""
                    You are a product and services specialist. Follow these guidelines:
                                        
                    1. Focus on feature education and best practices
                    2. Include specific examples of usage
                    3. Link to relevant documentation sections
                    4. Suggest related features that might help
                    
                    Be educational and encouraging in tone.                
                """
            )       
        
        async def run(self, ctx: GraphRunContext[CallCentre.GraphState]) -> CallCentre.Supervisor:
            result = await self.agent.run(
                ctx.state.prompt,
                message_history=ctx.state.history.get_all_messages(),
                usage=ctx.state.usage                
            )            
            
            ctx.state.history.assign(result.all_messages()).remove_part_kind("system-prompt")
            
            ctx.state.response = CallCentreResponse(
                specialist=ctx.state.specialist, 
                response=result.data,
                usage=ctx.state.usage
            )            
              
            return CallCentre.Supervisor()  
    
    def __init__(self):
        self.reset_state()
        
        self.graph = Graph(nodes=[
            CallCentre.Supervisor, 
            CallCentre.BillingAccountSpecialist, 
            CallCentre.TechnicalSupportSpecialist,
            CallCentre.ProductServiceSpecialist,
        ])                
        
    async def ask_async(self, prompt: str) -> CallCentreResponse:
        self.state.prompt = prompt 
        self.state.response = None
               
        await self.graph.run(CallCentre.Supervisor(), state=self.state)
        return self.state.response

    def reset_state(self):
        self.state = CallCentre.GraphState()
    

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
                call_centre.reset_state()
                continue 
            
            try:                
                result = await call_centre.ask_async(prompt)                
                
                print(Fore.LIGHTCYAN_EX + result.specialist.name)
                print(Fore.LIGHTCYAN_EX + result.response)                                
                                
            except Exception as e:
                print(Fore.MAGENTA + f"Error: {e}")
            finally:
                print(Fore.RESET)                

if __name__ == "__main__":
    os.system("cls")
    asyncio.run(main_async())
