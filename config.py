import openai
import os
import uuid
from dotenv import load_dotenv

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


# 加载.env文件中的环境变量
load_dotenv()

llm_model_name = "gpt-3.5-turbo-16k"


openai.api_key = os.getenv("OPENAI_API_KEY")  # get it at https://platform.openai.com/
if os.getenv("OPENAI_API_BASE"):
    openai.api_base = os.getenv("OPENAI_API_BASE")
stability_api_key = os.getenv("STABILITY_API_KEY")  # get it at https://beta.dreamstudio.ai/
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")  # optional, if you don't add it, keep it as "YOUR ANTHROPIC API KEY"


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


# 生成32位唯一的uuid
def generate_uuid():
    # 生成UUID
    id = uuid.uuid4().hex
    return id


# 保存小说每章节的内容
def save_novel_chapter(novel_id, chapter_index, file_name, file_content):
    # 创建章节文件目录
    chapter_folder = os.path.join(os.getcwd(), f"story/{novel_id}/chapter_{chapter_index + 1}")
    if not os.path.exists(chapter_folder):
        os.makedirs(chapter_folder)

    # 写入章节内容到文件
    file_path = os.path.join(chapter_folder, f"{file_name}.txt")
    with open(file_path, "w") as file:
        file.write(file_content)