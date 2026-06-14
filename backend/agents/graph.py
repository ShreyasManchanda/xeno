from typing import TypedDict
from langgraph.graph import StateGraph, END

from agents.state import CampaignState


async def analyst_node(state: dict) -> dict:
    from agents.analyst import run_analyst
    from db.session import SessionLocal
    db = SessionLocal()
    try:
        result = await run_analyst(state, db)
        return result
    finally:
        db.close()


async def strategist_node(state: dict) -> dict:
    from agents.strategist import run_strategist
    from db.session import SessionLocal
    db = SessionLocal()
    try:
        result = await run_strategist(state, db)
        return result
    finally:
        db.close()


async def executor_node(state: dict) -> dict:
    from agents.executor import run_executor
    from db.session import SessionLocal
    db = SessionLocal()
    try:
        result = await run_executor(state, db)
        return result
    finally:
        db.close()


def build_graph():
    workflow = StateGraph(dict)
    
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("executor", executor_node)
    
    workflow.set_entry_point("analyst")
    
    workflow.add_edge("analyst", "strategist")
    workflow.add_edge("strategist", "executor")
    workflow.add_edge("executor", END)
    
    return workflow.compile()


graph = build_graph()
