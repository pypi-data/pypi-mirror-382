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


def load_config():
    """load config"""
    with importlib.resources.open_text("diglife", "config.yaml") as f:
        return yaml.safe_load(f)
    




logger = Log.logger

config = load_config()

app = FastAPI(
    title="LLM Service",
    description="Provides an OpenAI-compatible API for custom large language models.",
    version="1.0.1",
)

# --- Configure CORS ---
# ! Add this section !
# Define allowed origins. Be specific in production!
# Example: origins = ["http://localhost:3000", "https://your-frontend-domain.com"]
origins = [
    "*",  # Allows all origins (convenient for development, insecure for production)
    # Add the specific origin of your "别的调度" tool/frontend if known
    # e.g., "http://localhost:5173" for a typical Vite frontend dev server
    # e.g., "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the allowed origins
    allow_credentials=True,  # Allows cookies/authorization headers
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers (Content-Type, Authorization, etc.)
)
# --- End CORS Configuration ---


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

# config.get("similarity_cutoff", 0.5)

llm_model_name =os.getenv("llm_model_name") #config.get("llm_model_name", "gemini-2.5-flash-preview-05-20-nothinking")
llm_api_key = os.getenv("llm_api_key") #config.get("llm_api_key", None)
recommended_biographies_cache_max_leng = os.getenv("recommended_biographies_cache_max_leng",2) #config.get("recommended_biographies_cache_max_leng", 2)
recommended_biographies_cache_max_leng = int(recommended_biographies_cache_max_leng)
recommended_cache_max_leng = os.getenv("recommended_cache_max_leng",2) #config.get("recommended_cache_max_leng", 2)
recommended_cache_max_leng = int(recommended_cache_max_leng)
user_server_base_url = "http://182.92.107.224:7000"



ep = EmbeddingPool()
MCmanager = MemoryCardManager(model_name = llm_model_name,
                              api_key = llm_api_key)
bg = BiographyGenerate(model_name = llm_model_name,
                              api_key = llm_api_key)
da = DigitalAvatar(model_name = llm_model_name,
                              api_key = llm_api_key)


task_store: Dict[str, Dict[str, Any]] = {}
recommended_biographies_cache: Dict[str, Dict[str, Any]] = {}
recommended_figure_cache: Dict[str, Dict[str, Any]] = {}




@app.get("/")
async def root():
    """server run"""
    envs = {
        "MySQL_DB_HOST":os.getenv("MySQL_DB_HOST"),
        "MySQL_DB_USER":os.getenv("MySQL_DB_USER"),
        "MySQL_DB_PASSWORD":os.getenv("MySQL_DB_PASSWORD"),
        "MySQL_DB_NAME":os.getenv("MySQL_DB_NAME"),
        "MySQL_DB_Table_Name":os.getenv("MySQL_DB_Table_Name"),
        "host":os.getenv("host"),
        "port":os.getenv("port"),
        "similarity_top_k":os.getenv("similarity_top_k"),
        "similarity_cutoff":os.getenv("similarity_cutoff"),
        "collection_name":os.getenv("collection_name"),
        "api_key":os.getenv("api_key"),
        "model_name":os.getenv("model_name"),
        "llm_model_name":os.getenv("llm_model_name"),
        "llm_api_key":os.getenv("llm_api_key"),
        "recommended_biographies_cache_max_leng":os.getenv("recommended_biographies_cache_max_leng"),
        "recommended_cache_max_leng":os.getenv("recommended_cache_max_leng"),
        "get_avatar_desc_url":os.getenv("get_avatar_desc_url"),
        "get_memory_desc_url":os.getenv("get_memory_desc_url"),

    }

    return {"message": "LLM Service is running.",
            "envs":envs}


