"""LangGraph agent definition."""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict
from agent.nodes import understand_intent, process_data, generate_response


class AgentState(TypedDict):
    """State structure for the agent."""
    session_id: str
    user_message: str
    conversation_history: list
    intent: Dict[str, Any]
    analysis_result: Dict[str, Any]
    dataframe: Any
    response: str


def create_agent_graph():
    """Create and return the LangGraph agent."""
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("understand", understand_intent)
    workflow.add_node("process", process_data)
    workflow.add_node("respond", generate_response)
    
    # Define the flow
    workflow.set_entry_point("understand")
    workflow.add_edge("understand", "process")
    workflow.add_edge("process", "respond")
    workflow.add_edge("respond", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Create the agent instance
agent = create_agent_graph()

