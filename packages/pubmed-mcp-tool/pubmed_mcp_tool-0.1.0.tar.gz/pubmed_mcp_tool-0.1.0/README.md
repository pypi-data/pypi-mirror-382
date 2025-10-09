# PubMed MCP工具

基于FastMCP构建的PubMed文献检索MCP服务器。

## 功能

- 基于关键词检索PubMed文献
- 返回文献标题、作者、发表日期、期刊等信息
- 提供PubMed链接

## 安装和运行

### 安装依赖
```bash
uv sync
```

### 运行服务器
```bash
# 使用uv运行
uv run main.py

# 或者直接运行
python main.py
```

服务器将在 http://localhost:8000 启动

## 使用示例

服务器启动后，可以使用以下工具：

### search_pubmed
- **功能**: 基于关键词检索PubMed文献
- **参数**:
  - `keyword` (str): 搜索关键词
  - `max_results` (int, 可选): 最大返回结果数，默认10
- **返回**: 包含文献信息的字典

## API端点

- `POST /mcp/tools/search_pubmed`: 调用文献检索工具

## 示例请求

```bash
curl -X POST http://localhost:8000/mcp/tools/search_pubmed \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "COVID-19",
    "max_results": 5
  }'
```