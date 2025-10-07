# NagaAgent Core

NagaAgent核心依赖包，包含核心功能和API服务器相关依赖。

## 版本

当前版本：1.0.6

## 包含的依赖

### 核心依赖
- `mcp>=1.6.0` - MCP协议支持
- `openai>=1.76.0` - OpenAI API客户端
- `python-dotenv>=1.1.0` - 环境变量管理
- `requests>=2.32.3` - HTTP请求库
- `aiohttp>=3.11.18` - 异步HTTP客户端

### API服务器相关依赖
- `flask>=3.1.0` - Flask Web框架
- `gevent>=25.5.1` - 异步网络库
- `fastapi>=0.115.0` - FastAPI Web框架
- `uvicorn[standard]>=0.34.0` - ASGI服务器

### GUI 依赖（统一随包安装）
- `PyQt5>=5.15.11`
- `pyqt5-qt5>=5.15.2`
- `pyqt5-sip>=12.17.0`

## 安装

```bash
pip install nagaagent-core==1.0.1
## 统一导入方式

上层项目无需直接依赖 `PyQt5`，统一从本包导入：

```python
from nagaagent_core.qt import QtCore, QtGui, QtWidgets  # 推荐

# 或需要原命名空间时：
from nagaagent_core.vendors.PyQt5 import QtCore, QtGui, QtWidgets
```

```

## 开发安装

```bash
git clone <repository-url>
cd nagaagent-core
pip install -e .
```

## 许可证

MIT License
