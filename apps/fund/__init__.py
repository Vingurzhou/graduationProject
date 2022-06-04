# -*- coding: utf-8 -*-


"""
File   :model
Author :wezhou
Date   :2021/11/12
Product:PyCharm
Project:demoProject
Details:
   #             with open(
    #                     f'././static/js/{fund}.js',
    #                     'w') as f:
    #                 f.write(f'''
    # let myChart = echarts.init(document.getElementById('chart'));
    # const xData = {self.data}.map(item => {{
    #                   return item['净值日期'];
    #                 }});
    # const yData ={self.data}.map(item => {{
    #                   return item['单位净值'];
    #                 }});
    # const option = {{
    #     title : {{
    #         text: '{fund}',
    #         x: 'center',
    #         align: 'right'
    #     }},
    #     grid: {{
    #         bottom: 80
    #     }},
    #     toolbox: {{
    #         feature: {{
    #             saveAsImage: {{}}
    #         }}
    #     }},
    #     tooltip : {{
    #         trigger: 'axis',
    #         axisPointer: {{
    #             animation: false
    #         }}
    #     }},
    #     dataZoom: [
    #         {{
    #             show: true,
    #             realtime: true,
    #             start: 65,
    #             end: 85
    #         }},
    #         {{
    #             type: 'inside',
    #             realtime: true,
    #             start: 65,
    #             end: 85
    #         }}
    #     ],
    #     //x轴时间轴
    #     xAxis : [
    #         {{
    #             type : 'category',
    #             data : xData
    #         }}
    #     ],
    #     yAxis: [
    #         {{
    #             name: '净值',
    #             type: 'value'
    #         }}
    #     ],
    #     //y轴
    #     series: [
    #         {{
    #             name:'{fund}',
    #             type:'line',
    #             animation: false,
    #             smooth:true,
    #             symbol:'none',
    #             lineStyle: {{
    #                 normal: {{
    #                     width: 1
    #                 }}
    #             }},
    #             data:yData
    #         }}
    #     ]
    # }};
    # myChart.setOption(option);
    # ''')
"""

import json
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
import demjson
import numpy
import pandas
import requests
from requests.adapters import HTTPAdapter
from apps.extend import MysqlUtil


def compute_error_for_line_given_points(b, w, points):
    totalError = 0
    for i in range(0, len(points)):
        x = points[i, 0]
        y = points[i, 1]
        # computer mean-squared-error
        totalError += (y - (w * x + b)) ** 2
    # average loss for each point
    return totalError / float(len(points))


def step_gradient(b_current, w_current, points, learningRate):
    b_gradient = 0
    w_gradient = 0
    N = float(len(points))
    for i in range(0, len(points)):
        x = points[i, 0]
        y = points[i, 1]
        # grad__b = 2(wx+b-y )
        b_gradient += (2 / N) * ((w_current * x + b_current) - y)
        # grad__w = 2(wx+b-y )*x
        w_gradient += (2 / N) * x * ((w_current * x + b_current) - y)  # update w
        # with open('w.txt','a')as f:
        #     f.write(f'{b_gradient}{w_gradient}\n')
    new_b = b_current - (learningRate * b_gradient)
    new_w = w_current - (learningRate * w_gradient)
    return [new_b, new_w]


def gradient_descent_runner(points, starting_b, starting_w, learning_rate, num_iterations):
    b = starting_b
    w = starting_w
    # update for several times
    for i in range(num_iterations):
        b, w = step_gradient(b, w, numpy.array(points), learning_rate)
    return [b, w]


