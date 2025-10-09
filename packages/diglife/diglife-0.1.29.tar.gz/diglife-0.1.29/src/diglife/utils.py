"""
Author: 823042332@qq.com 823042332@qq.com
Date: 2025-08-28 09:07:54
LastEditors: 823042332@qq.com 823042332@qq.com
LastEditTime: 2025-09-03 13:56:45
FilePath: /prompt_writing_assistant/src/prompt_writing_assistant/unit.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""

import re
import importlib
import yaml
from diglife.log import Log

logger = Log.logger


def extract_json(text: str) -> str:
    """从文本中提取python代码
    Args:
        text (str): 输入的文本。
    Returns:
        str: 提取出的python文本
    """
    pattern = r"```json([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if matches:
        return matches[0].strip()  # 添加strip()去除首尾空白符
    else:
        return ""  # 返回空字符串或抛出异常，此处返回空字符串


def extract_article(text: str) -> str:
    """从文本中提取python代码
    Args:
        text (str): 输入的文本。
    Returns:
        str: 提取出的python文本
    """
    pattern = r"```article([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if matches:
        return matches[0].strip()  # 添加strip()去除首尾空白符
    else:
        return ""  # 返回空字符串或抛出异常，此处返回空字符串


def load_inpackage_file(package_name: str, file_name: str, file_type="yaml"):
    """load config"""
    with importlib.resources.open_text(package_name, file_name) as f:
        if file_type == "yaml":
            return yaml.safe_load(f)
        else:
            return f.read()


def super_print(s, target: str = "target"):
    print()
    print()
    print("==" * 21 + target + "==" * 21)
    print()
    print("==" * 50)
    print(type(s))
    print("==" * 50)
    print(s)
    print("==" * 50)
    print()


def super_log(s, target: str = "target"):
    logger.info("==" * 16 + target + "==" * 16)
    logger.info("")
    logger.info("")
    logger.info("==" * 40)
    logger.info(type(s))
    logger.info("==" * 40)
    logger.info(s)
    logger.info("==" * 40)
    logger.info("")
