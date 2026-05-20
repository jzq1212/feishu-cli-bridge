<h1 align="center">Feishu CLI Bridge</h1>

<p align="center">
  <strong>飞书 ↔ Crush CLI 的 WebSocket 桥接器</strong>
</p>

<p align="center">
  📱 在飞书上聊天 → 🤖 Crush 自动执行 → 💬 回复到飞书
</p>

## 它能做什么

```
飞书消息 → WebSocket → bot.py → crush run "你的问题" → 结果返回飞书
```

把 [Crush](https://github.com/crush-chat/crush) 搬进飞书，手机上就能用。

## 特点

- **WebSocket 模式** — 无需公网 IP，不用 ngrok，飞书原生 WebSocket 直连
- **权限控制** — 指定飞书用户才能使用，不担心乱用
- **非阻塞执行** — CLI 调用跑在独立线程里，飞书消息处理不卡顿

## 对比其他桥接器

| | feishu-cli-bridge | larkcc | cc-connect |
|---|---|---|---|
| 适用 agent | **Crush** | 仅 Claude Code | 有限类型 |
| 流式输出 | ❌ | ✅ | ✅ |
| 飞书卡片 | ❌ | ✅ | ✅ |

> larkcc 和 cc-connect 都不支持 Crush，所以有了这个桥接器。

## 快速开始

### 1. 创建飞书应用

1. 打开 [飞书开放平台](https://open.feishu.cn/)，创建**企业自建应用**
2. 在**凭证与基础信息**页面获取 `App ID` 和 `App Secret`
3. 开启**机器人**能力
4. 订阅事件：`im.message.receive_v1`
5. 发布应用

WebSocket 模式不需要配置回调 URL。

### 2. 安装

```bash
git clone https://github.com/jzq1212/feishu-cli-bridge.git
cd feishu-cli-bridge
pip install -r requirements.txt
```

### 3. 配置

```bash
cp .env.example .env
```

编辑 `.env`：

```env
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLI_BIN=crush
CLI_CWD=/path/to/your/project
```

### 4. 运行

```bash
python bot.py
```

看到 `=== READY ===` 就说明连上了。给你的飞书机器人发消息试试。

## 配置说明

| 变量 | 默认值 | 说明 |
|---|---|---|
| `FEISHU_APP_ID` | — | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | — | 飞书应用 App Secret |
| `CLI_BIN` | `crush` | Crush 二进制路径或名称 |
| `CLI_TIMEOUT` | `300` | 每次调用超时（秒） |
| `CLI_CWD` | — | Crush 工作目录（空 = 继承 bot.py 的目录） |
| `MAX_OUTPUT` | `8000` | 返回飞书的最大字符数 |
| `ALLOWED_USERS` | — | 允许使用的飞书用户 open_id（逗号分隔，空 = 所有人） |

CLI 的调用方式：`{CLI_BIN} run "用户消息"`。

### 限制用户

在飞书管理后台获取用户的 `open_id`（格式 `ou_xxxxxxxx`）：

```env
ALLOWED_USERS=ou_xxxx1,ou_xxxx2
```

## 项目结构

```
feishu-cli-bridge/
├── bot.py              # 主程序
├── requirements.txt     # Python 依赖
├── .env.example         # 配置模板
├── LICENSE              # MIT 许可证
└── README.md            # 本文件
```

## 依赖

- Python 3.10+
- [lark-oapi](https://github.com/feishu/lark-oapi) — 飞书官方 Python SDK
- python-dotenv — 环境变量加载

## License

MIT