@app.post("/life_topic_score")
async def life_topic_score_server(request: LifeTopicScoreRequest):
    """
    Calculates the life topic score based on the provided parameters.
    S_list elements must be integers between 1 and 10.
    """
    logger.info("running life_topic_score")
    try:
        result = MemoryCardManager.get_score(
            S=request.S_list,
            total_score=request.total_score,
            epsilon=request.epsilon,
            K=request.K,
        )
        return {
            "message": "Life topic score calculated successfully",
            "result": int(result),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@app.post("/life_aggregate_scheduling_score")
async def life_aggregate_scheduling_score_server(request: ScoreRequest):
    """
    Calculates the life aggregate scheduling score based on the provided parameters.
    S_list: List of scores (as strings, will be converted to integers)
    K: Coefficient K (default 0.8)
    total_score: Total score to add (default 0)
    epsilon: Epsilon value (default 0.001)
    """
    logger.info("running life_aggregate_scheduling_score")
    try:
        result = MemoryCardManager.get_score(
            request.S_list,
            total_score=request.total_score,
            epsilon=request.epsilon,
            K=request.K,
        )
        return {
            "message": "life aggregate scheduling score successfully",
            "result": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@app.post("/memory_card/score")
async def score_from_memory_card_server(request: MemoryCardsRequest):
    """
    记忆卡片质量评分
    接收一个记忆卡片内容字符串，并返回其质量评分。
    """
    logger.info("running memory_card/score")
    results = await MCmanager.ascore_from_memory_card(memory_cards=request.memory_cards)

    return {"message": "memory card score successfully", "result": results}


@app.post("/memory_card/merge", response_model=MemoryCard, summary="记忆卡片合并")
async def memory_card_merge_server(request: MemoryCards) -> dict:
    logger.info("running memory_card_merge")
    memory_cards = request.model_dump()["memory_cards"]

    result = await MCmanager.amemory_card_merge(memory_cards=memory_cards)

    return MemoryCard(
        title=result.get("title"),
        content=result.get("content"),
        time=result.get("time"),
    )


@app.post(
    "/memory_card/polish", response_model=MemoryCard, summary="记忆卡片发布AI润色"
)
async def memory_card_polish_server(request: MemoryCard) -> dict:
    """
    记忆卡片发布AI润色接口。
    接收记忆卡片内容，并返回AI润色后的结果。
    """
    logger.info("running memory_card_polish")
    memory_card = request.model_dump()
    result = await MCmanager.amemory_card_polish(memory_card=memory_card)

    return MemoryCard(title=result.get("title"), content=result.get("content"), time="")


@app.post(
    "/memory_card/generate_by_text",
    response_model=MemoryCardsGenerate,
    summary="上传文件生成记忆卡片",
)
async def memory_card_generate_by_text_server(request: ChatHistoryOrText) -> dict:
    """
    # 0091 上传文件生成记忆卡片-memory_card_system_prompt
    # 0092 聊天历史生成记忆卡片-time_prompt
    """
    logger.info("running generate_by_text")
    # 假设 agenerate_memory_card 是一个异步函数，并且已经定义在其他地方
    chapters = await MCmanager.agenerate_memory_card_by_text(
        chat_history_str=request.text, weight=1000
    )

    return MemoryCardsGenerate(memory_cards=chapters)


@app.post(
    "/memory_card/generate",
    response_model=MemoryCardsGenerate,
    summary="聊天历史生成记忆卡片",
)
async def memory_card_generate_server(request: ChatHistoryOrText) -> dict:
    """
    # 0093 上传文件生成记忆卡片-memory_card_system_prompt
    # 0094 聊天历史生成记忆卡片-time_prompt
    """
    logger.info("running memory_card generate")
    # 假设 agenerate_memory_card 是一个异步函数，并且已经定义在其他地方
    chapters = await MCmanager.agenerate_memory_card(
        chat_history_str=request.text, weight=1000
    )
    print(chapters, "chapters")
    return MemoryCardsGenerate(memory_cards=chapters)


async def _generate_biography(task_id: str, request_data: BiographyRequest):
    """
    模拟一个耗时的传记生成过程。
    在真实场景中，这里会调用LLM或其他复杂的生成逻辑。
    """
    memory_cards = request_data.model_dump()["memory_cards"]
    try:
        task_store[task_id]["status"] = "PROCESSING"
        task_store[task_id]["progress"] = 0.1
        logger.info(f"Task {task_id}: Starting generation ")

        # 素材整理
        material = await bg.amaterial_generate(
            vitae=request_data.vitae, memory_cards=memory_cards
        )
        task_store[task_id]["progress"] = 0.2
        task_store[task_id]["material"] = material
        # 生成大纲
        outline = await bg.aoutline_generate(material)

        task_store[task_id]["progress"] = 0.3
        # TODO 1 传记生成完成以后做一个回调函数
        # TODO 2 生成传记标题
        task_store[task_id]["biography_title"] = "个人传记"
        task_store[task_id]["outline"] = outline

        # 生成传记简介
        brief = await bg.agener_biography_brief(outline)
        task_store[task_id]["biography_brief"] = brief

        task_store[task_id]["progress"] = 0.5
        biography_json = {}
        biography_name = []
        biography_place = []

        tasks = []
        for part, chapters in outline.items():
            for chapter in chapters:
                logger.info(
                    f"Creating task for chapter: {chapter.get('chapter_number')} {chapter.get('title')}"
                )
                tasks.append(
                    bg.awrite_chapter(
                        chapter,
                        master=request_data.user_name,
                        material=material,
                        outline=outline,
                    )
                )
        results = await asyncio.gather(*tasks, return_exceptions=False)

        for part, chapters in outline.items():
            biography_json[part] = []
            for chapter in chapters:
                chapter_number = chapter.get("chapter_number")
                for x in results:
                    if x.get("chapter_number") == chapter_number:
                        biography_json[part].append(x.get("article"))
                        biography_name += x.get("chapter_name")
                        biography_place += x.get("chapter_place")

        assert isinstance(biography_json, dict)
        assert isinstance(biography_name, list)
        assert isinstance(biography_place, list)

        biography_name = list(set(biography_name))
        biography_place = list(set(biography_place))
        task_store[task_id]["biography_json"] = biography_json
        task_store[task_id]["biography_name"] = biography_name
        task_store[task_id]["biography_place"] = biography_place
        task_store[task_id]["status"] = "COMPLETED"
        task_store[task_id]["progress"] = 1.0


        biography_callback_url_success = user_server_base_url + f'/api/inner/notifyBiographyStatus?generateTaskId={task_id}&status=1'
        await aget_(url = biography_callback_url_success)


    except Exception as e:
        task_store[task_id]["status"] = "FAILED"
        task_store[task_id]["error_message"] = str(e)
        task_store[task_id]["progress"] = 1.0
        logger.info(f"Task {task_id}: Generation failed with error: {e}")

        biography_callback_url_failed = user_server_base_url + f'/api/inner/notifyBiographyStatus?generateTaskId={task_id}&status=0'
        await aget_(url = biography_callback_url_failed)



@app.post(
    "/generate_biography", response_model=BiographyResult, summary="提交传记生成请求"
)
async def generate_biography(request: BiographyRequest):
    """
    提交一个传记生成请求。

    此接口会立即返回一个任务ID，客户端可以使用此ID查询生成进度和结果。
    实际的生成过程会在后台异步执行。
    """
    task_id = str(uuid.uuid4())
    task_store[task_id] = {
        "task_id": task_id,
        "status": "PENDING",
        "biography_title": None,
        "biography_brief": None,
        "biography_json": None,
        "biography_name": None,
        "biography_place": None,
        "error_message": None,
        "progress": 0.0,
        "request_data": request.model_dump(),  # 存储请求数据以备后续使用
    }

    asyncio.create_task(_generate_biography(task_id, request))

    return BiographyResult(task_id=task_id, status="PENDING", progress=0.0)


@app.get(
    "/get_biography_result/{task_id}",
    response_model=BiographyResult,
    summary="查询传记生成结果",
)
async def get_biography_result(task_id: str):
    """
    根据任务ID查询传记生成任务的状态和结果。
    """
    task_info = task_store.get(task_id)
    logger.info(task_id)
    if not task_info:
        raise HTTPException(
            status_code=404, detail=f"Task with ID '{task_id}' not found."
        )

    return BiographyResult(
        task_id=task_info["task_id"],
        status=task_info["status"],
        biography_title=task_info.get("biography_title", ""),
        biography_brief=task_info.get("biography_brief", ""),
        biography_json=task_info.get("biography_json", {}),
        biography_name=task_info.get("biography_name", []),
        biography_place=task_info.get("biography_place", []),
        error_message=task_info.get("error_message"),
        progress=task_info.get("progress", 0.0),
    )


# 免费版传记优化
@app.post("/generate_biography_free", summary="提交传记生成请求")
async def generate_biography(request: BiographyRequest):
    """
    提交一个传记生成请求。

    此接口会立即返回一个任务ID，客户端可以使用此ID查询生成进度和结果。
    实际的生成过程会在后台异步执行。
    """
    memory_cards = request.model_dump()["memory_cards"]
    result = await bg.agenerate_biography_free(
        user_name=request.user_name,
        memory_cards=memory_cards,
        vitae=request.vitae,
    )

    return {"title": result.get("title"), "content": result.get("content")}


# 推荐算法


@app.post(
    "/recommended/update",  # 推荐使用POST请求进行数据更新
    summary="更新或添加文本嵌入",
    description="将给定的文本内容与一个ID关联并更新到Embedding池中。",
    response_description="表示操作是否成功。",
)
def recommended_update(item: UpdateItem):
    """记忆卡片是0  传记是1
    记忆卡片是0
    记忆卡片上传的是记忆卡片的内容 str
    记忆卡片id
    0

    传记是1
    上传的是传记简介  str
    传记id
    1

    数字分身是2
    上传数字分身简介和性格描述  str
    数字分身id
    2
    """
    # TODO 需要一个反馈状态
    try:
        if item.type in [0, 1, 2]:  # 上传的是卡片
            ep.update(text=item.text, id=item.id, type=item.type)
        else:
            logger.error(f"Error updating EmbeddingPool for ID '{item.id}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update embedding for ID '{item.id}': {e}",
            )

        return {"status": "success", "message": f"ID '{item.id}' updated successfully."}

    except ValueError as e:  # 假设EmbeddingPool.update可能抛出ValueError
        logger.warning(f"Validation error during update: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating EmbeddingPool for ID '{item.id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update embedding for ID '{item.id}': {e}",
        )


@app.post("/recommended/delete", response_model=DeleteResponse, description="delete")
async def delete_server(request: DeleteRequest):

    logger.info("running delete_server")

    # TODO 需要一个反馈状态
    result = ep.delete(id=request.id)  # 包裹的内核函数

    ########
    return DeleteResponse(
        status="success",
    )




# async def aget_content_by_id(url = ""):
#     # url = url.format(user_profile_id = user_profile_id)
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url)
#             response.raise_for_status()  # 如果状态码是 4xx 或 5xx，会抛出 HTTPStatusError 异常
            
#             print(f"Status Code: {response.status_code}")
#             print(f"Response Body: {response.json()}") # 假设返回的是 JSON
#             return response.json()
#         except httpx.HTTPStatusError as e:
#             print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
#         except httpx.RequestError as e:
#             print(f"An error occurred while requesting {e.request.url!r}: {e}")
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
#     return None

async def aget_(url = ""):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # 如果状态码是 4xx 或 5xx，会抛出 HTTPStatusError 异常
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.json()}") # 假设返回的是 JSON
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    return None

