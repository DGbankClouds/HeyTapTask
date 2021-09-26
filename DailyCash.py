# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/12
# @Author  : MashiroF
# @File    : DailyCash.py
# @Software: PyCharm

'''
cron:  30 5,12 * * * DailyCash.py
new Env('欢太每日现金');
'''

import os
import re
import sys
import time
import json
import random
import logging

# 日志模块
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logFormat = logging.Formatter("%(message)s")

# 日志输出流
stream = logging.StreamHandler()
stream.setFormatter(logFormat)
logger.addHandler(stream)

# 日志录入时间
logger.info(f"任务:{'任务中心'}\n时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")

# 第三方库
try:
    import requests
except ModuleNotFoundError:
    print("缺少requests依赖！程序将尝试安装依赖！")
    os.system("pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple")
    os.execl(sys.executable, 'python3', __file__, *sys.argv)

# 检测配置文件是否已下载(云函数不适用)
try:
    if not os.path.exists('HT_config.py'):
        logger.info('配置文件不存在,尝试进行下载...')
        url = 'https://ghproxy.com/https://raw.githubusercontent.com/Mashiro2000/QL_HeyTap/main/HT_config.py'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52'
        }
        configText = requests.get(url=url,headers=headers).content.decode('utf8')
        with open(file= 'HT_config.py',mode='w',encoding='utf-8') as fc:
            fc.write(configText)
        logger.info('下载命令执行完毕!')
        logger.info('请根据导航进行配置')
        logger.info('青龙面板 -> 脚本管理 -> 搜索`HT_config`关键字 -> 编辑')
        time.sleep(3)
        sys.exit(0)
except:
    url = 'https://ghproxy.com/https://raw.githubusercontent.com/Mashiro2000/QL_HeyTap/main/HT_config.py'
    logger.info('请手动下载配置文件到当前目录')
    time.sleep(3)
    sys.exit(0)

# 配置文件
try:
    logger.info('尝试导入本地欢太CK...')
    from HT_config import accounts,text
    logger.info(text)
    lists = accounts
except:
    logger.info('本地欢太CK不存在')
    lists = []

