from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import platform

from astrbot import logger

# ================== 配置区 ==================
# 字体路径配置（根据系统自动选择）
def get_font_path():
    system = platform.system()
    if system == "Windows":
        return "C:/Windows/Fonts/msyh.ttc"
    elif system == "Darwin":  # macOS
        return "/System/Library/Fonts/PingFang.ttc"
    else:  # Linux/Docker
        # 用户上传的字体路径
        user_font = "/usr/share/fonts/chinese/msyh.ttc"
        if os.path.exists(user_font):
            return user_font
        # 备选路径
        font_paths = [
            "/usr/share/fonts/chinese/MSYH.TTC",
            "/usr/share/fonts/chinese/SIMSUN.TTC",
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
        return None

FONT_PATH = get_font_path()

OUTPUT_IMAGE = "data/plugins/astrbot_plugin_omniapi/data/help_cmd.png"

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
    if FONT_PATH:
        try:
            font = ImageFont.truetype(FONT_PATH, size)
            logger.info(f"✅ 使用字体: {FONT_PATH}")
            return font
        except OSError:
            logger.warning(f"⚠️ 字体加载失败: {FONT_PATH}")
    logger.warning("⚠️ 使用默认字体（可能不支持中文）")
    return ImageFont.load_default()


def parse_commands(raw_text: str):
    """
    解析Markdown格式的指令文本
    输出：[{"type": "分类名", "icon": "图标", "lines": [...]}]
    """
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
    categories = []
    current_cat = {"type": "通用", "icon": "•", "lines": []}

    for line in lines:
        # 检测标题行（以 ### 开头）
        if line.startswith("### "):
            if current_cat["lines"]:
                categories.append(current_cat)
            # 提取分类名，去除图标
            title = line.replace("### ", "").strip()
            if "🎬" in title:
                icon = "🎬"
            elif "🎤" in title:
                icon = "🎤"
            elif "🖼️" in title:
                icon = "🖼️"
            elif "🎵" in title:
                icon = "🎵"
            else:
                icon = "📋"
            current_cat = {"type": title, "icon": icon, "lines": []}
        # 检测列表项（以 - 开头）
        elif line.startswith("- "):
            current_cat["lines"].append(line)
        # 分隔线
        elif line.startswith("---"):
            if current_cat["lines"]:
                categories.append(current_cat)
            current_cat = {"type": "其他", "icon": "•", "lines": []}
        # 跳过Markdown标题标记
        elif line.startswith("## ") or line.startswith("# "):
            continue

    if current_cat["lines"]:
        categories.append(current_cat)

    # 页脚
    footer = ""
    for line in lines:
        if "发送指令" in line:
            footer = line.strip()
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
        total_height += 35  # 分类标题
        for cmd in cat["lines"]:
            wrapped = textwrap.wrap(cmd, width=35)  # 每行约35字
            total_height += len(wrapped) * (COMMAND_FONT_SIZE + 10)
        total_height += 20  # 分类间距

    total_height += 60  # 页脚 + 底部留白

    # 创建画布
    image = Image.new("RGB", (max_width, max(total_height, 400)), BG_COLOR)
    draw = ImageDraw.Draw(image)

    # 绘制标题
    draw.text((40, 20), "🌟 AstrBotOmniAPI 指令列表", fill=TITLE_COLOR, font=title_font)

    y_offset = 70

    # 绘制每个分类
    for cat in categories:
        if not cat["lines"]:
            continue

        # 分类标题
        cat_text = f"{cat['icon']} {cat['type']}"
        draw.text((40, y_offset), cat_text, fill=CATEGORY_COLOR, font=category_font)
        y_offset += 35

        # 指令列表
        for cmd in cat["lines"]:
            # 移除列表标记 "- "
            cmd_clean = cmd.replace("- ", "", 1)
            wrapped_lines = textwrap.wrap(cmd_clean, width=35)
            for line in wrapped_lines:
                draw.text((50, y_offset), line, fill=COMMAND_COLOR, font=command_font)
                y_offset += COMMAND_FONT_SIZE + 10
        y_offset += 15  # 分类间空隙

    # 绘制页脚
    if footer:
        draw.line([(40, y_offset), (max_width - 40, y_offset)], fill=SEPARATOR_COLOR, width=2)
        y_offset += 15
        draw.text((40, y_offset), footer, fill=TEXT_COLOR, font=footer_font)

    # 保存
    image.save(output_path, "PNG", quality=95)
    logger.info(f"✅ 帮助图片已生成: {os.path.abspath(output_path)}")
    return output_path


# ================== 使用示例 ==================
if __name__ == "__main__":
    HELP_TEXT = """## 🌟 可用指令

### 🎬 随机视频
- /随机视频
- /did
- /男大

### 🎬 听泉鉴宝
- /听泉鉴宝
- /鉴宝

---

发送指令即可获取对应内容
"""

    generate_help_image(HELP_TEXT, OUTPUT_IMAGE)