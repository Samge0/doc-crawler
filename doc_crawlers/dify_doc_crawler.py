#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-26 14:44
# describe：

import urllib3
# Suppress only the specific InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from bs4 import BeautifulSoup
from base_doc_crawler import BaseDocCrawler
from utils import fileutils


class DifyDocCrealer(BaseDocCrawler):
    
    def get_index_url(self):
        return 'https://docs.dify.ai/v/zh-hans'
    
    def get_html_save_dir(self):
        return fileutils.get_cache_dir('dify2/html')
    
    def get_markdown_save_dir(self):
        return fileutils.get_cache_dir('dify2/markdown')
    
    def get_item_list(self, soup: BeautifulSoup):
        return [{'text': a.text.strip(), 'link': a['href']} for a in soup.find('aside').find_all('a', href=True) if 'zh-hans' in a['href']]
    
    def get_replace_content(self, soup: BeautifulSoup):
        # 获取标签名为 'main' 的文本
        main_tag = soup.find('main')
        if not main_tag:
            return ''

        # 移除 'main' 标签最后两个元素
        if len(main_tag.contents) >= 2:
            main_tag.contents[-1].extract()
            main_tag.contents[-1].extract()
        return main_tag
    
    def get_filename(self, link):
        if 'zh-hans/guides/' in link:
            filename = link.split('zh-hans/guides/')[1].replace('/', '-')
        elif 'zh-hans/' in link:
            filename = link.split('zh-hans/')[1].replace('/', '-')
        else:
            filename = os.path.basename(link)   
        return filename
    
    
if __name__ == '__main__':
    DifyDocCrealer().crawl()