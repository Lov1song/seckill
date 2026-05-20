from dotenv import load_dotenv
load_dotenv(override=True)

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Annotated
from agent.tools import search_products, get_seckill_activities, get_user_coupons, calculate_best_deal, set_price_alert, get_price_alerts
from agent.prompts import SYSTEM_PROMPT
import os


api_key = os.getenv("DASHSCOPE_API_KEY")
print(f"API Key: {api_key[:10]}...")  # 只打印前10位，安全起见

tools = [search_products,get_seckill_activities,get_seckill_activities,get_user_coupons,calculate_best_deal,set_price_alert,get_price_alerts]

llm = ChatOpenAI(
    model = "qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    streaming=True
)

llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: int

async def call_llm(state: AgentState) -> dict:
    system = SYSTEM_PROMPT + f"\n\n当前用户ID：{state['user_id']}，查询优惠券时直接使用此ID，无需询问用户。"
    messages = [SystemMessage(content=system)] + state["messages"]
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

def should_use_tool(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "use_tool"
    return "end"

tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("tools", tool_node)
graph.set_entry_point("llm")
graph.add_conditional_edges(
    "llm",
    should_use_tool,
    {
        "use_tool": "tools",
        "end": END
    }
)
graph.add_edge("tools", "llm")

agent_app = graph.compile()