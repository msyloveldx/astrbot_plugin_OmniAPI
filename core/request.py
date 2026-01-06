import random
import httpx
import tempfile
from typing import Tuple, Optional, Dict, Any

from astrbot.api import logger
from .apiManager import APIManager

class RequestManager:
    def __init__(self,
                 # config: Dict[str, Any]
                 ):
        # self.config = config
        self.api_manager = APIManager()
        self.client = None

    async def initialize(self):
        """初始化HTTP客户端"""
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_text(self, url: str, headers: Dict[str, str], params: Dict[str, str]):
        """发送GET请求，返回响应文本"""
        # 获取api_key
        params["ckey"] = self.api_manager.get_ckey()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code != 200:
                    logger.error(f"视频下载失败，状态码: {resp.status_code}")
                    return None
                logger.info(f"文本获取成功，内容: {resp.json()}")
                json_data = resp.json()  # ✅ await 异步方法
                text = json_data.get("text")  # ✅ 从 dict 取值

                return text
        except Exception as e:
            logger.error(f"文本获取异常: {str(e)}")
            return None

    async def get_audio(self, url: str, headers: Dict[str, str], params: Dict[str, str], role: str, msg: str) -> str | None:
        """发送GET请求，返回语音文件路径"""
        # 获取api_key
        params["ckey"] = self.api_manager.get_ckey()
        params["msg"] = msg
        params["id"] = role
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("GET", url, headers=headers, params=params) as resp:
                    if resp.status_code != 200:
                        logger.error(f"语音下载失败，状态码: {resp.status_code}")
                        return None

                    # 创建临时 .mp3 文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                        temp_path = tmp.name

                    with open(temp_path, "wb") as f:
                        async for chunk in resp.aiter_bytes(8192):
                            f.write(chunk)

                    # 转为 .wav或.silk
                    from pydub import AudioSegment
                    mp3_file = AudioSegment.from_file(temp_path, format="mp3")
                    wav_file = mp3_file.export(temp_path, format="wav")
                    # wav_file.export(temp_path, format="silk")

                    logger.info(f"语音下载成功，临时文件: {temp_path}")
                    return temp_path
        except Exception as e:
            logger.error(f"语音下载异常: {str(e)}")
            return None

    async def get_audio_url(self, url: str, headers: Dict[str, str], params: Dict[str, str], role: str, msg: str) -> str | None:
        """发送GET请求，返回语音文件url路径"""
        # 获取api_key
        params["ckey"] = self.api_manager.get_ckey()
        params["msg"] = msg
        params["id"] = role
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # ✅ 正确：直接 await get，不要 async with
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code != 200:
                    logger.error(f"语音下载失败，状态码: {resp.status_code}")
                    return None

                logger.info(resp.json())
                audio_url = resp.json()["url"]

                async with client.stream("GET", audio_url, headers=headers) as resp:
                    if resp.status_code != 200:
                        logger.error(f"语音下载失败，状态码: {resp.status_code}")
                        return None

                    # 创建临时 .mp3 文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                        temp_path = tmp.name

                    with open(temp_path, "wb") as f:
                        async for chunk in resp.aiter_bytes(8192):
                            f.write(chunk)

                    # 转为 .wav或.silk
                    from pydub import AudioSegment
                    mp3_file = AudioSegment.from_file(temp_path, format="mp3")
                    wav_file = mp3_file.export(temp_path, format="wav")
                    # wav_file.export(temp_path, format="silk")

                    logger.info(f"语音下载成功，临时文件: {temp_path}")
                    return temp_path
        except Exception as e:
            logger.error(f"语音下载异常: {str(e)}")
            return None

    async def get_video(self, url: str, headers: Dict[str, str], params: Dict[str, str]) -> str | None:
        """下载视频，返回临时文件路径"""
        # 获取api_key
        params["ckey"] = self.api_manager.get_ckey()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("GET", url, headers=headers, params=params) as resp:
                    if resp.status_code != 200:
                        logger.error(f"视频下载失败，状态码: {resp.status_code}")
                        return None

                    # 创建临时 .mp4 文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        temp_path = tmp.name

                    with open(temp_path, "wb") as f:
                        async for chunk in resp.aiter_bytes(8192):
                            f.write(chunk)

                    logger.info(f"视频下载成功，临时文件: {temp_path}")
                    return temp_path
        except Exception as e:
            logger.error(f"视频下载异常: {str(e)}")
            return None

    async def get_video_url(self, url: str, headers: Dict[str, str], params: Dict[str, str]) -> str | None:
        """发送GET请求，返回文件url路径"""
        # 获取api_key
        params["ckey"] = self.api_manager.get_ckey()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # ✅ 正确：直接 await get，不要 async with
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code != 200:
                    logger.error(f"视频下载失败，状态码: {resp.status_code}")
                    return None

                logger.info(resp.json())
                temp_path = resp.json()["data"]

                return temp_path
        except Exception as e:
            logger.error(f"视频下载异常: {str(e)}")
            return None

    async def get_image(self, url: str, headers: Dict[str, str], params: Dict[str, str], msg: str) -> str | None:
        """下载图片，返回临时文件路径"""
        # 获取api_key
        params["ckey"] = self.api_manager.get_ckey()
        params["msg"] = msg
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("GET", url, headers=headers, params=params) as resp:
                    if resp.status_code != 200:
                        logger.error(f"图片下载失败，状态码: {resp.status_code}")
                        return None

                    # 创建临时 .png 文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        temp_path = tmp.name

                    with open(temp_path, "wb") as f:
                        async for chunk in resp.aiter_bytes(8192):
                            f.write(chunk)

                    logger.info(f"图片下载成功，临时文件: {temp_path}")
                    return temp_path
        except Exception as e:
            logger.error(f"图片下载异常: {str(e)}")
            return None

    async def get_image_url(self, url: str, headers: Dict[str, str], params: Dict[str, str], msg: str) -> str | None:
        """下载图片，返回临时文件路径"""
        # 获取api_key
        params["ckey"] = self.api_manager.get_ckey()
        params["msg"] = msg
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # ✅ 正确：直接 await get，不要 async with
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code != 200:
                    logger.error(f"图片下载失败，状态码: {resp.status_code}")
                    return None

                logger.info(resp.json())
                temp_path = resp.json()["data"]

                return temp_path
        except Exception as e:
            logger.error(f"图片下载异常: {str(e)}")
            return None


    async def get_random_video(self, url: str, headers: Dict[str, str], params: Dict[str, str]) -> str | None:
        """下载视频，返回随机视频文件路径"""
        # url = "https://api.317ak.cn/api/jhsp"
        # headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        # }
        random_list = [
            "奈奈魔王", "曼小丑熊", "钱思怡系", "穗岁同学", "甜妹小金", "肉肉不胖", "兔兔奶糖", "木糖醇系", "钱思怡系",
            "萧萧系列", "青春男大", "黑丝系列", "白丝系列", "女大系列", "麦麦妹妹", "雅婷妹妹", "歪宝学姐", "小欣老师",
            "甜菜大王", "漫欲姐姐", "萱萱仙女", "西颜妹妹", "雪雪学姐", "毛蛋妹妹", "爆笑虫子", "开心锤锤", "风景视频",
            "米雷画画", "辰妈系列", "天诗府系", "清凉一夏", "旺仔小乔", "小李逵系", "萝卜头系", "做我的猫", "懒羊翻唱",
            "应激兄弟", "范老九系", "治愈视频", "浅影姐姐", "王大毛系", "胖虎姐姐", "鞠婧祎系", "赵思露系", "甜妹系列",
            "园园宝贝", "失眠豆包", "瑶妹宝贝", "元气少女", "仙女系列", "感觉至上", "御萝双修", "清纯甜美", "奶油乎乎",
            "晴川林子", "派大萱系", "江寻千系", "圆一依系", "白可歪歪", "突突萌娃"
        ]
        params = {
            "ckey": "LCW4HP76R9LKRWXCEMAX",
            "msg": f"{random.choices(random_list)}",
            "type": "json",
            "lb": ""
        }
        # 获取api_key
        params["ckey"] = self.api_manager.get_ckey()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("GET", url, headers=headers, params=params) as resp:
                    if resp.status_code != 200:
                        logger.error(f"视频下载失败，状态码: {resp.status_code}")
                        return None

                    # 创建临时 .mp4 文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        temp_path = tmp.name

                    with open(temp_path, "wb") as f:
                        async for chunk in resp.aiter_bytes(8192):
                            f.write(chunk)

                    logger.info(f"视频下载成功，临时文件: {temp_path}")
                    return temp_path
        except Exception as e:
            logger.error(f"视频下载异常: {str(e)}")
            return None

    async def terminate(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("HTTP客户端已关闭")



