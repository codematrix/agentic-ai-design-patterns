# NOTE:
# - This section defines call-centre specialists as tools to be utilized by the anonymous call-centre supervisor agent.
# - Pydantic AI tools offer multiple flavors for defining tools: `plan` (decorator), `context` (decorator), and `tool definition`. See the documentation: https://ai.pydantic.dev/tools/
# - For this example, I opted for the `tool definition` flavor because it is loosely coupled to the agent until runtime.
#   This approach ensures flexibility, allowing these tools to be reusable by various anonymous call-centre supervisor agents

from typing import List
from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.tools import Tool
from pydantic_ai.usage import Usage

class CallCentreToolStates:
    model: Model
    usage: Usage
    
    def __init__(self, model: Model, usage: Usage):
        self.model = model
        self.usage = usage    

class CallCentreTools:
    def __init__(self, states: CallCentreToolStates):
        self.__tools__ : List[Tool] = []    
        self.__states__ = states
        
        self.billing_account_agent = Agent(
            model=states.model,   
            system_prompt="""
                You are a billing and account support specialist. Follow these guidelines:
                
                1. First acknowledge the specific billing issue
                2. Explain any charges or discrepancies clearly
                3. List concrete next steps with timeline
                4. End with payment options if relevant
            """          
        )
        
        self.technical_support_agent = Agent(
            model=states.model,
            system_prompt="""
                You are a technical support specialist. Follow these guidelines:
                
                1. List exact steps to resolve the issue
                2. Include system requirements if relevant
                3. Provide workarounds for common problems
                4. End with escalation path if needed
                
                Use clear, numbered steps and technical details.
            """
        )              
        
        self.product_service_agent = Agent(
            model=states.model,
            system_prompt="""
                You are a product and services specialist. Follow these guidelines:
                                    
                1. Focus on feature education and best practices
                2. Include specific examples of usage
                3. Link to relevant documentation sections
                4. Suggest related features that might help
                
                Be educational and encouraging in tone.                
            """
        )                   

        # add our call centre specialists 
        self.__tools__.append(Tool(name = "technical_support_specialist", function = self.technical_support_specialist, description="Specialist to handle technical support enquiries"))
        self.__tools__.append(Tool(name = "billing_account_specialist", function = self.billing_account_specialist, description="Specialist to handle billing and/or account enquiries"))
        self.__tools__.append(Tool(name = "product_service_specialist", function = self.product_service_specialist, description="Specialist to handle product and/or service enquiries"))

    #----------------------#
    #      SPECIALISTS     #
    #----------------------#

    async def technical_support_specialist(self, user_prompt: str) -> str:
        """
        Technical Support Specialist that handles technical support issues.
        Use this tool to provide the user the final response if the concern is technical in nature.

        Example call: technical_support_specialist("I'm having issues with my cell phone.")
        
        Args:
            user_prompt (str): The user's prompt.
        Returns:
            response: str
        """

        result = await self.technical_support_agent.run(
            user_prompt=user_prompt,
            usage=self.__states__.usage
        )
        
        return result.data
    
    async def billing_account_specialist(self, user_prompt: str) -> str:
        """
        Billing and accounts specialists that only handles billing and/or account questions.
        Use this tool to provide the user the final response if the concern is billing or account in nature.

        Example call: billing_account_specialist("My account is locked.")
        
        Args:
            user_prompt (str): The user's prompt.
        Returns:
            response: str
        """

        result = await self.billing_account_agent.run(
            user_prompt=user_prompt,
            usage=self.__states__.usage
        )
                
        return result.data
    
    async def product_service_specialist(self, user_prompt: str) -> str:
        """
        Product and services specialists that only handles product and/or service questions.
        Use this tool to provide the user the final response if the concern is product or services in nature.

        Example call: product_service_specialist("I like to know more about you latest cell phones.")
        
        Args:
            user_prompt (str): The user's prompt.
        Returns:
            response: str
        """

        result = await self.product_service_agent.run(
            user_prompt=user_prompt,
            usage=self.__states__.usage
        )
        
        return result.data        

    def get_tools(self) -> List[Tool]:
        return self.__tools__
