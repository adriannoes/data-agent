"""Nodes for the LangGraph agent."""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.data_analysis import load_csv, get_summary, filter_data, get_column_info


# Global variable to store SSE events (simple in-memory store for MVP)
sse_events: Dict[str, list] = {}


def add_sse_event(session_id: str, event_type: str, data: Any):
    """Add an SSE event to the session's event queue."""
    if session_id not in sse_events:
        sse_events[session_id] = []
    
    sse_events[session_id].append({
        "type": event_type,
        "data": data
    })


def get_sse_events(session_id: str) -> list:
    """Get and clear SSE events for a session."""
    events = sse_events.get(session_id, [])
    sse_events[session_id] = []
    return events


def understand_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 1: Understand user intent from the message."""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])
    
    # Build context for understanding intent
    context = "You are a data analysis assistant. Analyze the user's message and determine:\n"
    context += "1. What data analysis they want to perform\n"
    context += "2. Which CSV files might be needed\n"
    context += "3. What operations to perform (summary, filter, specific analysis)\n\n"
    
    if conversation_history:
        context += "Previous conversation:\n"
        for msg in conversation_history[-3:]:  # Last 3 messages for context
            context += f"- {msg['role']}: {msg['content']}\n"
        context += "\n"
    
    context += f"User message: {user_message}\n\n"
    context += "Respond with a JSON object containing: intent (string), csv_file (string or null), operations (list of strings)"
    
    messages = [HumanMessage(content=context)]
    response = llm.invoke(messages)
    
    # Try to parse JSON from response
    try:
        intent_data = json.loads(response.content)
    except:
        # Fallback if not valid JSON
        intent_data = {
            "intent": response.content,
            "csv_file": None,
            "operations": []
        }
    
    add_sse_event(state["session_id"], "status", {"message": "Understanding your request..."})
    
    state["intent"] = intent_data
    return state


def process_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 2: Process data using analysis tools."""
    intent = state.get("intent", {})
    csv_file = intent.get("csv_file")
    operations = intent.get("operations", [])
    
    if not csv_file:
        # Try to find CSV files in data directory
        data_dir = Path(__file__).parent.parent / "data"
        csv_files = list(data_dir.glob("*.csv"))
        
        if csv_files:
            csv_file = csv_files[0].name
            add_sse_event(state["session_id"], "status", {"message": f"Using available file: {csv_file}"})
        else:
            state["analysis_result"] = {"error": "No CSV file specified and no CSV files found in data directory"}
            return state
    
    # Load CSV
    data_dir = Path(__file__).parent.parent / "data"
    csv_path = data_dir / csv_file
    
    try:
        df = load_csv(str(csv_path))
        add_sse_event(state["session_id"], "status", {"message": f"Loaded {csv_file} with {len(df)} rows"})
        
        results = {
            "file": csv_file,
            "rows": len(df),
            "columns": df.columns.tolist()
        }
        
        # Perform operations based on intent
        if "summary" in str(operations).lower() or "summarize" in state.get("user_message", "").lower():
            summary = get_summary(df)
            results["summary"] = summary
            add_sse_event(state["session_id"], "preview", {
                "html": f"<h2>Data Summary</h2><p>Rows: {summary['shape'][0]}, Columns: {summary['shape'][1]}</p><pre>{json.dumps(summary, indent=2)}</pre>"
            })
        
        if "filter" in str(operations).lower():
            # Simple filter example - can be enhanced
            results["filtered_sample"] = df.head(10).to_dict(orient="records")
            add_sse_event(state["session_id"], "preview", {
                "html": f"<h2>Sample Data</h2><pre>{json.dumps(results['filtered_sample'], indent=2)}</pre>"
            })
        
        # Default: show summary if no specific operation
        if not results.get("summary") and not results.get("filtered_sample"):
            summary = get_summary(df)
            results["summary"] = summary
            sample = df.head(5).to_dict(orient="records")
            results["sample"] = sample
            
            html_content = f"""
            <div style="padding: 20px; font-family: Arial, sans-serif;">
                <h2>Data Analysis: {csv_file}</h2>
                <p><strong>Shape:</strong> {summary['shape'][0]} rows × {summary['shape'][1]} columns</p>
                <h3>Columns:</h3>
                <ul>
                    {''.join([f'<li>{col}</li>' for col in summary['columns']])}
                </ul>
                <h3>Sample Data:</h3>
                <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">
{json.dumps(sample, indent=2)}
                </pre>
            </div>
            """
            add_sse_event(state["session_id"], "preview", {"html": html_content})
        
        state["analysis_result"] = results
        state["dataframe"] = df  # Store for potential further processing
        
    except Exception as e:
        state["analysis_result"] = {"error": str(e)}
        add_sse_event(state["session_id"], "error", {"message": f"Error processing data: {str(e)}"})
    
    return state


def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 3: Generate final response for the user."""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    user_message = state.get("user_message", "")
    intent = state.get("intent", {})
    analysis_result = state.get("analysis_result", {})
    
    # Build response context
    context = f"User asked: {user_message}\n\n"
    context += f"Intent identified: {intent.get('intent', 'N/A')}\n\n"
    
    if "error" in analysis_result:
        context += f"Error occurred: {analysis_result['error']}\n"
        context += "Provide a helpful error message to the user."
    else:
        context += f"Analysis completed successfully:\n"
        context += f"- File: {analysis_result.get('file', 'N/A')}\n"
        context += f"- Rows processed: {analysis_result.get('rows', 0)}\n"
        context += f"- Columns: {', '.join(analysis_result.get('columns', []))}\n\n"
        context += "Provide a clear, concise summary of the analysis results in Portuguese."
    
    messages = [HumanMessage(content=context)]
    response = llm.invoke(messages)
    
    final_response = response.content
    
    add_sse_event(state["session_id"], "complete", {"message": "Analysis complete"})
    
    state["response"] = final_response
    return state