@app.post(
    "/recommended/search_biographies_and_cards",
    summary="搜索传记和记忆卡片",
    description="搜索传记和记忆卡片",
    response_description="搜索结果列表。",
)
async def recommended_biographies_and_cards(query_item: QueryItem):
    """
        # result = [
        #     {
        #         "id": "1916693308020916225",  # 传记ID
        #         "type": 1,
        #         "order": 0,
        #     },
        #     {
        #         "id": "1962459564012359682",  # 卡片ID
        #         "type": 0,
        #         "order": 1,
        #     },
        #     {
        #         "id": "1916389315373727745",  # 传记ID
        #         "type": 1,
        #         "order": 2,
        #     },
        # ]

        {
        "text":"这是一个传记001",
        "id":"1916693308020916225",
        "type":1
    }
    {
        "text":"这是一个传记002",
        "id":"1916389315373727745",
        "type":1
    }
    {
        "text":"这是一个卡片001",
        "id":"1962459564012359682",
        "type":0
    }
    """
    try:
        # TODO 需要一个通过id 获取对应内容的接口
        # TODO 调用id 获得对应的用户简介 query_item.user_id


        user_profile_id_to_fetch = query_item.user_id
        # memory_info = await aget_content_by_id(user_profile_id_to_fetch,url = user_server_base_url + "/api/inner/getMemoryCards?userProfileId={user_profile_id}")
        memory_info = await aget_(url = user_server_base_url + f"/api/inner/getMemoryCards?userProfileId={user_profile_id_to_fetch}")
        # memory_info = await get_memorycards_by_id(user_profile_id_to_fetch)
        user_brief = '\n'.join([i.get('content') for i in memory_info['data']["memoryCards"][:4]])


        result = ep.search_bac(query=user_brief)

        if recommended_biographies_cache.get(query_item.user_id):
            clear_result = [
                i
                for i in result
                if i.get("id")
                not in recommended_biographies_cache.get(query_item.user_id)
            ]
        else:
            recommended_biographies_cache[query_item.user_id] = []
            clear_result = result

        recommended_biographies_cache[query_item.user_id] += [
            i.get("id") for i in result
        ]
        recommended_biographies_cache[query_item.user_id] = list(
            set(recommended_biographies_cache[query_item.user_id])
        )
        if (
            len(recommended_biographies_cache[query_item.user_id])
            > recommended_biographies_cache_max_leng
        ):
            recommended_biographies_cache[query_item.user_id] = []

        return {
            "status": "success",
            "result": clear_result,
            "query": query_item.user_id,
        }

    except Exception as e:
        logger.error(
            f"Error searching EmbeddingPool for query '{query_item.user_id}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {e}",
        )



