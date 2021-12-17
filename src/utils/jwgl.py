from bs4 import BeautifulSoup
from collections import defaultdict
import re
from typing import List, Tuple
import requests
import datetime
import json
import time

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

ua = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'Host': 'jwxt.bupt.edu.cn',
    'Origin': 'https://jwxt.bupt.edu.cn'
}


def encodepw(username, password):
    from base64 import b64encode
    return (b64encode(str.encode(username)) + b"%%%" + b64encode(str.encode(password))).decode()


def get_text(username, password, week, day):
    url = "https://jwgl.bupt.edu.cn/jsxsd/"
    ua['Host'] = "jwgl.bupt.edu.cn"
    ua['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8," \
                   "application/signed-exchange;v=b3;q=0.9 "
    if 'Origin' in ua.keys():
        del ua['Origin']
    _ = requests.get(url=url, headers=ua, verify=False)  # 获得登录页面
    url_auth = "https://jwgl.bupt.edu.cn/jsxsd/xk/LoginToXk"
    ua['Origin'] = "https://jwgl.bupt.edu.cn"
    data = {
        "userAccount": username,
        "userPassword": password,
        "encoded": encodepw(username, password)
    }
    s = requests.session()
    _ = s.post(url=url_auth, headers={"Referer": "https://jwgl.bupt.edu.cn/jsxsd/",
                                      "Origin": "https://jwgl.bupt.edu.cn", }, data=data, verify=False)
    s.headers.update({'Referer': "https://jwgl.bupt.edu.cn/jsxsd/framework/xsMain.jsp"})
    if 'Origin' in ua.keys():
        del ua['Origin']
    class_data = {
        'typewhere': 'jszq',
        'xnxqh': '2021-2022-1',
        'xqbh': '01',
        'bjfh': '=',
        'jszt': '5',
        'zc': str(week),
        'zc2': str(week),
        'xq': str(day),
        'xq2': str(day),
        'kbjcmsid': '9475847A3F3033D1E05377B5030AA94D',
    }
    kb_html = s.post(url="https://jwgl.bupt.edu.cn/jsxsd/kbxx/jsjy_query2", headers=ua, data=class_data, verify=False)
    kb_html.encoding = "utf-8"
    ua['Origin'] = "https://jwgl.bupt.edu.cn"
    return kb_html.text


def get_class(class_name: str) -> int:
    if class_name.startswith('图书馆'):
        return 0
    return int(class_name.split('-')[0])


def get_class_name(class_num: int) -> str:
    if class_num == 0:
        return '图书馆'
    if class_num == 1:
        return '教一楼'
    if class_num == 2:
        return '教二楼'
    if class_num == 3:
        return '教三楼'
    if class_num == 4:
        return '教四楼'


def get_info(classroom: Tuple[str, int, str, List]):
    return {
        "name": classroom[0],
        "function": "多媒体教室(校本部)",
        "seats": classroom[1]
    }


def generate_free_table(html: str) -> List[Tuple[str, int, str, List]]:
    bs = BeautifulSoup(html, features="html.parser")
    classrooms = bs.find_all('tr', {'onmouseover': 'this.style.cursor=\'hand\''})
    schedule = []
    for i in classrooms:
        temp = []
        tds = i.find_all('td')
        info = tds[0].text.strip().split('|')[0].split('(')
        if info[0].startswith('虚拟'):
            continue
        name: str = info[0]
        seats = int(re.findall(r'(.*)/', info[1])[0])
        for j in range(1, len(tds)):
            temp.append(tds[j].text.strip())
        schedule.append((name, seats, get_class_name(get_class(name)), temp))
    return schedule


def generate_result(schedule, week, day):
    result = {}
    for i in range(14):
        free = defaultdict(list)
        for t in schedule:
            if len(t[3][i]) == 0:
                free[t[2]].append(get_info(t))
        for _, v in free.items():
            v.sort(key=lambda x: x['name'])
        result['%02d' % week + '.' + str(day - 1) + '.' + '%02d' % i] = free
    return result


def get_result(name, password, week, day):
    schedule = generate_free_table(get_text(name, password, week, day))
    return generate_result(schedule, week, day)


def get_week_day():
    diff = (datetime.datetime.now() - datetime.datetime(2021, 8, 30, 0, 0, 0)).days
    diff = max(diff, 0)
    return diff // 7 + 1, diff % 7 + 1


if __name__ == '__main__':
    info = get_week_day()
    result = {}
    for i in range(7):
        t = get_result('__username__', '__password__', info[0], i + 1)
        result.update(t)
        time.sleep(0.5)
    with open("jwgl.json", mode='w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    f.close()
