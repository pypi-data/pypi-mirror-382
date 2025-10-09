from fastmcp import FastMCP
import httpx

# 创建MCP服务器
mcp = FastMCP("PubMed Literature Search")

@mcp.tool
async def search_pubmed(keyword: str, max_results: int = 10) -> dict:
    """
    基于关键词检索PubMed文献
    
    Args:
        keyword: 搜索关键词
        max_results: 最大返回结果数 (默认10)
    
    Returns:
        dict: 包含文献信息的字典
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    try:
        # 第一步: 搜索文献ID
        search_url = f"{base_url}esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": keyword,
            "retmax": max_results,
            "retmode": "json"
        }
        
        async with httpx.AsyncClient() as client:
            search_response = await client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            # 获取文献ID列表
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not pmids:
                return {"message": "未找到相关文献", "results": []}
            
            # 第二步: 获取文献详细信息
            summary_url = f"{base_url}esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "json"
            }
            
            summary_response = await client.get(summary_url, params=summary_params)
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            # 解析结果
            results = []
            result_data = summary_data.get("result", {})
            
            for pmid in pmids:
                article = result_data.get(pmid, {})
                if article:
                    title = article.get("title", "")
                    authors = article.get("authors", [])
                    author_list = [author.get("name", "") for author in authors if author.get("name")]
                    
                    pubdate = article.get("pubdate", "")
                    source = article.get("source", "")
                    
                    results.append({
                        "pmid": pmid,
                        "title": title,
                        "authors": ", ".join(author_list),
                        "publication_date": pubdate,
                        "journal": source,
                        "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    })
            
            return {
                "keyword": keyword,
                "total_found": len(pmids),
                "results": results
            }
            
    except httpx.HTTPError as e:
        return {"error": f"HTTP错误: {str(e)}"}
    except Exception as e:
        return {"error": f"检索失败: {str(e)}"}

if __name__ == "__main__":
    # 以HTTP模式运行服务器
    mcp.run(transport="http", host="0.0.0.0", port=8000)
