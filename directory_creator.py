"""
directory_creator.py

Provides website crawling and directory mapping functionality for Director-AI.
Builds a hierarchical structure of a website and exports as CSV, JSON, or XML.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import networkx as nx
import pandas as pd
import json
from typing import Set, Dict, List

class DirectoryCreator:
    def __init__(self, base_url: str, max_depth: int = 2):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.graph = nx.DiGraph()

    def crawl(self, url: str, depth: int = 0):
        if depth > self.max_depth or url in self.visited:
            return
        self.visited.add(url)
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            links = [urljoin(url, a.get('href')) for a in soup.find_all('a', href=True)]
            for link in links:
                parsed = urlparse(link)
                if parsed.netloc == urlparse(self.base_url).netloc:
                    self.graph.add_edge(url, link)
                    self.crawl(link, depth + 1)
        except Exception as e:
            pass  # Optionally log errors

    def export_csv(self, filename: str):
        edges = list(self.graph.edges())
        df = pd.DataFrame(edges, columns=['from', 'to'])
        df.to_csv(filename, index=False)

    def export_json(self, filename: str):
        data = nx.node_link_data(self.graph)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def export_xml(self, filename: str):
        # Simple XML export (hierarchical)
        from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
        root = Element('website')
        nodes = {n: SubElement(root, 'page', url=n) for n in self.graph.nodes()}
        for src, dst in self.graph.edges():
            SubElement(nodes[src], 'link', url=dst)
        tree = ElementTree(root)
        tree.write(filename)

# Example usage:
# creator = DirectoryCreator('https://example.com', max_depth=2)
# creator.crawl(creator.base_url)
# creator.export_csv('site_map.csv')
# creator.export_json('site_map.json')
# creator.export_xml('site_map.xml')
