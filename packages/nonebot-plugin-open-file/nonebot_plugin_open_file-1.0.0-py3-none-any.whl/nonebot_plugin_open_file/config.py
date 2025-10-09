from typing import Dict, List
from pydantic import BaseModel
from nonebot import get_plugin_config


class Config(BaseModel):
    
    # 管理员QQ号列表，只有这些用户可以使用文件打开功能
    file_opener_admins: List[str] = []
    
    # 关键词到文件路径的映射
    # 格式: {"关键词": "文件路径"}
    file_opener_keywords: Dict[str, str] = {}
    
    # 是否启用插件
    file_opener_enable: bool = True
    
    # 是否记录操作日志
    file_opener_log_enabled: bool = True


# 获取插件配置
plugin_config = get_plugin_config(Config)