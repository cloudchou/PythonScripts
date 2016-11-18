#!/usr/bin/env python
#  本脚本用于在博客更新后 通知所有搜索引擎 博客有更新
# -*- coding:utf-8 -*-
from xmlrpc import client
import sys


def ping(ping_url, *args, **kwds):
    """args: site_name, site_host, post_url, rss_url."""
    print("try to ping: " + ping_url)
    with client.ServerProxy(ping_url) as proxy:
        result = proxy.weblogUpdates.extendedPing(*args)
        print("ping: " + ping_url + "\nresult:")
        print(result)


def ping_all(*args, **kwds):
    ping_url_list = [
        'http://ping.baidu.com/ping/RPC2',
        'http://blogsearch.google.com/ping/RPC2',
    ]
    for url in ping_url_list:
        ping(url, *args, **kwds)


def main():
    site_name = "tech2ipo"
    site_host = "http://www.cloudchou.com"
    blog_url = 'http://www.cloudchou.com/android/post-980.html'
    if len(sys.argv) > 0:
        blog_url = sys.argv[1]
    rss_url = "http://www.cloudchou.com/feed.xml"
    print("blog url : " + blog_url)
    ping_all(site_name, site_host, blog_url, rss_url)


main()
