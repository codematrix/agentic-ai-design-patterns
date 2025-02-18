# NOTES:
# This is simple single agent using a mock Asana API to manage tasks and projects by means of Tools.
# This is a streamlit version of the console.py. 
# To run this in streamlit 
#   - navigate to the directory where this file is located  
#   - execute the following: streamlit run streamlit_ui.py

import os
import sys
import asyncio
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.messages import TextPart
from asana_tools import AsanaTools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from _utils.message_history import MessageHistory
from _utils.utils import Utils

load_dotenv()

tools = AsanaTools()

agent = Agent(
    model="openai:gpt-4o-mini",
    tools=tools.get_tools(),        
    system_prompt=(
        "You are a personal assistant to help manage project tasks. "
        "Anytime the user requests a list of projects or tasks, always retrieve it using tools. "
        f"The current date is: {datetime.now().date()}"
    )
)
        
async def main_async():
    st.title("Project/Task Manager")        
        
    if "messages" not in st.session_state:
        # load for a database            
        st.session_state.messages = MessageHistory()  
     
    # display all user and ai messages
    message_history = st.session_state.messages.get_all_messages()
    for message in message_history:
        for part in message.parts:
            if part.part_kind in ["user-prompt", "text"]:
                with st.chat_message("human" if part.part_kind == "user-prompt" else "ai"):
                    st.markdown(part.content)                
    
    if prompt := st.chat_input("What would you like research today?"):        
        st.chat_message("user").markdown(prompt)        
        
        # stream the ai response
        response_content = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()             
            async with agent.run_stream(prompt, message_history=message_history) as result:
                async for chunk in Utils.stream_result_async(result):
                    response_content += chunk
                    message_placeholder.markdown(response_content)    
                
            # update the latest history
            st.session_state.messages.assign(result.all_messages())
            st.session_state.messages.append(TextPart(content=response_content))            

if __name__ == "__main__":        
    asyncio.run(main_async())
