import os
import random
import time
import html2text
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from utils import fileutils, timeutils, uautils


class BaseDocCrawler(object):
    
    # 是否需要替换已存在的文件
    NEED_REPLACE = False
 
    def get_header(self):
        """
        Get the header to use.

        Returns:
            dict: A dictionary of header, where the key is the header name and the value is the header value.
        """
        return {'User-Agent': uautils.random_one()}

    def get_proxies(self):
        """
        Get the proxies to use.

        Returns:
            dict: A dictionary of proxies, where the key is the protocol and the value is the proxy URL.
        """
        return {'http': None, 'https': None}
    
    @timeutils.monitor
    def get_response(self, link, max_retries=5):
        """
        Try to get the response of a link with a maximum number of retries.

        Args:
            link (str): The link to get the response from.
            max_retries (int, optional): The maximum number of retries. Defaults to 5.

        Returns:
            requests.Response: The response of the link.

        Raises:
            Exception: Raises an exception if all retries failed.
        """
        try:
            link_response = requests.get(link, headers=self.get_header(), proxies=self.get_proxies(), timeout=20, verify=False)
            return link_response
        except Exception as e:
            if max_retries > 0:
                sleep_time = random.randint(1, 5)
                timeutils.print_log(f"Error: {str(e):100}... Retrying...[{max_retries}]...随机休眠{sleep_time}秒后继续")
                time.sleep(sleep_time)
                return self.get_response(link, max_retries - 1)
            else:
                raise e

    @timeutils.monitor
    def htmlpath2md(self, htmlpath, filename):
        """
        读取HTML文件，使用html2text将其转换为markdown并保存

        :param htmlpath:  HTML文件的路径
        :param filename:  文件名
        :return:
        """
        md_save_path = f"{self.get_markdown_save_dir()}/{filename}.md"
        if self.NEED_REPLACE is False and os.path.exists(md_save_path):
            timeutils.print_log(f"exists, skip: {md_save_path}")
            return
            
        content = fileutils.read(htmlpath)
        md_context = html2text.html2text(content)
        fileutils.save(md_save_path, md_context)
        timeutils.print_log(f"{htmlpath}\n转为 markdown 文件=> {md_save_path}")
        
    def get_filename(self, link):
        """
        Get the filename of the link.

        :param link: The link to get the filename of.
        :return: The filename of the link.
        """
        return os.path.basename(link)
    
    def get_html_save_dir(self):
        return fileutils.get_cache_dir('default_doc/html')
    
    def get_markdown_save_dir(self):
        return fileutils.get_cache_dir('default_doc/markdown')
    
    @timeutils.monitor
    def crawl(self):
        """
        Get the index page of the documentation and traverse the link list to get the content of each page and save it to a file.
        
        :return: None
        """
        index_url = self.get_index_url()
        response = self.get_response(index_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取所有文档item列表，返回格式为：[{'text':'xxx', 'link':'http://xxx'}……]
        lst = self.get_item_list(soup)

        # 遍历 lst
        for item in lst:
            text = item.get('text')
            link = urljoin(index_url, item.get('link'))
            
            # 自定义文件名
            filename = self.get_filename(link)  
            filename = filename.split('?')[0]
            
            if text:
                filename += f"-{text}"

            filename = filename.replace(' ', '-').replace('/', 'or')
            save_path = f"{self.get_html_save_dir()}/{filename}.html"
            if self.NEED_REPLACE is False and os.path.exists(save_path):
                timeutils.print_log(f"exists, skip: {save_path}")
                self.htmlpath2md(save_path, filename)
                continue
            
            # 获取每个链接的响应内容
            link_response = self.get_response(link)
            item_soup = BeautifulSoup(link_response.text, 'html.parser')
            
            # 获取标签名需要替换body的内容
            replace_content = self.get_replace_content(item_soup)

            # 替换原来 'body' 里面的内容
            body_tag = item_soup.find('body')
            if body_tag:
                body_tag.clear()
                body_tag.append(replace_content)
            
            # 自动补全所有链接（a、link、script、img等）
            for tag in item_soup.find_all(['a', 'link', 'script', 'img']):
                if tag.name == 'a' and tag.get('href'):
                    tag['href'] = urljoin(index_url, tag['href'])
                elif tag.name == 'link' and tag.get('href'):
                    tag['href'] = urljoin(index_url, tag['href'])
                elif tag.name == 'script' and tag.get('src'):
                    tag['src'] = urljoin(index_url, tag['src'])
                elif tag.name == 'img' and tag.get('src'):
                    tag['src'] = urljoin(index_url, tag['src'])
                    
            fileutils.save(save_path, item_soup.prettify())
                
            self.htmlpath2md(save_path, filename)

            timeutils.print_log(f"Saved: {save_path}")
            
        timeutils.print_log("all done")