class Fund(object):
    def __init__(self, *args):
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=10))
        s.mount('https://', HTTPAdapter(max_retries=10))
        self.s = s
        self.single_fund = list()
        self.all_fund = list()
        self.fund_relationship = dict()
        self.funds = args
        self.data = None
        self.text = None
        self.datas = dict()
        self.k2 = list()

    def spider_single_fund(self):
        for fund in self.funds:
            sql = f'select fund_code,fund_abbreviation from fund_relationship'
            m = MysqlUtil(sql)
            m.fetchall()
            results = m.results
            dataframe = pandas.DataFrame(results)
            self.fund_relationship = dataframe.set_index(['fund_abbreviation'])['fund_code'].to_dict()
            num = self.fund_relationship.get(fund)
            num = str(num).zfill(6)
            payload = {}
            headers = {
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                'Accept': '*/*',
                'Referer': 'http://fundf10.eastmoney.com/',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cookie': 'qgqp_b_id=21efa4852885689256b2b8b87507bdf9; st_si=38989772358106; HAList=a-sz-000725-%u4EAC%u4E1C%u65B9%uFF21; em_hq_fls=js; st_asi=delete; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND0=null; EMFUND9=11-12 21:13:04@#$%u62DB%u5546%u4E2D%u8BC1%u767D%u9152%u6307%u6570%28LOF%29A@%23%24161725; st_pvi=34688778422262; st_sp=2021-10-28%2017%3A24%3A25; st_inirUrl=https%3A%2F%2Fwww.cnblogs.com%2F; st_sn=9; st_psi=20211112211419409-112200305283-2960355705'
            }
            urls = [
                f"http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18301733888408697981_1636722859420&fundCode={num}&pageIndex={page_number}&pageSize=20&startDate=&endDate=&_=1636723028821 "
                for page_number in range(1, 80)]

            def url_parse(url):
                response = self.s.request("GET", url, headers=headers, data=payload, timeout=5)
                data = response.text
                data = data.strip('jQuery18301733888408697981_1636722859420(')
                data = data.strip(')')
                data = json.loads(data)
                LSJZList = data['Data']['LSJZList']
                LSJZList = [{'净值日期': LSJZ['FSRQ'], '单位净值': float(LSJZ['DWJZ']), '累计净值': LSJZ['LJJZ'], **LSJZ} for LSJZ
                            in
                            LSJZList]
                # LSJZList = [[LSJZ['FSRQ'], LSJZ['DWJZ']] for LSJZ in LSJZList]
                self.single_fund.extend(LSJZList)
            with ThreadPoolExecutor() as pool:
                pool.map(url_parse, urls)

            # self.data = json.dumps(self.single_fund[::-1], ensure_ascii=False)
            self.data = (self.single_fund[::-1])
            pandas.DataFrame(self.data).to_csv(f'./static/data/{fund}.csv', index=False)
            self.text = f'''（净值估算数据按照基金历史披露持仓和指数走势估算，不构成投资建议，仅供参考，实际以基金公司披露净值为准。）
            
            
            
            该基金到目前为止
            申购状态为{self.single_fund[0]['SGZT']}
            赎回状态为{self.single_fund[0]['SHZT']}
            平均单位净值为{sum([float(i['单位净值']) for i in self.single_fund]) / len(self.single_fund)}
            平均累计净值为{sum([float(i['累计净值']) for i in self.single_fund]) / len(self.single_fund)}
            近3月阶段涨幅为{(self.single_fund[0]['单位净值'] - self.single_fund[90]['单位净值']) / self.single_fund[90]['单位净值']}
            近1月阶段涨幅为{(self.single_fund[0]['单位净值'] - self.single_fund[30]['单位净值']) / self.single_fund[30]['单位净值']}
            近1周阶段涨幅为{(self.single_fund[0]['单位净值'] - self.single_fund[7]['单位净值']) / self.single_fund[7]['单位净值']}
            '''

    def spider_fund_relationship(self):
        payload = {}
        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'http://fund.eastmoney.com/fund.html',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'qgqp_b_id=21efa4852885689256b2b8b87507bdf9; st_si=38989772358106; HAList=a-sz-000725-%u4EAC%u4E1C%u65B9%uFF21; em_hq_fls=js; st_asi=delete; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; ASP.NET_SessionId=n3hlzbxzh0qyjs5dqrlkzu0t; _adsame_fullscreen_18186=1; _adsame_fullscreen_18503=1; searchbar_code=161725_001307; EMFUND0=null; EMFUND8=11-12%2022%3A24%3A33@%23%24%u62DB%u5546%u4E2D%u8BC1%u767D%u9152%u6307%u6570%28LOF%29A@%23%24161725; EMFUND9=11-12 22:24:45@#$%u4E2D%u6B27%u6C38%u88D5%u6DF7%u5408C@%23%24001307; st_pvi=34688778422262; st_sp=2021-10-28%2017%3A24%3A25; st_inirUrl=https%3A%2F%2Fwww.cnblogs.com%2F; st_sn=18; st_psi=20211112222445527-112200305282-7065421459'
        }
        for page_number in range(1, 64):
            # print(f'正在爬取第{page_number}页')
            url = f"http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=1&lx=1&letter=&gsid=&text=&sort=zdf,desc&page={page_number},200&dt=1636727136051&atfc=&onlySale=0"
            response = self.s.request("GET", url, headers=headers, data=payload, timeout=5)
            data = response.text
            data = data.strip('var db=')
            data = demjson.decode(data)
            datas = data['datas']
            # datas = [{"基金代码": i[0],
            #           "基金简称": i[1],
            #           "申购状态": i[9],
            #           "赎回状态": i[10]}
            #          for i in datas]
            for data in datas:
                # SQL 插入语句
                sql = f'''INSERT INTO fund_relationship (fund_code,fund_abbreviation,subscription_status,redemption_status)VALUES('{data[0]}','{data[1]}','{data[9]}','{data[10]}');'''
                print(sql)
                m = MysqlUtil(sql)
                m.insert()

    def compare_funds(self):
        for fund in self.funds:
            print(fund)
            sql = f'select fund_code,fund_abbreviation from fund_relationship'
            m = MysqlUtil(sql)
            m.fetchall()
            results = m.results
            dataframe = pandas.DataFrame(results)
            self.fund_relationship = dataframe.set_index(['fund_abbreviation'])['fund_code'].to_dict()
            num = self.fund_relationship.get(fund)
            num = str(num).zfill(6)
            payload = {}
            headers = {
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                'Accept': '*/*',
                'Referer': 'http://fundf10.eastmoney.com/',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cookie': 'qgqp_b_id=21efa4852885689256b2b8b87507bdf9; st_si=38989772358106; HAList=a-sz-000725-%u4EAC%u4E1C%u65B9%uFF21; em_hq_fls=js; st_asi=delete; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND0=null; EMFUND9=11-12 21:13:04@#$%u62DB%u5546%u4E2D%u8BC1%u767D%u9152%u6307%u6570%28LOF%29A@%23%24161725; st_pvi=34688778422262; st_sp=2021-10-28%2017%3A24%3A25; st_inirUrl=https%3A%2F%2Fwww.cnblogs.com%2F; st_sn=9; st_psi=20211112211419409-112200305283-2960355705'
            }
            urls = [
                f"http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18301733888408697981_1636722859420&fundCode={num}&pageIndex={page_number}&pageSize=20&startDate=&endDate=&_=1636723028821 "
                for page_number in range(1, 80)]

            def url_parse(url):
                response = self.s.request("GET", url, headers=headers, data=payload, timeout=5)
                data = response.text
                data = data.strip('jQuery18301733888408697981_1636722859420(')
                data = data.strip(')')
                data = json.loads(data)
                LSJZList = data['Data']['LSJZList']
                LSJZList = [{'净值日期': LSJZ['FSRQ'], '单位净值': LSJZ['DWJZ']} for LSJZ in LSJZList]
                # LSJZList = [[LSJZ['FSRQ'], LSJZ['DWJZ']] for LSJZ in LSJZList]
                self.single_fund.extend(LSJZList)
                self.single_fund.extend(LSJZList)

            with ThreadPoolExecutor() as pool:
                pool.map(url_parse, urls)
            # self.data = json.dumps(self.single_fund[::-1], ensure_ascii=False)
            self.data = (self.single_fund[::-1])
            self.datas[fund] = self.data

    def predict_fund(self):
        predict_data = [[k / 1000, v['单位净值']] for k, v in enumerate(self.data)]
        points = numpy.array(predict_data)
        learning_rate = 0.0001
        initial_b = 0
        initial_w = 0
        num_iterations = 10000
        b, w = gradient_descent_runner(points, initial_b, initial_w, learning_rate, num_iterations)
        self.result = f'迭代{num_iterations}次时,b={b}, w={w}, loss={compute_error_for_line_given_points(b, w, points)}'
        self.k2 = [w * i[0] + b for i in predict_data]  # 线2的纵坐标


if __name__ == '__main__':
    # f = Fund('中欧盛世成长混合(LOF)E', '中欧盛世成长混合(LOF)A')
    # f = Fund('中欧盛世成长混合(LOF)E')
    # f.spider_single_fund()
    # # f.compare_funds()
    # f.predict_fund()
    f=Fund()
    f.spider_fund_relationship()
    pass
