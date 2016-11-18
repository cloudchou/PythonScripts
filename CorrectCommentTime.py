# -*- coding: utf8 -*-
from datetime import datetime

import demjson

post_time_file = 'posts_time.json'
comment_time_file = 'comments.json'
p_time_dict = demjson.decode_file(post_time_file)
comments_list = demjson.decode_file(comment_time_file)


def correct_comment_time(comment):
    # "time": "2016-06-21 22:43:00",
    comment_time = datetime.strptime(comment["time"], '%Y-%m-%d %H:%M:%S')
    comment_url = comment["url"]
    if not (comment_url in p_time_dict.keys()):
        print("comment_url " + comment_url + " have no post url ")
        return
    post_time = datetime.strptime(p_time_dict[comment_url], '%Y-%m-%d %H:%M:%S')
    comment_time = comment_time.replace(year=post_time.year)
    if comment_time < post_time:
        comment_time = comment_time.replace(year=post_time.year + 1)
    comment["time"] = comment_time.strftime('%Y-%m-%d %H:%M:%S')


for comment in comments_list:
    correct_comment_time(comment)
    if not ("child" in comment.keys()):
        continue
    child_comments = comment["child"]
    for c_comment in child_comments:
        correct_comment_time(c_comment)

print("Your comments will saved to comments_correct_time.json.")
demjson.encode_to_file("comments_correct_time.json", comments_list, 'utf-8', True, indent_amount=2, compactly=False)
print("Finish  !!!!   Now you can open comments_correct_time.json to see the comments")
