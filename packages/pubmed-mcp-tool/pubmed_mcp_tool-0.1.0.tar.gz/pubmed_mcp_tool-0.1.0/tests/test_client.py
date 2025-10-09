import httpx
import json

# 测试PubMed MCP服务器
base_url = "http://localhost:8000"
headers = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json"
}

# 测试工具列表
print("测试工具列表...")
try:
    response = httpx.post(f"{base_url}/mcp", 
                         json={
                             "jsonrpc": "2.0",
                             "method": "tools/list",
                             "id": 1
                         },
                         headers=headers)
    print(f"状态码: {response.status_code}")
    result = response.json()
    if "result" in result:
        tools = result["result"].get("tools", [])
        print(f"可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"- {tool['name']}: {tool.get('description', '无描述')}")
    else:
        print(f"响应: {result}")
except Exception as e:
    print(f"错误: {e}")

# 测试文献检索
print("\n测试文献检索...")
try:
    response = httpx.post(f"{base_url}/mcp", 
                         json={
                             "jsonrpc": "2.0",
                             "method": "tools/call",
                             "params": {
                                 "name": "search_pubmed",
                                 "arguments": {
                                     "keyword": "COVID-19",
                                     "max_results": 3
                                 }
                             },
                             "id": 2
                         },
                         headers=headers)
    print(f"状态码: {response.status_code}")
    result = response.json()
    if "result" in result:
        print(f"找到文献数量: {result['result']['total_found']}")
        for i, paper in enumerate(result['result']['results']):
            print(f"{i+1}. {paper['title'][:100]}...")
            print(f"   作者: {paper['authors'][:100]}...")
            print(f"   发表日期: {paper['publication_date']}")
            print(f"   期刊: {paper['journal']}")
            print(f"   PubMed链接: {paper['pubmed_url']}")
            print()
    else:
        print(f"响应: {result}")
except Exception as e:
    print(f"错误: {e}")