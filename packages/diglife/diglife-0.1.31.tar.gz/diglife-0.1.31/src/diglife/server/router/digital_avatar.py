
from fastapi import APIRouter, Depends, HTTPException, status


from diglife.core import DigitalAvatar
from diglife.log import Log
logger = Log.logger

from ..models import BriefResponse, MemoryCards, AvatarXGRequests
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)

import os


llm_model_name =os.getenv("llm_model_name") #config.get("llm_model_name", "gemini-2.5-flash-preview-05-20-nothinking")
llm_api_key = os.getenv("llm_api_key") #config.get("llm_api_key", None)


da = DigitalAvatar(model_name = llm_model_name,
                              api_key = llm_api_key)

router = APIRouter(tags=["digital_avatar"])

@router.post(
    "/brief", response_model=BriefResponse, description="数字分身介绍"
)
async def brief_server(request: MemoryCards):
    logger.info("running brief_server")
    memory_cards = request.model_dump()["memory_cards"]
    result = await da.abrief(memory_cards=memory_cards)
    return BriefResponse(
        title=result.get("title"),
        content=result.get("content"),
        tags=result.get("tags")[:2],
    )


@router.post("/personality_extraction")
async def digital_avatar_personality_extraction(request: AvatarXGRequests):
    """数字分身性格提取"""

    logger.info("running digital_avatar_desensitization")
    memory_cards = request.model_dump()["memory_cards"]
    result = await da.personality_extraction(memory_cards=memory_cards,action = request.action,old_character = request.old_character)
    return {"text": result}


@router.post("/desensitization")
async def digital_avatar_desensitization(request: MemoryCards):
    """
    数字分身脱敏
    """
    logger.info("running digital_avatar_desensitization")
    memory_cards = request.model_dump()["memory_cards"]
    result = await da.desensitization(memory_cards=memory_cards)
    memory_cards = {"memory_cards": result}
    return MemoryCards(**memory_cards)
