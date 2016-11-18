# -*- coding: utf8 -*-
import os
import re
import codecs
from datetime import datetime
from urllib.parse import unquote

import demjson

blog_dir = "E:\\git\\cloudchou.github.io\\_posts"

files = os.listdir(blog_dir)


def get_file_content(file_path):
    with codecs.open(file_path, 'r', 'utf-8') as f:
        return f.readlines()


posts = {}
print("compute post time for every posts")
for filename in files:
    file_path = blog_dir + "\\" + filename
    file_content = get_file_content(file_path)
    meta_file_content = re.sub(r'(---.*---).*', r'\1', ''.join(file_content), flags=re.M | re.S)
    date_str = re.sub(r'---.*date: ([^+]+).*---', r'\1', meta_file_content, flags=re.M | re.S)
    post_link_str = re.sub(r'---.*permalink: ([\S]+).*---', r'\1', meta_file_content, flags=re.M | re.S)
    time_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
    time = time_obj.strftime("%Y-%m-%d %H:%M:%S")
    post_link_str = unquote(post_link_str)
    posts["http://www.cloudchou.com" + post_link_str] = time

print("write post time to files")
demjson.encode_to_file("posts_time.json", posts, 'utf-8', True, indent_amount=2, compactly=False)
print("finish !!!! Now You can open posts_time.json to see post time for every post")