class DailyCash:
    def __init__(self,dic):
        self.dic = dic
        self.sess = requests.session()

    # 登录验证
    def login(self):
        url = 'https://store.oppo.com/cn/oapi/users/web/member/check'
        headers = {
            'Host': 'store.oppo.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        response = self.sess.get(url=url,headers=headers).json()
        if response['code'] == 200:
            logger.info(f"{self.dic['user']}\t登录成功")
            return True
        else:
            logger.info(f"{self.dic['user']}\t登录失败")
            return False

    # 浏览商品
    def viewGoods(self, count,flag,dic=None):
        headers = {
            'clientPackage': 'com.oppo.store',
            'Host': 'msec.opposhop.cn',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'User-Agent': 'okhttp/3.12.12.200sp1',
            'Accept-Encoding': 'gzip'
        }
        result = self.getGoodMess(count=count)    # 秒杀列表存在商品url
        if result['meta']['code'] == 200:
            for each in result['detail']:
                url = f"https://msec.opposhop.cn/goods/v1/info/sku?skuId={each['skuid']}"
                self.sess.get(url=url,headers=headers)
                logger.info(f"正在浏览商品id:{each['skuid']}...")
                time.sleep(random.randint(7,10))
            if flag == 1:     # 来源天天领现金
                self.getCash(dic=dic)

    # 分享商品
    def shareGoods(self, flag,count,dic=None):
        url = 'https://msec.opposhop.cn/users/vi/creditsTask/pushTask'
        headers = {
            'clientPackage': 'com.oppo.store',
            'Host': 'msec.opposhop.cn',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'User-Agent': 'okhttp/3.12.12.200sp1',
            'Accept-Encoding': 'gzip',
        }
        params = {
            'marking': 'daily_sharegoods'
        }
        for i in range(count + random.randint(1,3)):
            self.sess.get(url=url,headers=headers,params=params)
            logger.info(f"正在执行第{i+1}次微信分享...")
            time.sleep(random.randint(7,10))
        if flag == 1: #来源天天赚钱
            self.getCash(dic=dic)

    # 秒杀详情页获取商品数据
    def getGoodMess(self,count=10):
        taskUrl = f'https://msec.opposhop.cn/goods/v1/SeckillRound/goods/{random.randint(100,250)}'    # 随机商品
        headers = {
            'clientPackage': 'com.oppo.store',
            'Host': 'msec.opposhop.cn',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'User-Agent': 'okhttp/3.12.12.200sp1',
            'Accept-Encoding': 'gzip',
        }
        params = {
            'pageSize':count + random.randint(1,3)
        }
        response = self.sess.get(url=taskUrl,headers=headers,params=params).json()
        if response['meta']['code'] == 200:
            return response
        else:
            logger.info(response)

    def getCash(self,dic):
        url = 'https://store.oppo.com/cn/oapi/omp-web/web/dailyCash/drawReward'
        headers = {
            'Host': 'store.oppo.com',
            'Connection': 'keep-alive',
            'Origin': 'https://store.oppo.com',
            'source_type': '501',
            'clientPackage': 'com.oppo.store',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://store.oppo.com/cn/app/cashRedEnvelope?activityId=1&us=shouye&um=xuanfu&uc=xianjinhongbao',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.9'
        }
        data = {
            'activityId':1,
            'channel':3,
            'channelRewardId':dic['id']
        }
        response = self.sess.post(url=url,headers=headers,data=data).json()
        if response['code'] == 200:
            logger.info(f"[{dic['taskName']}]\t{response['data']['amount']}")
        elif response['code'] == 1000001:
            logger.info(f"[{dic['taskName']}]\t{response['errorMessage']}")

    # 天天领取现金
    def getDailyCashTask(self):
        url = 'https://store.oppo.com/cn/oapi/omp-web/web/dailyCash/queryActivityReward'
        headers = {
            'Host': 'store.oppo.com',
            'Connection': 'keep-alive',
            'source_type': '501',
            'clientPackage': 'com.oppo.store',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://store.oppo.com/cn/app/cashRedEnvelope?activityId=1&us=shouye&um=xuanfu&uc=xianjinhongbao',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.9'
        }
        params = {
            'activityId':1
        }
        response = self.sess.get(url=url,headers=headers,params=params).json()
        if response['code'] == 200:
            self.taskRewardList = response['data']['taskRewardList']
            self.timingRewardList = response['data']['timingRewardList']
            return True
        elif response['code'] == 1000001:
            logger.info(response['errorMessage'])
            return False

    # 天天领现金浏览模板
    def viewCashTask(self,dic):
        url = 'https://store.oppo.com/cn/oapi/credits/web/dailyCash/reportDailyTask'
        param = {
            'taskType':dic['taskType'],
            'taskId':f"dailyCash{dic['id']}"
        }
        headers = {
            'Host': 'store.oppo.com',
            'Connection': 'keep-alive',
            'source_type': '501',
            'clientPackage': 'com.oppo.store',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://store.oppo.com/cn/app/cashRedEnvelope?activityId=1&us=shouye&um=xuanfu&uc=xianjinhongbao',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.9'
        }
        response = self.sess.get(url=url,headers=headers,params=param).json()
        if response['code'] == 200:
            logger.info(f"正在执行{dic['taskName']}...")
            time.sleep(random.randint(5,7))
            self.getCash(dic=dic)
        else:
            logger.info(f"{dic['taskName']}执行失败")


    def runTaskRewardList(self):
        for each in self.taskRewardList:
            if each['taskName'] == '浏览商品':
                if each['taskStatus'] == 0:
                    self.viewGoods(count=6,flag=1,dic=each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            elif each['taskName'] == '浏览秒杀专区':
                if each['taskStatus'] == 0:
                    self.viewCashTask(each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            elif each['taskName'] == '分享商品':
                if each['taskStatus'] == 0:
                    self.shareGoods(count=2,flag=1,dic=each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            elif each['taskName'] == '观看直播':
                if each['taskStatus'] == 0:
                    self.viewCashTask(each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            elif each['taskName'] == '浏览签到页':
                if each['taskStatus'] == 0:
                    self.viewCashTask(each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            if each['taskName'] == '浏览领券中心':
                if each['taskStatus'] == 0:
                    self.viewCashTask(each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            elif each['taskName'] == '浏览realme商品':
                if each['taskStatus'] == 0:
                    self.viewCashTask(each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            elif each['taskName'] == '浏览指定商品':
                if each['taskStatus'] == 0:
                    self.viewCashTask(each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            elif each['taskName'] == '浏览一加商品':
                if each['taskStatus'] == 0:
                    self.viewCashTask(each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")
            elif each['taskName'] == '浏览OPPO商品':
                if each['taskStatus'] == 0:
                    self.viewCashTask(each)
                elif each['taskStatus'] == 1:
                    self.getCash(dic=each)
                elif each['taskStatus'] == 2:
                    logger.info(f"{each['taskName']}\t已领取")

    # pushPlus配信
    @staticmethod
    def sendForPush():
        if [each for each in admin['mask'] if each == os.path.basename(__file__)[:-3]] == []:
            with open(file=LOG_FILE,mode='r',encoding='utf-8') as f:
                content = f.read()
            url = 'http://www.pushplus.plus/send'
            data = {
                "token": admin['pushGroup']['pushToken'],
                "title":"欢太任务通知",
                "content":content,
                "template":"txt"
            }
            if admin['pushGroup']['pushToken'] != "":
                if admin['pushGroup']['pushTopic'] != "":
                    data['topic'] = admin['pushGroup']['pushTopic']
                response = requests.post(url=url,data=json.dumps(data)).json()
                if response['code'] == 200:
                    logger.info(f"Push Plus发信成功！\n")
                else:
                    logger.info(f"Push Plus发信失败！\t失败原因:{response['msg']}")
            else:
                logger.info("未配置pushPlus Token,取消配信！")
        else:
            logger.info(f"{os.path.basename(__file__)[:-3]}\t发信功能被屏蔽")

    # 执行欢太商城实例对象
    def start(self):
        self.sess.headers.update({
            "User-Agent":self.dic['UA']
        })
        self.sess.cookies.update({
            "Cookie": self.dic['CK']
        })
        if self.login() == True:
            if self.getDailyCashTask() == True:         # 获取天天领现金数据，判断CK是否正确(登录可能成功，但无法跑任务)
                self.runTaskRewardList()                # 运行天天领现金
            logger.info('*' * 40 + '\n')

# 检测CK是否存在必备参数
def checkHT(string):
    if len(re.findall(r'source_type=.*?;',string)) == 0:
        logger.info('CK格式有误:可能缺少`source_type`字段')
        return False
    if len(re.findall(r'TOKENSID=.*?;',string)) == 0:
        logger.info('CK格式有误:可能缺少`TOKENSID`字段')
        return False
    if len(re.findall(r'app_param=.*?[;]?',string)) == 0:
        logger.info('CK格式有误:可能缺少`app_param`字段')
        return False
    return True

# # 格式化设备信息Json
# # 由于青龙的特殊性,把CK中的 app_param 转换未非正常格式，故需要此函数
# def transform(string):
#     dic2 = {}
#     dic1 = eval(string)
#     for i in dic1['app_param'][1:-1].split(','):
#         dic2[i.split(':')[0]] = i.split(':')[-1]
#     if dic1['CK'][-1] != ';':
#         dic1['CK'] = dic1['CK'] + ';'
#     dic1['CK'] = dic1['CK'] + f"app_param={json.dumps(dic2,ensure_ascii=False)}"
#     dic1['CK'] = checkHT(dic1['CK'])
#     return dic1

# # 读取青龙CK
# def getEnv(key):
#     lists2 = []
#     logger.info("尝试导入青龙面板CK...")
#     variable = os.environ.get(key)
#     if variable == None:
#         logger.info("青龙面板环境变量 TH_COOKIE 不存在！")
#     else:
#         for each in variable.split('&'):
#             result = transform(each)
#             if result:
#                 lists2.append(result)
#     return lists2

# 兼容云函数
def main(event, context):
    global lists
    for each in lists:
        if all(each.values()):
            if checkHT(each['CK']):
                dailyCash = DailyCash(each)
                for count in range(3):
                    try:
                        time.sleep(random.randint(2,5))    # 随机延时
                        dailyCash.start()
                        break
                    except requests.exceptions.ConnectionError:
                        logger.info(f"{dailyCash.dic['user']}\t请求失败，随机延迟后再次访问")
                        time.sleep(random.randint(2,5))
                        continue
                else:
                    logger.info(f"账号: {dailyCash.dic['user']}\n状态: 取消登录\n原因: 多次登录失败")
                    break

if __name__ == '__main__':
    main(None,None)