@app.post(
    "/recommended/search_figure_person",
    description="搜索数字分身的",
)
async def recommended_figure_person(query_item: QueryItem):
    """

    """
    try:

        user_profile_id_to_fetch = query_item.user_id
        # avatar_info = await aget_avatar_desc_by_id(user_profile_id_to_fetch)
        # avatar_info = await aget_content_by_id(user_profile_id_to_fetch,url = user_server_base_url + "/api/inner/getAvatarDesc?userProfileId={user_profile_id}")
        avatar_info = await aget_(url = user_server_base_url + f"/api/inner/getAvatarDesc?userProfileId={user_profile_id_to_fetch}")
        print(avatar_info,'avatar_info')
        if avatar_info["code"] == 200:
            user_brief = avatar_info["data"].get("avatarDesc")
        else:
            user_brief = "这是一个简单的人"

        result = ep.search_figure_person(query=user_brief)  # 100+

        if recommended_figure_cache.get(query_item.user_id):
            # 不需要创建
            clear_result = [
                i
                for i in result
                if i.get("id") not in recommended_figure_cache.get(query_item.user_id)
            ]
        else:
            recommended_figure_cache[query_item.user_id] = []
            clear_result = result

        recommended_figure_cache[query_item.user_id] += [i.get("id") for i in result]
        recommended_figure_cache[query_item.user_id] = list(
            set(recommended_figure_cache[query_item.user_id])
        )
        if (
            len(recommended_figure_cache[query_item.user_id])
            > recommended_cache_max_leng
        ):
            recommended_figure_cache[query_item.user_id] = []
        return {
            "status": "success",
            "result": clear_result,
            "query": query_item.user_id,
        }

    except Exception as e:
        logger.error(
            f"Error searching EmbeddingPool for query '{query_item.user_id}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {e}",
        )


