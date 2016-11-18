# -*- coding: utf-8 -*-
import requests
from Tools.scripts.treesync import raw_input
from bs4 import BeautifulSoup
import re
from datetime import datetime
import demjson

common_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/54.0.2840.71 Safari/537.36',
}
jiathis_headers = {
    'Host': 'login.jiathis.com'
}
uyan_headers = {
    'Host': 'www.uyan.cc'
}


def login(email, password):
    s = requests.session()
    print("try to get formhash")
    # 获取form_hash
    login_url = "http://login.jiathis.com/?callback=http%3A%2F%2Fwww.uyan.cc&inframe=1"
    html = s.get(login_url, headers={**common_headers, **jiathis_headers})
    soup = BeautifulSoup(html.text, 'html.parser')
    hidden_input = soup.find('input', type='hidden')
    form_hash = hidden_input['value']
    login_data = {'memberid': email,
                  'password': password,
                  'remember': 'on',
                  'formhash': form_hash,
                  'loginsubmit': '1'}
    # 登录
    print("try to login")
    r = s.post(login_url, data=login_data, headers={**common_headers, **jiathis_headers})
    print("Login  status code %d" % r.status_code)
    # 二次登录 服务器返回两个需要跳转的url,必须登陆后才能正常获取评论数据
    # < script  type = "text/javascript" reload = "1"
    #    src = "http://www.ujian.cc/api?time=1479365706&code=7d7dxmlfzeLjsJPHskx5iPdvPA%2Be5fP9M2TKBGOkPg00vtkQYw2KiNZ
    #   4YivO56uOL8p108Un3QWsad0c6XATgO17NZELxnWwzWY5DjAZ6m%2BGHhG6rrhJxRdFqP5vYg0pITpiFwX6vdPGYrWjqimxoN
    #   FnveKSh57JUzvIeDdP%2FqsuwUX%2BUW34sSAUhQ"
    # >  < / script >
    # < script  type = "text/javascript" reload = "1"
    # src = "http://www.uyan.cc/api?time=1479365706&code=c467tlQYos152lYKkZZb30b2KGuvy9J7jd%2Bb6DgEkpG%2FVp7ny6%2FE5y6g
    # JNCqObFfU%2BP73TBkI4SphRYiKtA0j6X%2BjjeOIQiBSuyIj5iGyq3fgrK%2F3X%2Fmlnc0Mg4w%2F9pVOAAoygby6WxG%2BBZkNJSyfEHo%2Bw
    # 0qv%2F0dHmMhw3AKJ2zt8PUs%2F055BosK9A"
    #  > < / script >
    soup = BeautifulSoup(r.text, 'html.parser')
    script_tags = soup.find_all('script', reload='1')
    print("try to login for api redirect.")
    for script_tag in script_tags:
        r = s.get(script_tag['src'], headers={**common_headers, **uyan_headers})
        print("api login result: %d" % r.status_code)
    return s


def strip_str(str):
    title = re.sub(r'^[\n\s]+', r"", str, flags=re.M | re.S)
    title = re.sub(r'[\n\s]+$', r"", title, flags=re.M | re.S)
    return title


def parse_page_comments(child_comments, comments, soup):
    # print(soup.prettify())
    # 评论数据形式
    # "su": "",
    # "url": "http://d.com/a.html",  页面地址
    # "title": "测试一下，你就知道", 页面标题
    # "content": "c", 评论内容
    # "time": "2012-10-09 10:40:29", 评论时间
    # "uname": "test",  昵称 (必选)
    # "email": "zhangsan@sina.com",  邮箱地址 (非必选)
    # "ulink": "http://blog.jiathis.com", 个人主页链接地址 (非必选)
    # "status": "0"  0：正常, 1：待验证, 2：垃圾，3：已被删除 (非必选，默认是正常评论)
    # child: 子评论，格式和父级评论大致相同，但是子集评论无更下一级的评论
    user_comments = soup.find_all('div', 'user-comment')
    for user_comment in user_comments:
        uname_elem = user_comment.find('a', 'uyan_cmt_uname')
        uname = uname_elem['title']
        sibling1 = uname_elem.next_sibling.next_sibling
        parent_u_name = ''
        if sibling1.has_attr("class"):
            # sibling1["class"] 是一个list, ['connector']
            parent_u_name = sibling1.contents[3].string
            sibling1 = sibling1.next_sibling.next_sibling
        silba_elem = sibling1.contents[1]
        url = silba_elem['href']
        title = strip_str(silba_elem.string)
        content = strip_str(user_comment.find('div', 'uyan_cmt_txt').string)
        orig_time = strip_str(user_comment.find('div', 'cmt_time').string)
        # 所有时间都缺少年的信息， 只能先用2016年代替，要靠其它方式补充年的信息，
        # 如果是Jekyll脚本， 可以获取每篇博客的发表时间 来进行计算， 可以粗略估计评论时间必须>博客发表时间
        orig_time = '2016年 ' + orig_time
        time_obj = datetime.strptime(orig_time, '%Y年  %m月 %d日 %H:%M')
        time = time_obj.strftime("%Y-%m-%d %H:%M:%S")
        comment = {"uname": uname, "url": url, "title": title, "content": content, "time": time}
        if parent_u_name != '':
            child_comments.append({**comment, "parent_uname": parent_u_name})
        else:
            comments.append(comment)


def get_next_page_num(cur_page, soup):
    page_num_lis = soup.find('div', 'page').find_all('li')
    for page_num_li in page_num_lis:
        if page_num_li.has_attr("class"):
            cur_page = int(page_num_li.find("a").string)
        else:
            string = page_num_li.find("a").string
            if string.isdigit():
                page_num = int(string)
                if page_num > cur_page:
                    return page_num
    return -1


def get_all_page_comments(child_comments, comments, s):
    comment_url = "http://www.uyan.cc/comment/content?domain=www.cloudchou.com&act=ajaxGetContent&stat=0"
    r = s.get(comment_url, headers={**common_headers, **uyan_headers})
    print("get first page comment status %d." % r.status_code)
    soup = BeautifulSoup(r.text, 'html.parser')
    parse_page_comments(child_comments, comments, soup)
    next_page_num = get_next_page_num(1, soup)
    print("next page num : %d" % next_page_num)
    while next_page_num != -1:
        comment_url = "http://www.uyan.cc/comment/content/%d/?domain=www.cloudchou.com&act=ajaxGetContent&stat=0" \
                      % next_page_num
        r = s.get(comment_url, headers={**common_headers, **uyan_headers})
        print("get %d page comment status %d." % (next_page_num, r.status_code))
        soup = BeautifulSoup(r.text, 'html.parser')
        parse_page_comments(child_comments, comments, soup)
        next_page_num = get_next_page_num(next_page_num, soup)


def main():
    email = raw_input("Please enter your uyan login email:")
    password = raw_input("Please enter your uyan password:");
    session = login(email, password)
    comments = []
    child_comments = []
    get_all_page_comments(child_comments, comments, session)
    for c_comment in child_comments:
        parent_uname = c_comment["parent_uname"]
        del c_comment["parent_uname"]
        for p_comment in comments:
            if p_comment['uname'] == parent_uname and c_comment["url"] == p_comment["url"]:
                if not 'child' in p_comment.keys():
                    p_comment['child'] = [c_comment]
                else:
                    p_comment['child'].append(c_comment)
                break
    print("Your comments will saved to comments.json.")
    demjson.encode_to_file("comments.json", comments, 'utf-8', True, indent_amount=2, compactly=False)
    print("Finish  !!!!   Now you can open comments.json to see the comments")


if __name__ == '__main__':
    main()
