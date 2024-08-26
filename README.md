## 下载文档并转为md的脚本
为了将一些页面文档内容下载并转为markdown文件&上传到RAG知识库中查询，写一个脚本实现。

### 创建env环境
```shell
conda create -n doc-crawler python=3.10.13 -y
```

### 安装依赖
```shell
pip install -r requirements.txt
```

### 下载文档
- 下载[dify的文档](https://docs.dify.ai/v/zh-hans)并转为md文件
```shell
python doc_crawlers/dify_doc_crawler.py
```