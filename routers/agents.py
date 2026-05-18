from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from dependencies import get_current_user
from models.user import User
from langchain_core.messages import HumanMessage
from agent.graph import agent_app
import json

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/chat")
async def chat(
    message: str,
    current_user: User = Depends(get_current_user)
):
    async def generate():
        async for event in agent_app.astream_events(
            {
                "messages": [HumanMessage(content=message)],
                "user_id": current_user.id
            },
            version="v2"
        ):
            event_type = event["event"]
            
            # 只捕获 LLM 流式输出的文字片段
            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                
                # 过滤掉工具调用，只推送文字内容
                if chunk.content and not chunk.tool_call_chunks:
                    data = json.dumps(
                        {"content": chunk.content},
                        ensure_ascii=False
                    )
                    yield f"data: {data}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )