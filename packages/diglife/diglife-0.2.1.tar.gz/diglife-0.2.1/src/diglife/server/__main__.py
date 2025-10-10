# server
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from diglife.core import MemoryCardManager
from diglife.core import DigitalAvatar
from diglife.log import Log
import os


from diglife.server.router.digital_avatar import router as avatar_router
from diglife.server.router.memory_card import router as memory_card_router
from diglife.server.router.recommended import router as recommended_router
from diglife.server.router.biography import router as biography_router
from dotenv import load_dotenv, find_dotenv

from .models import LifeTopicScoreRequest, ScoreRequest, UseroverviewRequests, UserRelationshipExtractionRequest

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)


logger = Log.logger


app = FastAPI(
    title="LLM Service",
    description="Provides an OpenAI-compatible API for custom large language models.",
    version="1.0.1",
)

# --- Configure CORS ---
origins = [
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the allowed origins
    allow_credentials=True,  # Allows cookies/authorization headers
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers (Content-Type, Authorization, etc.)
)
# --- End CORS Configuration ---



llm_model_name =os.getenv("llm_model_name")
llm_api_key = os.getenv("llm_api_key")


da = DigitalAvatar(model_name = llm_model_name,
                              api_key = llm_api_key)


app.include_router(avatar_router, prefix="/digital_avatar")
app.include_router(memory_card_router, prefix="/memory_card")
app.include_router(recommended_router, prefix="/recommended")
app.include_router(biography_router)


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


if __name__ == "__main__":
    # 这是一个标准的 Python 入口点惯用法
    # 当脚本直接运行时 (__name__ == "__main__")，这里的代码会被执行
    # 当通过 python -m YourPackageName 执行 __main__.py 时，__name__ 也是 "__main__"
    # 27
    import argparse
    import uvicorn
    from ..log import Log

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
        app_import_string = (
            f"{__package__}.__main__:app"  # <--- 关键修改：传递导入字符串
        )
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
