from fastapi import APIRouter, Depends

from schema.chatbot import ChatRequest, ChatResponse
from robo.chitti import chat_with_finance_agent
from auth import get_current_user


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    response = chat_with_finance_agent(
        input_message=request.message
    )

    return ChatResponse(
        response=response
    )