# astrbot_plugin_OmniAPI

AstrBot 多模态娱乐插件，通过指令获取API的图片、文字、视频、音频等内容并发送。支持动态配置API接口，可灵活扩展各种内容类型的API。

## 功能特点

- 🎬 **多模态API支持**：支持视频、图片、文字、音频等多种内容类型的API调用
- 🎛️ **动态配置**：通过JSON配置文件动态注册和管理API指令
- 🚀 **丰富指令**：支持多种视频、图片、音频API指令
- 🧹 **自动清理**：自动清理临时文件，避免磁盘空间占用
- 📊 **详细日志**：提供详细的日志记录，便于调试和监控
- ⚡ **异步处理**：使用异步HTTP请求，提高处理效率

## 支持的指令

插件支持多种视频、图片和音频指令，包括但不限于：

| 指令 | 功能 | 类型 |
|------|------|------|
| did | 发送美女视频 | 视频 |
| 随机视频 | 发送随机视频 | 视频 |
| 男大/帅哥 | 发送帅哥视频 | 视频 |
| 4k壁纸 | 发送4K壁纸 | 图片 |
| 久喵系列 | 发送视频内容 | 视频 |
| 仙桃猫系 | 发送视频内容 | 视频 |
| 公主花园 | 发送视频内容 | 视频 |
| 甜甜表妹 | 发送视频内容 | 视频 |
| 心情好好 | 发送视频内容 | 视频 |
| 小雪妹妹 | 发送视频内容 | 视频 |
| 红鸾姐姐 | 发送视频内容 | 视频 |
| 狼宝姐姐 | 发送视频内容 | 视频 |
| 雪梨美女 | 发送视频内容 | 视频 |
| 兔兔美女 | 发送视频内容 | 视频 |
| 奶白奈奈 | 发送视频内容 | 视频 |
| ... | 更多视频内容 | 视频 |

## 安装方法

1. 将插件目录 `astrbot_plugin_OmniAPI` 放入 AstrBot 的 `data/plugins` 目录下
2. 安装依赖：`pip install -r requirements.txt`
3. 配置API密钥（可选）：在 `plugin_apis.json` 中设置 `ckey` 参数
4. 重启 AstrBot

## 配置说明

### API配置
- 所有API配置位于 [plugin_apis.json](./plugin_apis.json) 文件中
- 支持多种API类型：`video`、`image`、`text`、`audio`
- 支持多种视频类型：`video`（下载本地）、`url`（直接URL）
- 支持多种图片类型：`image`（下载本地）、`url`（直接URL）

### 系统配置
- 插件开关配置位于 `data/config/astrbot_plugin_OmniAPI_config.json`
- 可控制各类型API的启用/禁用：
  - `enable_text`: 文本API开关
  - `enable_image`: 图片API开关
  - `enable_audio`: 音频API开关
  - `enable_video`: 视频API开关
  - `api_keys`: API密钥配置

## 插件结构

```
astrbot_plugin_OmniAPI/
├── main.py              # 插件主入口，注册指令和处理逻辑
├── core/                # 核心功能模块
│   ├── __init__.py
│   ├── apiHandle.py     # API处理逻辑
│   ├── apiManager.py    # API配置管理
│   └── request.py       # HTTP请求处理
├── data/                # 数据配置目录
│   ├── t2i_templates/   # 模板文件
│   │   ├── astrbot_powershell.html
│   │   └── base.html
│   └── cmd_config.json
├── tmp/                 # 临时文件目录（自动创建）
├── .gitignore
├── LICENSE
├── README.md            # 插件说明文档
├── metadata.yaml        # 插件元数据
├── plugin_apis.json     # API配置文件
├── _conf_schema.json    # 配置模式定义
└── requirements.txt     # 依赖列表
```

## API类型说明

### 视频API
- `video`类型：下载视频到本地后发送
- `url`类型：直接通过URL发送视频

### 图片API
- `image`类型：下载图片到本地后发送
- `url`类型：直接通过URL发送图片

### 文本API
- 直接返回文本内容

### 音频API
- 下载音频到本地后发送

## 使用方法

1. **直接调用**：发送对应指令（如 `did`、`随机视频` 等）
2. **查看帮助**：发送 `help_cmd` 查看所有可用指令

## 依赖说明

- `httpx>=0.24.0`：用于异步HTTP请求

## 日志记录

插件会生成详细的日志，方便调试和监控。日志级别为 INFO，包含以下信息：

- 插件初始化和销毁
- 收到的指令
- API调用过程
- 内容发送结果
- 错误信息

## 支持

[帮助文档](https://astrbot.app)

## 致谢
- [AstrBot](https://github.com/AstrBot/AstrBot)
- [倾梦API](https://api.317ak.cn)

## 许可证

MIT