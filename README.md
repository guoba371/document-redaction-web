# Web 文档脱敏工具

一个基于 Flask 的轻量级文档脱敏工具，支持上传 `Word (.doc / .docx)` 和 `PDF (.pdf)` 文件，对常见敏感字段进行自动脱敏，并生成可下载的新文件。

## 功能

- 支持上传单个 `DOC`、`DOCX` 或 `PDF` 文件
- 默认脱敏：姓名、身份证号、手机号、邮箱、地址、公司名称
- 支持前端勾选是否启用某类脱敏
- 支持输入自定义敏感关键字并选择是否脱敏
- 处理完成后直接下载新文件
- 尽量保留 Word / PDF 原有排版

## 一键启动

### macOS

直接双击项目目录中的 [start.command](./start.command) 即可。

也可以在终端中执行：

```bash
cd "/Users/sai/Desktop/Vibe Coding项目实践/document redaction"
chmod +x start.command start.sh
./start.command
```

脚本会自动完成以下步骤：

1. 创建 `.venv` 虚拟环境
2. 安装或更新依赖
3. 启动 Flask 服务
4. 自动打开浏览器访问 `http://127.0.0.1:5000`

## 手动启动

```bash
cd "/Users/sai/Desktop/Vibe Coding项目实践/document redaction"
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python app.py
```

## 停止服务

在启动服务的终端窗口中按 `Ctrl + C`。

## GitHub + Render 部署

这个项目已经补齐了 Render 部署文件：

- [Dockerfile](./Dockerfile)
- [render.yaml](./render.yaml)
- [requirements.txt](./requirements.txt)

其中 `.doc` 支持在不同环境下会自动选择转换器：

- macOS 本地开发：使用 `textutil`
- Render / Linux Docker：使用 `LibreOffice (soffice)`

### 1. 推送到 GitHub

如果你还没有初始化 Git 仓库，可以在项目目录执行：

```bash
cd "/Users/sai/Desktop/Vibe Coding项目实践/document redaction"
git init
git add .
git commit -m "feat: add document redaction web app"
git branch -M main
git remote add origin <你的 GitHub 仓库地址>
git push -u origin main
```

### 2. 在 Render 创建服务

1. 登录 Render
2. 选择 `New +` -> `Blueprint`
3. 连接你的 GitHub 仓库
4. 选择这个项目仓库
5. Render 会自动识别仓库根目录下的 `render.yaml`
6. 确认创建后开始部署

部署成功后，Render 会分配一个 `*.onrender.com` 地址。

### 3. 部署方式说明

本项目使用 Docker 部署到 Render，而不是 Render 的原生 Python Runtime。

原因是 `.doc` 文件转换在 Render 的 Linux 环境中需要 `LibreOffice` 这类系统级依赖。根据 Render 官方文档，若服务需要额外的 OS 级依赖，更适合使用 Docker 部署：

- Render Docker 文档：https://render.com/docs/docker
- Render Blueprint 规范：https://render.com/docs/blueprint-spec
- Render Web Service 说明：https://render.com/docs/web-services

### 4. Render 环境变量

Blueprint 已自动声明：

- `SECRET_KEY`：自动生成
- `PYTHONUNBUFFERED=1`

Render 还会自动提供 `PORT`，应用会绑定到 `0.0.0.0:$PORT`。

### 5. 健康检查

项目提供了健康检查接口：

```text
/health
```

Render 会用它做服务健康检查。

## 项目结构

```text
document redaction/
├── .dockerignore
├── .gitignore
├── app.py
├── config.py
├── Dockerfile
├── requirements.txt
├── README.md
├── render.yaml
├── start.command
├── start.sh
├── services/
│   ├── __init__.py
│   ├── doc_converter.py
│   ├── docx_handler.py
│   ├── patterns.py
│   ├── pdf_handler.py
│   └── redaction_service.py
├── templates/
│   ├── base.html
│   └── index.html
├── uploads/
└── processed/
```

## 说明

- `DOC` 文件会先自动转换为 `DOCX` 再执行脱敏：
  macOS 使用 `textutil`，Render/Linux Docker 使用 `LibreOffice`。
- `DOCX` 脱敏会尽量保留段落、表格、页眉页脚和大部分样式结构。
- `PDF` 脱敏基于可搜索文本定位后覆盖替换；如果 PDF 是扫描件图片，当前版本不含 OCR，识别效果会受限。
- 当前规则是轻量版正则方案，适合快速落地；如需更高识别准确率，可以继续扩展 NLP 或 OCR 能力。
