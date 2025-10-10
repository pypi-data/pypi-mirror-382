
# server
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator
from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from diglife.core import MemoryCardManager, BiographyGenerate
from diglife.core import DigitalAvatar
from diglife.embedding_pool import EmbeddingPool
from diglife.log import Log
import uuid
import asyncio
import httpx


from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)

import os




import importlib
import yaml


# class UseroverviewRequest(BaseModel):
#     old_overview: str
#     memory_cards: list[str]


# class UseroverviewResponse(BaseModel):
#     message: str
#     summary: str


class UserRelationshipExtractionRequest(BaseModel):
    text: str


# class UserRelationshipExtractionResponse(BaseModel):
#     message: str
#     output_relation: dict


class BriefResponse(BaseModel):
    title: str
    content: str
    tags: list[str]


# class digital_avatar_personalityResult(BaseModel):
#     """
#     传记生成结果的数据模型。
#     """

#     message: str = Field(..., description="优化好的记忆卡片")
#     text: str = Field(..., description="优化好的记忆卡片")


class DeleteRequest(BaseModel):
    id: str


class DeleteResponse(BaseModel):
    status: str = "success"  # 假设返回一个状态表示删除成功


class UpdateItem(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=2000, description="要更新的文本内容。"
    )
    id: str = Field(
        ..., min_length=1, max_length=100, description="与文本关联的唯一ID。"
    )
    type: int = Field(..., description="上传的类型")


class QueryItem(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=500, description="user_id")


class BiographyResult(BaseModel):
    """
    传记生成结果的数据模型。
    """

    task_id: str = Field(..., description="任务的唯一标识符。")
    status: str = Field(
        ...,
        description="任务的当前状态 (e.g., 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED').",
    )
    biography_title: Optional[str] = Field(None, description="传记标题")

    biography_brief: Optional[str] = Field(
        None, description="生成的传记简介，仅在状态为 'COMPLETED' 时存在。"
    )
    biography_json: dict | None = Field(
        None, description="生成的传记文本，仅在状态为 'COMPLETED' 时存在。"
    )
    biography_name: list[str] | None = Field(
        None, description="生成的传记文本中的人名，仅在状态为 'COMPLETED' 时存在。"
    )
    biography_place: list[str] | None = Field(
        None, description="生成的传记文本中的地名，仅在状态为 'COMPLETED' 时存在。"
    )
    error_message: Optional[str] = Field(
        None, description="错误信息，仅在状态为 'FAILED' 时存在。"
    )
    progress: float = Field(
        0.0, ge=0.0, le=1.0, description="任务处理进度，0.0到1.0之间。"
    )


# 记忆合并
class MemoryCardsRequest(BaseModel):
    memory_cards: list[str] = Field(..., description="记忆卡片列表")


# class MemoryCardsResult(BaseModel):
#     """
#     传记生成结果的数据模型。
#     """

#     message: str = Field(..., description="优化好的记忆卡片")
#     memory_cards: list[str] = Field(..., description="优化好的记忆卡片")


class LifeTopicScoreRequest(BaseModel):
    S_list: List[int] = Field(..., description="List of scores, each between 1 and 10.")
    K: float = Field(0.8, description="Weighting factor K.")
    total_score: int = Field(0, description="Initial total score.")
    epsilon: float = Field(0.001, description="Epsilon value for calculation.")

    @model_validator(mode="after")
    def validate_s_list(self):
        if not all(0 <= x <= 10 for x in self.S_list):
            raise ValueError(
                "All elements in 'S_list' must be integers between 1 and 10 (inclusive)."
            )
        return self


class ScoreRequest(BaseModel):
    S_list: List[float] = Field(
        ...,
        description="List of string representations of scores, each between 1 and 10.",
    )
    K: float = Field(0.3, description="Coefficient K for score calculation.")
    total_score: int = Field(0, description="Total score to be added.")
    epsilon: float = Field(0.0001, description="Epsilon value for score calculation.")

    @model_validator(mode="after")
    def check_s_list_values(self):
        for s_val in self.S_list:
            try:
                int_s_val = float(s_val)
                if not (0 <= int_s_val <= 100):
                    raise ValueError(
                        "Each element in 'S_list' must be an integer between 1 and 10."
                    )
            except ValueError:
                raise ValueError(
                    "Each element in 'S_list' must be a valid integer string."
                )
        return self

class MemoryCard(BaseModel):
    title: str
    content: str
    time: str


class MemoryCardGenerate(BaseModel):
    title: str
    content: str
    time: str
    score: int
    tag: str
    topic: int


class BiographyRequest(BaseModel):
    """
    请求传记生成的数据模型。
    """

    user_name: str = Field(None, description="用户名字")
    vitae: str = Field(None, description="用户简历")
    memory_cards: list[MemoryCard] = Field(..., description="记忆卡片列表")
    # 可以在这里添加更多用于生成传记的输入字段

class MemoryCards(BaseModel):
    memory_cards: list[MemoryCard] = Field(..., description="记忆卡片列表")


class MemoryCardsGenerate(BaseModel):
    memory_cards: list[MemoryCardGenerate] = Field(..., description="记忆卡片列表")


class UseroverviewRequests(BaseModel):
    action: str
    old_overview: str
    memory_cards: list[MemoryCard]


class AvatarXGRequests(BaseModel):
    action: str
    old_character: str
    memory_cards: list[MemoryCard]


# "memory_cards": ["我出生在东北辽宁葫芦岛下面的一个小村庄。小时候，那里的生活比较简单，人们日出而作，日落而息，生活节奏非常有规律，也非常美好。当时我们都是山里的野孩子，没有什么特别的兴趣爱好，就在山里各种疯跑。我小时候特别喜欢晚上看星星，那时的夜晚星星非常多，真的是那种突然就能看到漫天繁星的感觉。",
# "title": "初中时代的青涩与冲动",
#             "content": "我的初中生活是快乐的，尽管学校环境有些混乱，但我和朋友们在一起时总是很开心。与我玩得好的朋友大多学习成绩不太突出，而我那时也不是那种一心扑在学习上的人，我会和他们一起出去玩，一起疯。我们常常去县城的街上溜达，到处逛，打打闹闹。我印象最深刻的是初三那年，我们学校刚和另一所学校合并。当时正值青春期，学生们都比较躁动。有一次，在吃午饭的时候，我们班上一个和我关系很好的朋友，和另一个学校的人在打饭时发生了争执，随后演变成了一场两个班级之间的混战。我也加入了其中，我的头被不知道从哪里飞来的餐盘打中，当时鼓起了一个很大的包。我没有去看医生，只是鼓了一个包，当时比较皮，没那么脆弱，过两天就好了。这场混战导致我的那个朋友被他父母领回了沈阳，因为他家在沈阳，之前是把他放在老家上学。前段时间他结婚，邀请我去当伴郎，但我因为工作忙没有去成。现在回想起来，当时大家都还小，又是青春期，比较冲动。初中那段经历让我在之后很长一段时间里都比较意气用事，直到上大学的时候，我才慢慢意识到这个问题，并逐渐改了过来。现在，我面对问题时会更理智地去判断。",


class ChatHistoryOrText(BaseModel):
    text: str = Field(..., description="聊天内容或者文本内容")
