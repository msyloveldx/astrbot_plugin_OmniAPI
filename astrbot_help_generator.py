from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

from astrbot import logger

# ================== 配置区 ==================
# 替换为你自己的字体路径（支持中文）
# Windows 示例: "C:/Windows/Fonts/msyh.ttc"
# Mac 示例: "/System/Library/Fonts/PingFang.ttc"
# Linux 示例: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"（需中文字体）
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"  # 请根据你的系统修改！

OUTPUT_IMAGE = "astrbot_help_v4.10.6.png"

# 颜色配置
BG_COLOR = (250, 250, 255)  # 背景：浅蓝白
TITLE_COLOR = (0, 82, 255)  # 标题蓝
TEXT_COLOR = (30, 30, 50)  # 正文深灰
CATEGORY_COLOR = (0, 120, 200)  # 分类标题蓝
COMMAND_COLOR = (50, 50, 70)  # 指令灰黑
SEPARATOR_COLOR = (180, 180, 220)  # 分割线浅蓝

# 字体大小
TITLE_FONT_SIZE = 36
CATEGORY_FONT_SIZE = 24
COMMAND_FONT_SIZE = 20
FOOTER_FONT_SIZE = 18


# ===========================================

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        print(f"⚠️ 字体文件未找到: {FONT_PATH}")
        print("使用默认字体（可能不支持中文）")
        return ImageFont.load_default()


def parse_commands(raw_text: str):
    """
    简单解析指令文本，按分类分组
    输入：原始文本（含 🎬 🎙️ 等 emoji）
    输出：[{"type": "视频", "lines": [...], "icon": "🎬"}, ...]
    """
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
    categories = []
    current_cat = {"type": "通用", "icon": "•", "lines": []}

    for line in lines:
        if "视频指令" in line:
            if current_cat["lines"]:
                categories.append(current_cat)
            current_cat = {"type": "视频", "icon": "🎬", "lines": []}
        elif "语音指令" in line:
            if current_cat["lines"]:
                categories.append(current_cat)
            current_cat = {"type": "语音", "icon": "🎤", "lines": []}
        elif "图片指令" in line:
            if current_cat["lines"]:
                categories.append(current_cat)
            current_cat = {"type": "图片", "icon": "🖼️", "lines": []}
        elif "其他指令" in line or "————————" in line:
            if current_cat["lines"]:
                categories.append(current_cat)
            current_cat = {"type": "其他", "icon": "⚙️", "lines": []}
            break  # 后续为页脚
        else:
            # 提取指令行（如 "• 随机视频"）
            if "•" in line and not line.startswith("🌟"):
                current_cat["lines"].append(line)

    if current_cat["lines"]:
        categories.append(current_cat)

    # 页脚
    footer = ""
    for line in lines:
        if "————————" in line:
            footer = line.replace("——————————————", "").strip()
            break

    return categories, footer


def generate_help_image(raw_text: str, output_path: str):
    categories, footer = parse_commands(raw_text)

    # 初始化字体
    title_font = get_font(TITLE_FONT_SIZE)
    category_font = get_font(CATEGORY_FONT_SIZE)
    command_font = get_font(COMMAND_FONT_SIZE)
    footer_font = get_font(FOOTER_FONT_SIZE)

    # 估算图片高度
    total_height = 60  # 顶部留白 + 标题
    max_width = 800  # 固定宽度（适合手机查看）

    for cat in categories:
        total_height += 30  # 分类标题
        for cmd in cat["lines"]:
            wrapped = textwrap.wrap(cmd, width=38)  # 每行约38字
            total_height += len(wrapped) * (COMMAND_FONT_SIZE + 8)
        total_height += 15  # 分类间距

    total_height += 50  # 页脚 + 底部留白

    # 创建画布
    image = Image.new("RGB", (max_width, total_height), BG_COLOR)
    draw = ImageDraw.Draw(image)

    # 绘制标题
    draw.text((40, 20), "# AstrBot v4.10.6", fill=TITLE_COLOR, font=title_font)

    y_offset = 80

    # 绘制每个分类
    for cat in categories:
        if not cat["lines"]:
            continue

        # 分类标题（带图标）
        cat_text = f"{cat['icon']} {cat['type']}指令"
        draw.text((40, y_offset), cat_text, fill=CATEGORY_COLOR, font=category_font)
        y_offset += 35

        # 指令列表
        for cmd in cat["lines"]:
            wrapped_lines = textwrap.wrap(cmd, width=38)
            for line in wrapped_lines:
                draw.text((60, y_offset), line, fill=COMMAND_COLOR, font=command_font)
                y_offset += COMMAND_FONT_SIZE + 8
        y_offset += 10  # 分类间空隙

    # 绘制页脚
    if footer:
        draw.line([(40, y_offset - 5), (max_width - 40, y_offset - 5)], fill=SEPARATOR_COLOR, width=2)
        y_offset += 10
        draw.text((40, y_offset), footer, fill=TEXT_COLOR, font=footer_font)

    # 保存
    image.save(output_path, "PNG", quality=95)
    logger.info(f"✅ 帮助图片已生成: {os.path.abspath(output_path)}")
    return output_path


# ================== 使用示例 ==================
if __name__ == "__main__":
    # 🔻 请在此处粘贴你从 AstrBot 获取的完整指令文本 🔻
    HELP_TEXT = """
🌟 可用视频指令: —————————————————— 🎬 随机视频: • 随机视频 🎬 did: • did 🎬 男大: • 男大 • 帅哥 🎬 久喵系列: • 久喵系列 🎬 仙桃猫系: • 仙桃猫系 🎬 大雷系列: • 大雷系列 🎬 三梦奇缘: • 三梦奇缘 🎬 酒仙系列: • 酒仙系列 🎬 河南男大: • 河南男大 🎬 听泉鉴宝: • 听泉鉴宝 • 鉴宝 🎬 半佛仙人: • 半佛仙人 🎬 慧慧是猪猪: • 慧慧是猪猪 🎬 二饼: • 二饼 🎬 小潮: • 小潮 🎬 小潮team: • 小潮team 🎬 三梦: • 三梦 🎬 三梦奇缘: • 三梦奇缘 🎬 三梦视频: • 三梦视频 🎬 胡凯文: • 胡凯文 🎬 胡凯文系列: • 胡凯文系列 🎬 胡凯文搞笑: • 胡凯文搞笑 🎬 胡凯文模仿: • 胡凯文模仿 🎬 胡凯文合集: • 胡凯文合集 🎬 胡凯文直播: • 胡凯文直播 🎬 胡凯文视频: • 胡凯文视频 🎬 胡凯文搞笑视频: • 胡凯文搞笑视频 🎬 胡凯文模仿秀: • 胡凯文模仿秀 🎬 胡凯文搞笑模仿: • 胡凯文搞笑模仿 🎬 胡凯文搞笑合集: • 胡凯文搞笑合集 🎬 胡凯文直播回放: • 胡凯文直播回放 🎬 胡凯文视频合集: • 胡凯文视频合集 —————————————— 发送指令即可获取对应视频内容
"""

    generate_help_image(HELP_TEXT, OUTPUT_IMAGE)