import random
from typing import Dict, Any, Optional, List, Tuple
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Video, Plain, At, Record, Image
import httpx

from .astrbot_help_generator import generate_help_image
from .core.apiManager import APIManager
from .core.apiHandle import APIHandle

@register("astrbot_plugin_OmniAPI", "msyloveldx", "AstrBotOmniAPI 多模态娱乐，通过指令获取API的图片、文字、视频等内容并发送。",
          "v1.1.0")
class Main(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        self.config = config or {}
        self.api_manager = APIManager()
        self.api_handle = APIHandle()
        self.command_map: Dict[str, dict] = {}  # 命令到API配置的映射
        self.registered_commands: List[str] = []  # 已注册的命令列表

    async def initialize(self):
        """插件初始化方法"""
        logger.info("astrbot_plugin_OmniAPI 插件已初始化")
        # 加载并注册所有API命令
        await self.load_and_register_commands()
        logger.info(f"已注册指令: {', '.join(self.registered_commands)}")

    async def load_and_register_commands(self):
        """加载API配置并动态注册所有命令"""
        try:
            # 获取所有API配置
            apis = self.api_manager._init_apis()

            if not apis:
                logger.warning("未找到任何API配置")
                return

            # 清空现有映射
            self.command_map.clear()
            self.registered_commands.clear()

            # 遍历所有API配置
            for api_name, api_config in apis.items():
                # 检查是否有command字段
                commands = api_config.get("command", [])

                if not commands:
                    logger.warning(f"API '{api_name}' 未定义command字段，跳过注册")
                    continue

                # 为每个命令创建映射
                for cmd in commands:
                    cmd_clean = cmd.strip().lower()  # 清理命令，统一小写
                    if cmd_clean:
                        self.command_map[cmd_clean] = api_config
                        self.registered_commands.append(cmd_clean)
                        logger.debug(f"注册命令 '{cmd_clean}' -> API '{api_name}'")

            # 动态注册所有命令处理器
            await self.register_command_handlers()

            logger.info(f"成功加载 {len(self.command_map)} 个命令，来自 {len(apis)} 个API")

        except Exception as e:
            logger.error(f"加载API配置失败: {str(e)}", exc_info=True)

    async def register_command_handlers(self):
        """动态注册所有命令的处理器"""
        if not self.command_map:
            return

        # 接收所有的事件
        @filter.event_message_type(filter.EventMessageType.ALL)
        async def command_handler(event: AstrMessageEvent):
            # await self.handle_command(event)
            async for result in self.handle_command(event):
                yield result

    async def handle_command(self, event: AstrMessageEvent):
        """统一处理所有命令"""
        message_str = event.message_str.strip().lower()
        logger.debug(f"收到消息: '{message_str}'")

        # 精确匹配
        if message_str in self.command_map:
            api_config = self.command_map[message_str]
            logger.info(f"精确匹配指令: '{message_str}' -> API: {api_config.get('name', 'unknown')}")
            # await self.process_api_request(api_config, event)
            async for result in self.process_api_request(api_config, event):
                yield result
            return

        # 部分匹配（处理带参数的命令，如"did 123"）
        for cmd in self.registered_commands:
            if message_str.startswith(cmd + " ") or message_str.startswith(cmd + "，") or message_str.startswith(cmd + "-"):
                api_config = self.command_map[cmd]
                logger.info(
                    f"部分匹配指令: '{message_str}' -> 基础命令 '{cmd}' -> API: {api_config.get('name', 'unknown')}")
                # await self.process_api_request(api_config, event, message_str[len(cmd):].strip())
                async for result in self.process_api_request(api_config, event, message_str[len(cmd):].strip()):
                    yield result
                return

        # 未匹配到命令，不处理
        logger.debug(f"未匹配到任何命令: '{message_str}'")

    async def process_api_request(self, api_config: dict, event: AstrMessageEvent, params: str = ""):
        """处理API请求"""
        try:
            api_name = api_config.get("name", "unknown")
            video_type = api_config.get("videoType", "")
            image_type = api_config.get("imageType", "")
            type = api_config.get("type", "")

            logger.info(f"处理API请求: {api_name}, 类型: {video_type}")

            if not type:
                yield event.plain_result(f"API '{api_name}' 未配置type")
                return

            if api_config.get("type", "") == "video":
                # 根据视频类型处理
                if video_type == "video":
                    # await self.handle_video_type(api_config, event)
                    async for result in self.api_handle.handle_video_type(api_config, event):
                        yield result
                elif video_type == "url":
                    # await self.handle_url_type(api_config, event)
                    async for result in self.api_handle.handle_video_url_type(api_config, event):
                        yield result
                else:
                    yield event.plain_result(f"不支持的视频类型: {video_type}")

            elif api_config.get("type", "") == "image":
                if image_type == "image":
                    async for result in self.api_handle.handle_image_type(api_config, event):
                        yield result
                elif image_type == "url":
                    async for result in self.api_handle.handle_image_url_type(api_config, event):
                        yield result
                else:
                    yield event.plain_result(f"不支持的图片类型: {video_type}")

            elif api_config.get("type", "") == "text":
                async for result in self.api_handle.handle_text_type(api_config, event):
                    yield result

            elif api_config.get("type", "") == "audio":
                async for result in self.api_handle.handle_audio_type(api_config, event):
                    yield result
            else:
                yield event.plain_result(f"不支持的API类型: {api_config.get('type', '')}")

        except Exception as e:
            error_msg = f"处理API '{api_config.get('name', 'unknown')}' 失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            yield event.plain_result(f"❌ {error_msg}")



    @filter.command("4k壁纸")
    async def wallpaper_4k(self, event: AstrMessageEvent):
        """处理4k壁纸"""
        logger.info(f"收到指令{event.message_str}")

        url = "https://api.317ak.cn/api/tp/4kbz/4k"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        idList = [5,6,7,9,10,11,12,13,14,15,16,18,22,26,30,35,36]
        id_4k = random.choice(idList)
        params = {
            "ckey": "LCW4HP76R9LKRWXCEMAX",
            "count": "1",
            "id": f"{id_4k}",
            # "id": "36",
            "type": "json"
        }

        try:
            if not url:
                yield event.plain_result("API配置缺少url字段")
                return

            # 获取图片URL
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # ✅ 正确：直接 await get，不要 async with
                    resp = await client.get(url, headers=headers, params=params)
                    if resp.status_code != 200:
                        logger.error(f"图片下载失败，状态码: {resp.status_code}")

                    logger.info(resp.json())
                    image_url = resp.json()["data"][0]
            except Exception as e:
                logger.error(f"图片下载异常: {str(e)}")

            if not image_url:
                yield event.plain_result("获取图片URL失败")
                return

            # 发送视频URL
            chain = [
                At(qq=event.get_sender_id()),
                Plain(f"你的{resp.json()['tag']}请查收！"),
                Image.fromURL(url=str(image_url))
            ]
            yield event.chain_result(chain)
            logger.info(f"{resp.json()['tag']}发送成功: {image_url}")

        except Exception as e:
            logger.error(f"{resp.json()['tag']}处理失败: {str(e)}", exc_info=True)
            yield event.plain_result(f"❌ {resp.json()['tag']}处理失败: {str(e)}")

    @filter.command("help_cmd")
    async def help_command(self, event: AstrMessageEvent):
        """帮助命令，显示所有可用指令"""
        if not self.registered_commands:
            yield event.plain_result("暂无可用指令")
            return

        help_text = "🌟 可用指令:\n"
        help_text += "──────────────\n"

        # 按API分组显示命令
        api_commands = {}
        for cmd, api_config in self.command_map.items():
            api_name = api_config.get("name", "unknown")
            description = api_config.get("description", "")
            if api_name not in api_commands:
                api_commands[api_name] = []
            api_commands[api_name].append((cmd, description))

        for api_name, cmds_and_descs in api_commands.items():
            help_text += f"🎬 {api_name}:\n"
            for cmd, desc in cmds_and_descs:
                if desc:
                    help_text += f"  • {cmd} — {desc}\n"
                else:
                    help_text += f"  • {cmd}\n"

        help_text += "──────────────\n"
        help_text += "发送指令即可获取对应视频内容"
        # help_image = await self.text_to_image(help_text)
        # yield event.image_result(help_image)
        # yield event.plain_result(help_text)

        generate_help_image(help_text, "data/help_cmd.png")
        chain = [
            # At(qq=event.get_sender_id()),
            Image.fromFileSystem("data/help_cmd.png")
        ]
        yield event.chain_result(chain)