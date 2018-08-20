# coding:utf-8


import requests
import datetime
import random
import json
from urllib.parse import urlencode

import chardet
from lxml import etree
from login import make_cookies


class FetchWeibo(object):

    def __init__(self):
        self.users_dict = {
            '15600920758': 'chenhe1993',
            '791962385@qq.com': 'sina0624####',
            '14575782371': 'ja684623',
            '15874645844': 'ja684629',
        }

    @staticmethod
    def date_range(begindate, enddate):
        dates = []
        dt = datetime.datetime.strptime(begindate, "%Y-%m-%d")
        date = begindate[:]
        while date <= enddate:
            dates.append(date)
            dt = dt + datetime.timedelta(1)
            date = dt.strftime("%Y-%m-%d")
        return dates

    def get_cookies(self):
        """获取cookies"""
        return [
            {'_T_WM': '8eb40d501fdd2b55f206d9a28e233ada', 'SSOLoginState': '1534754283', 'SUHB': '0oUob1h2gdjew_',
             'SCF': 'AgyJfqg--fF4w2gfYhuZDa4jsmG_60lMVPhJu7d0d9wdS8-dw4xNNfJGrAtZXc3X_WrSsdjePL1IihDToDSVGvY.',
             'SUB': '_2A252fg27DeRhGeNJ6lAY8yjMwjWIHXVVgJPzrDV6PUJbkdBeLVD1kW1NS-J60QjUYyScibmbPEJnFA2CwX-dmwap'},
            {'SSOLoginState': '1534754290', 'SUHB': '0M2V6b-hqBhEg6', '_T_WM': '8eb40d501fdd2b55f206d9a28e233ada',
             'SUB': '_2A252fg2iDeRhGeVO4lMU8yvPwjmIHXVVgJPqrDV6PUJbkdBeLUOikW1NTXO141RbBk1ITv50QtFY_OTE1DehP-7G',
             'SCF': 'AgyJfqg--fF4w2gfYhuZDa4jsmG_60lMVPhJu7d0d9wdS8-dw4xNNfJGrAtZXc3X_WrSsdjePL1IihDToDSVGvY.'},
            {'SSOLoginState': '1534754296', 'SUHB': '0idrv90-501i-6', '_T_WM': '8eb40d501fdd2b55f206d9a28e233ada',
             'SUB': '_2A252fg2oDeRhGeBM41oR9SbLwj2IHXVVgJPgrDV6PUJbkdBeLWnakW1NRK0qHnIkEI8ZFw9JtzrvLo67r8eVF4RG',
             'SCF': 'AgyJfqg--fF4w2gfYhuZDa4jsmG_60lMVPhJu7d0d9wdS8-dw4xNNfJGrAtZXc3X_WrSsdjePL1IihDToDSVGvY.'},
            {'SSOLoginState': '1534754302', 'SUHB': '0ebt7pU50T2xjK', '_T_WM': '8eb40d501fdd2b55f206d9a28e233ada',
             'SUB': '_2A252fg2uDeRhGeBM41UX8ifOzD2IHXVVgJPmrDV6PUJbkdBeLW3xkW1NRK4RPJK_5cRCetZ4t2iWgjrfNi-5RmtM',
             'SCF': 'AgyJfqg--fF4w2gfYhuZDa4jsmG_60lMVPhJu7d0d9wdS8-dw4xNNfJGrAtZXc3X_WrSsdjePL1IihDToDSVGvY.'},
        ]
        # return make_cookies(self.users_dict)

    def _fetch_page(self, html):
        selector = etree.HTML(html)
        tmp = selector.xpath('//form[@method="post"]/div/input[@name="mp"]/@value')
        page = int(tmp[0]) if tmp else 0
        return page

    def _encode_html(self, html):
        code_detect = chardet.detect(html)['encoding']
        if code_detect:
            html = html.decode(code_detect, 'ignore')
        else:
            html = html.decode("utf-8", 'ignore')
        return html

    def fetch_users(self, keywords, begin_date, end_date):
        """
        抓取用户列表
        :param keywords: list
        :param begin_date: str 2018-08-20
        :param end_date:   str 2018-08-20
        :return: list
        """
        user_lst = []
        # begin_date = '-'.join([i.zfill(2) for i in begin_date.split('-')])
        # end_date = '-'.join([i.zfill(2) for i in end_date.split('-')])
        cookies = self.get_cookies()
        for keyword in keywords:
            for query_date in self.date_range(begin_date, end_date):
                data = {
                    'advancedfilter': '1',
                    'keyword': keyword,
                    'nick': '',
                    'starttime': query_date.replace('-', ''),
                    'endtime': query_date.replace('-', ''),
                    'sort': 'time',
                    'smblog': '搜索'
                }
                res = requests.post(
                    url='https://weibo.cn/search/',
                    data=data,
                    cookies=random.choice(cookies),
                    headers={
                        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36",
                        # 'cookies': json.dumps(random.choice(cookies))
                    }
                )
                html = res.content
                page = self._fetch_page(html)
                for pg in range(1, page + 1):
                    query = {
                        'hideSearchFrame': '',
                        'keyword': keyword,
                        'advancedfilter': '1',
                        'starttime': query_date,
                        'endtime': query_date,
                        'sort': 'time',
                        'page': str(pg),
                    }
                    url_encode = urlencode(query)
                    url = 'https://weibo.cn/search/mblog?{0}'.format(url_encode)
                    res = requests.get(url, cookies=random.choice(cookies))
                    html = res.content
                    selector = etree.HTML(html)
                    divs = selector.xpath('//div[@class="c" and @id]')
                    for div in divs:
                        author = div.xpath('./div/a[@class="nk"]/text()')[0]
                        link = div.xpath('./div/a[@class="nk"]/@href')[0]
                        print(author, link)
                        user_lst.append((author, link))
        return user_lst







if __name__ == '__main__':
    weibo = FetchWeibo()
    keyword = ['螺纹钢']
    begin_date = '2018-08-10'
    end_date = '2018-08-20'
    user_lst = weibo.fetch_users(keyword, begin_date, end_date)
