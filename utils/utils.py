from langchain_openai import ChatOpenAI
import streamlit as st

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from utils.langgraph_utils import *

@st.cache_resource(ttl=720)
def initialize_llm(api_key):
    try:
        llm  = ChatOpenAI(api_key=api_key)

        #test llm
        llm.invoke('Hi')

        return True, llm
    
    except:
        return False,None
    

@st.cache_resource(ttl=300)
def build_graph():
    workflow= StateGraph(ScrapeMaster)

    #Define Nodes
    workflow.add_node("scrape_and_summerize_text",scrape_and_summerize_text)
    workflow.add_node("summerized_all_summaries",summerized_all_summaries)
    workflow.add_node("generate_draft_email",generate_draft_email)
    workflow.add_node("human_feedback_func",human_feedback_func)

    #Define Edges
    workflow.add_conditional_edges(START,scrape_summeries, ["scrape_and_summerize_text"])
    workflow.add_edge("scrape_and_summerize_text","summerized_all_summaries")
    workflow.add_edge("summerized_all_summaries","generate_draft_email")
    workflow.add_edge("generate_draft_email","human_feedback_func")
    workflow.add_conditional_edges("human_feedback_func",should_continue,["generate_draft_email",END])

    #Define memory
    thread_memory= MemorySaver()

    #Compile the workflow
    graph = workflow.compile(checkpointer=thread_memory,interrupt_before=['human_feedback_func'])

    return graph

    