@app.post("/user_overview")
async def user_overview_server(request: UseroverviewRequests):
    """
    用户概述
    """
    logger.info("running user_overview_server")
    memory_cards = request.model_dump()["memory_cards"]
    result = await da.auser_overview(
        action = request.action,
        old_overview=request.old_overview, 
        memory_cards=memory_cards
    )  # 包裹的内核函数

    return {"overview": result}


@app.post("/user_relationship_extraction", description="用户关系提取")
async def user_relationship_extraction_server(
    request: UserRelationshipExtractionRequest,
):
    logger.info("running user_relationship_extraction_server")

    result = await da.auser_relationship_extraction(text=request.text)
    return {"relation": result}


@app.post(
    "/digital_avatar/brief", response_model=BriefResponse, description="数字分身介绍"
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


@app.post("/digital_avatar/personality_extraction")
async def digital_avatar_personality_extraction(request: AvatarXGRequests):
    """数字分身性格提取"""

    logger.info("running digital_avatar_desensitization")
    memory_cards = request.model_dump()["memory_cards"]
    result = await da.personality_extraction(memory_cards=memory_cards,action = request.action,old_character = request.old_character)
    return {"text": result}


@app.post("/digital_avatar/desensitization")
async def digital_avatar_desensitization(request: MemoryCards):
    """
    数字分身脱敏
    """
    logger.info("running digital_avatar_desensitization")
    memory_cards = request.model_dump()["memory_cards"]
    result = await da.desensitization(memory_cards=memory_cards)
    memory_cards = {"memory_cards": result}
    return MemoryCards(**memory_cards)


if __name__ == "__main__":
    # 这是一个标准的 Python 入口点惯用法
    # 当脚本直接运行时 (__name__ == "__main__")，这里的代码会被执行
    # 当通过 python -m YourPackageName 执行 __main__.py 时，__name__ 也是 "__main__"
    import argparse
    import uvicorn
    from .log import Log

    default = 8007

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        "port",
        metavar="PORT",
        type=int,
        nargs="?",  # 端口是可选的
        default=default,
        help=f"Specify alternate port [default: {default}]",
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        "--dev",
        action="store_true",  # 当存在 --dev 时，该值为 True
        help="Run in development mode (default).",
    )

    # 添加 --prod 选项
    group.add_argument(
        "--prod",
        action="store_true",  # 当存在 --prod 时，该值为 True
        help="Run in production mode.",
    )
    args = parser.parse_args()

    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"

    port = args.port
    if env == "dev":
        port += 100
        Log.reset_level("debug", env=env)
        reload = True
        app_import_string = f"{__package__}.server:app"  # <--- 关键修改：传递导入字符串
    elif env == "prod":
        Log.reset_level(
            "info", env=env
        )  # ['debug', 'info', 'warning', 'error', 'critical']
        reload = False
        app_import_string = app
    else:
        reload = False
        app_import_string = app

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app_import_string, host="0.0.0.0", port=port, reload=reload  # 启用热重载
    )
