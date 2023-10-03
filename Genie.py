import streamlit as st

from langchain.llms import OpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.utilities import SerpAPIWrapper
from langchain.tools import Tool, StructuredTool
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from utils import get_worksheet
from task import Task, get_all_tasks_as_text, change_priority


#
# Tool functions
#
def add_task(description: str) -> str:
    t = Task(description=description)
    t.save()
    return f"Added new task to the list: {description}"


#
# Initialize the various smart components
#
sheet = get_worksheet()
llm = OpenAI(openai_api_key=st.secrets["openai_api_key"], temperature=0.3, streaming=True)
search = SerpAPIWrapper(serpapi_api_key=st.secrets["serpapi_api_key"])
agent_kwargs = {"extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],}
memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

#
# Initialize list of tools
#
tools = [
    StructuredTool.from_function(
        func=llm.predict,
        name="Ask the oracle",
        description="useful for when you don't know where to find the answer",
    ),
    StructuredTool.from_function(
        func=search.run,
        name="Search",
        description="useful for when you need to answer questions about current events or consult documentation for a given product",
    ),
    StructuredTool.from_function(
        func=get_all_tasks_as_text,
        name="Get all tasks",
        description="useful for when you need to get all the tasks in the tasklist with details about priority, deadline and task type"
    ),
    StructuredTool.from_function(
        func=add_task,
        name="Add new task",
        description="useful for when you need to add a new task to the tasklist, but only if the task does not exist already",
    ),
    StructuredTool.from_function(
        func=change_priority,
        name="change the priority of task",
        description="useful for when you need to change the priority of an existing task that is already in the tasklist. Do NOT add the task if it does not exist.",
    ),
]

#
# Langchain agent to tie it all together
#
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
)

#
# Streamlit chat interface
#
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(prompt, callbacks=[st_callback])
        st.write(response)
