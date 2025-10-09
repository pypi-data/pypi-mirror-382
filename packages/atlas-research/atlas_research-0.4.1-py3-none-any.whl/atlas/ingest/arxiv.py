import requests
import xml.etree.ElementTree as ET

class ArxivIngestor:
    """
    ArxivIngestor: arXiv API에서 논문 메타데이터를 수집하는 클래스
    """

    def __init__(self, base_url="http://export.arxiv.org/api/query"):
        self.base_url = base_url

    def fetch_papers(self, query: str, max_results: int = 5):
        """
        arXiv에서 검색어(query) 기반으로 논문 메타데이터 가져오기

        Args:
            query (str): 검색 키워드
            max_results (int): 가져올 논문 수

        Returns:
            list[dict]: 논문 정보 딕셔너리 리스트
        """
        url = f"{self.base_url}?search_query=all:{query}&start=0&max_results={max_results}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        papers = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text.strip()
            link = entry.find("atom:id", ns).text.strip()
            summary = entry.find("atom:summary", ns).text.strip()

            papers.append({
                "title": title,
                "link": link,
                "summary": summary
            })

        return papers
