import asyncio
import json
from fastmcp import Client

async def test_pubmed_search():
    """测试PubMed搜索功能"""
    try:
        async with Client("http://localhost:8000/mcp") as client:
            # 测试工具列表
            print("获取工具列表...")
            tools = await client.list_tools()
            print(f"可用工具: {[tool.name for tool in tools]}")
            
            # 测试PubMed搜索
            print("\n测试PubMed搜索...")
            result = await client.call_tool(
                "search_pubmed",
                arguments={
                    "keyword": "COVID-19",
                    "max_results": 3
                }
            )
            
            # 获取结果内容
            if hasattr(result, 'content'):
                # 如果是列表，取第一个元素
                if isinstance(result.content, list) and len(result.content) > 0:
                    content = result.content[0].text
                    data = json.loads(content)
                else:
                    data = result.content
            else:
                data = result
            
            if isinstance(data, dict):
                print(f"找到文献数量: {data.get('total_found', 0)}")
                for i, paper in enumerate(data.get('results', [])):
                    print(f"\n{i+1}. {paper['title'][:100]}...")
                    print(f"   作者: {paper['authors'][:100]}...")
                    print(f"   发表日期: {paper['publication_date']}")
                    print(f"   期刊: {paper['journal']}")
                    print(f"   PubMed链接: {paper['pubmed_url']}")
            else:
                print(f"结果: {data}")
        
                
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_pubmed_search())