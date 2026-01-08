import json
from pathlib import Path
from typing import Dict, Any, Optional

from astrbot.api import logger

class APIManager:
    def __init__(self,
                 # config: Dict[str, Any]
                 ):
        # self.config = config
        self.apis = self._init_apis()

    def _init_apis(self) -> Dict[str, Dict[str, Any]]:
        """初始化API配置"""
        # 读取JSON文件
        with open('data/plugins/astrbot_plugin_omniapi/plugin_apis.json', 'r', encoding='utf-8') as file:
            apis = json.load(file)
        return apis

    def get_system_config(self) -> Dict[str, Dict[str, Any]]:
        """获取系统配置"""
        # 读取JSON文件
        with open('data/config/astrbot_plugin_omniapi_config.json', 'r', encoding='utf-8-sig') as file:
            config = json.load(file)
        return config

    def get_ckey(self) -> str:
        """获取API的CKEY"""
        ckey = self.get_system_config().get("api_keys")
        return ckey

    def get_enable_text(self):
        """获取文本开关配置"""
        return self.get_system_config().get("enable_text")

    def get_enable_image(self):
        """获取图片开关配置"""
        return self.get_system_config().get("enable_image")

    def get_enable_voice(self):
        """获取语音开关配置"""
        return self.get_system_config().get("enable_audio")

    def get_enable_video(self):
        """获取视频开关配置"""
        return self.get_system_config().get("enable_video")


    def match_api_by_command(self, command: str) -> Optional[Dict[str, Any]]:
        """
        根据指令匹配API
        :param command: 指令
        :return: API配置，如果未匹配到返回None
        """
        for api_name, api_data in self.apis.items():
            if command in api_data["command"]:
                return api_data
        return None

    def get_api_by_name(self, api_name: str) -> Optional[Dict[str, Any]]:
        """
        根据API名称获取API配置
        :param api_name: API名称
        :return: API配置，如果未找到返回None
        """
        return self.apis.get(api_name)

    def get_all_apis(self) -> Dict[str, Dict[str, Any]]:
        """获取所有API配置"""
        return self.apis

    def update_api(self, api_name: str, api_config: Dict[str, Any]):
        """
        更新API配置
        :param api_name: API名称
        :param api_config: 新的API配置
        """
        self.apis[api_name] = api_config
        logger.info(f"API配置已更新: {api_name}")

    def add_api(self, api_config: Dict[str, Any]):
        """
        添加新API
        :param api_config: API配置
        """
        api_name = api_config.get("name")
        if api_name:
            self.apis[api_name] = api_config
            logger.info(f"API已添加: {api_name}")

    def remove_api(self, api_name: str):
        """
        删除API
        :param api_name: API名称
        """
        if api_name in self.apis:
            del self.apis[api_name]
            logger.info(f"API已删除: {api_name}")
