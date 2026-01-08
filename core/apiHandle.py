"""各种类型api的处理"""
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger
from astrbot.api.message_components import Video, Plain, At, Record, Image
import os

from .request import RequestManager
from .apiManager import APIManager

class APIHandle:
    """API处理类"""
    def __init__(self):
        self.request = RequestManager()
        self.api_manager = APIManager()
        self.enable_text = self.api_manager.get_enable_text()
        self.enable_image = self.api_manager.get_enable_image()
        self.enable_audio = self.api_manager.get_enable_voice()
        self.enable_video = self.api_manager.get_enable_video()

    async def handle_text_type(self, api_config: dict, event: AstrMessageEvent):
        """处理text类型的API"""
        if self.enable_text == False:
            yield event.plain_result("暂未开启文本API功能")
            return

        logger.info(f"{api_config.get('name', '')}为text文本类型")

        try:
            # 获取URL和参数
            url = api_config.get("url", "").strip()
            headers = api_config.get("headers", {})
            params = api_config.get("params", {})

            if not url:
                yield event.plain_result("API配置缺少url字段")
                return

            text = await self.request.get_text(url, headers=headers, params=params)
            yield event.plain_result(text)

        except Exception as e:
            logger.error(f"处理{api_config.get('name', '')}text类型失败: {str(e)}", exc_info=True)
            yield event.plain_result(f"❌ {api_config.get('name', '')}文本处理失败: {str(e)}")


    async def handle_audio_type(self, api_config: dict, event: AstrMessageEvent):
        """处理audio类型的API"""
        if self.enable_audio == False:
            yield event.plain_result("暂未开启语音API功能")
            return

        logger.info(f"{api_config.get('name', '')}为audio语音类型")

        try:
            # 获取URL和参数
            name = api_config.get("name", "")
            url = api_config.get("url", "").strip()
            headers = api_config.get("headers", {})
            params = api_config.get("params", {})
            message_str = event.message_str
            role = message_str.split("-")[1]
            msg = message_str.split("-")[2]

            if not url:
                yield event.plain_result("API配置缺少url字段")
                return

            # 下载语音
            temp_path = await self.request.get_audio_url(url, headers=headers, params=params, role=role, msg=msg)
            if not temp_path or not os.path.exists(temp_path):
                yield event.plain_result(f"{api_config.get('name', '')}语音下载失败或文件不存在")
                return

            # 统一路径格式
            temp_path = temp_path.replace("\\", "/")

            # 发送视频
            chain = [
                At(qq=event.get_sender_id()),
                Plain(f"你的{api_config.get('name', '语音')}请查收！"),
                Record(file=temp_path),
            ]
            yield event.chain_result(chain)
            logger.info(f"{api_config.get('name', '')}语音发送成功: {temp_path}")

        except Exception as e:
            logger.error(f"处理{api_config.get('name', '')}audio类型失败: {str(e)}", exc_info=True)
            yield event.plain_result(f"❌ {api_config.get('name', '')}语音处理失败: {str(e)}")
        finally:
            # 清理临时文件
            if 'temp_path' in locals() and temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    logger.info(f"临时文件已删除: {temp_path}")
                except Exception as e:
                    logger.warning(f"删除临时文件失败: {str(e)}")


    async def handle_video_type(self, api_config: dict, event: AstrMessageEvent):
        """处理video类型的API"""
        if self.enable_video == False:
            yield event.plain_result("暂未开启视频API功能")
            return

        logger.info(f"{api_config.get('name', '')}为video视频类型，使用get_video函数下载")

        try:
            # 获取URL和参数
            name = api_config.get("name", "")
            url = api_config.get("url", "").strip()
            headers = api_config.get("headers", {})
            params = api_config.get("params", {})

            if not url:
                yield event.plain_result("API配置缺少url字段")
                return

            # 下载视频
            # if name == "随机视频":
            #     temp_path = await self.request.get_random_video(url, headers=headers, params=params)
            # else:
            temp_path = await self.request.get_video(url, headers=headers, params=params)
            if not temp_path or not os.path.exists(temp_path):
                yield event.plain_result(f"{api_config.get('name', '')}视频下载失败或文件不存在")
                return

            # 统一路径格式
            temp_path = temp_path.replace("\\", "/")

            # 发送视频
            chain = [
                At(qq=event.get_sender_id()),
                Plain(f"你的{api_config.get('name', '视频')}请查收！"),
                Video.fromFileSystem(path=str(temp_path)),
            ]
            yield event.chain_result(chain)
            logger.info(f"{api_config.get('name', '')}视频发送成功: {temp_path}")

        except Exception as e:
            logger.error(f"处理{api_config.get('name', '')}video类型失败: {str(e)}", exc_info=True)
            yield event.plain_result(f"❌ {api_config.get('name', '')}视频处理失败: {str(e)}")
        finally:
            # 清理临时文件
            if 'temp_path' in locals() and temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    logger.info(f"临时文件已删除: {temp_path}")
                except Exception as e:
                    logger.warning(f"删除临时文件失败: {str(e)}")


    async def handle_video_url_type(self, api_config: dict, event: AstrMessageEvent):
        """处理视频url类型的API"""
        if self.enable_video == False:
            yield event.plain_result("暂未开启视频API功能")
            return

        logger.info(f"{api_config.get('name', '')}为url视频类型，使用get_video_url函数下载")

        try:
            # 获取URL和参数\
            name = api_config.get("name", "")
            url = api_config.get("url", "").strip()
            headers = api_config.get("headers", {})
            params = api_config.get("params", {})

            if not url:
                yield event.plain_result("API配置缺少url字段")
                return

            # 获取视频URL
            if name == "随机视频":
                video_url = await self.request.get_random_video(url, headers=headers, params=params)
            else:
                video_url = await self.request.get_video_url(url, headers=headers, params=params)
            if not video_url:
                yield event.plain_result(f"获取{api_config.get('name', '')}视频URL失败")
                return

            # 发送视频URL
            chain = [
                At(qq=event.get_sender_id()),
                Plain(f"你的{api_config.get('name', '视频')}请查收！"),
                Video.fromURL(url=str(video_url))
            ]
            yield event.chain_result(chain)
            logger.info(f"{api_config.get('name', '')}URL发送成功: {video_url}")

        except Exception as e:
            logger.error(f"{api_config.get('name', '')}url处理失败: {str(e)}", exc_info=True)
            yield event.plain_result(f"❌ {api_config.get('name', '')}URL处理失败: {str(e)}")


    async def handle_image_type(self, api_config: dict, event: AstrMessageEvent):
        """处理本地图片类型的API"""
        if self.enable_image == False:
            yield event.plain_result("暂未开启图片API功能")
            return

        logger.info(f"{api_config.get('name', '')}为图片类型，使用get_image_url函数下载")

        try:
            # 获取URL和参数
            name = api_config.get("name", "")
            url = api_config.get("url", "").strip()
            headers = api_config.get("headers", {})
            params = api_config.get("params", {})
            message_str = event.message_str
            # 判断是否为星座运势
            if message_str.split("-")[0] == "星座运势":
                msg = message_str.split("-")[1]
            else:
                msg = ""

            if not url:
                yield event.plain_result("API配置缺少url字段")
                return

            # 获取图片URL
            temp_path = await self.request.get_image(url, headers=headers, params=params, msg=msg)
            if not temp_path:
                yield event.plain_result("获取图片URL失败")
                return

            # 发送视频URL
            chain = [
                At(qq=event.get_sender_id()),
                Plain(f"你的{api_config.get('name', '图片')}请查收！"),
                Image.fromFileSystem(path=str(temp_path))
            ]
            yield event.chain_result(chain)
            logger.info(f"{api_config.get('name', '')}发送成功: {temp_path}")

        except Exception as e:
            logger.error(f"{api_config.get('name', '')}处理失败: {str(e)}", exc_info=True)
            yield event.plain_result(f"❌ {api_config.get('name', '')}处理失败: {str(e)}")


    async def handle_image_url_type(self, api_config: dict, event: AstrMessageEvent):
        """处理图片url类型的API"""
        if self.enable_image == False:
            yield event.plain_result("暂未开启图片API功能")
            return

        logger.info(f"{api_config.get('name', '')}为图片类型，使用get_image_url函数下载")

        try:
            # 获取URL和参数
            name = api_config.get("name", "")
            url = api_config.get("url", "").strip()
            headers = api_config.get("headers", {})
            params = api_config.get("params", {})
            message_str = event.message_str
            msg = message_str.split("-")[1]

            if not url:
                yield event.plain_result("API配置缺少url字段")
                return

            # 获取图片URL
            image_url = await self.request.get_image_url(url, headers=headers, params=params, msg=msg)
            if not image_url:
                yield event.plain_result("获取图片URL失败")
                return

            # 发送视频URL
            chain = [
                At(qq=event.get_sender_id()),
                Plain(f"你的{api_config.get('name', '图片')}请查收！"),
                Image.fromURL(url=str(image_url))
            ]
            yield event.chain_result(chain)
            logger.info(f"{api_config.get('name', '')}URL发送成功: {image_url}")

        except Exception as e:
            logger.error(f"{api_config.get('name', '')}url处理失败: {str(e)}", exc_info=True)
            yield event.plain_result(f"❌ {api_config.get('name', '')}URL处理失败: {str(e)}")