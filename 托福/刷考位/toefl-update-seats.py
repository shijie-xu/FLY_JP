#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 15:23:39 2020

@author: shijie
"""

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import json
from retry import retry
import requests
import datetime
from twilio.rest import Client

# this function need API Keys from Twillo, please confirm that you have a valid one.
def send_sms():
    token = '8180220f6a55755e0a0f5e3fec0d98e0'
    sid = 'ACb241bbb83fa61c39973969c0e30f847e'
    client = Client(sid,token)
    msg = client.messages.create(to='+8615056932298',from_='+12172804097',body='发现新的考位，请速查邮件！')

def send_mail(title, content):
    from email.mime.text import MIMEText
    from email.header import Header
    from smtplib import SMTP_SSL
    
    host_server = r'smtp.qq.com'
    sender_qq = '<Your QQ Number (recommended)>'
    pwd = '<QQ Verified Code>'
    sender_qq_mail = '<Your QQ Number>@qq.com'
    receiver = sender_qq_mail
    mail_content = content
    mail_title = title
    
    smtp = SMTP_SSL(host_server)
    smtp.set_debuglevel(1)
    smtp.ehlo(host_server)
    smtp.login(sender_qq, pwd)
    
    msg = MIMEText(mail_content, 'plain', 'utf-8')
    msg['Subject'] = Header(mail_title, 'utf-8')
    msg['From'] = sender_qq_mail
    msg['To'] = receiver
    smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
    smtp.quit()

def notify_in_ubuntu(title, content):
    from gi.repository import Notify
    Notify.init("TOEFL SEATS QUERY")
    Notify.Notification.new(title, content).show()

driver = webdriver.Firefox(executable_path="geckodriver")

@retry(max_delay=10)
def query_js(code):
    return driver.execute_script(js_query)

# ====== login in ==========
login_url = r'https://toefl.neea.cn/login'
driver.get(login_url)
time.sleep(5)
driver.find_element_by_id('userName').send_keys('<Your NEEA ID>')
driver.find_element_by_id('textPassword').send_keys('<You NEEA Password>')
for i in range(10):
    print('\r[loading] escaped time: %d s' % i, end='')
    time.sleep(1)
# print(driver.page_source)

# ------ run js to get JSON ------
js_testDays = r'return $.getJSON("testDays")'
js_testCenter = r'return $.getJSON("/getTestCenterProvinceCity")'
days_list = list(driver.execute_script(js_testDays))
centers_list = list(driver.execute_script(js_testCenter))
driver.get(r'https://toefl.neea.cn/myHome/<Your ID>/index#!/testSeat')


#cities = [x['cityNameEn'] for prov in centers_list for x in prov['cities']]
# cities = ['HEFEI', 'SUZHOU', 'NANJING', 'BEIJING']
#cities = ['HEFEI']
cities = ['SHANGHAI', 'BEIJING', 'DONGGUAN', 'SHENZEHN', 'NINGBO','SUZHOU', 'CHANGZHOU', 'XUZHOU', 'YANGZHOU', 'HANGZHOU', 'XIAN', 'LANZHOU', 'JINAN', 'WEIFANG']
earliest_date = datetime.datetime.strptime('2020-12-30', '%Y-%m-%d')
start_date = datetime.datetime.strptime('2020-8-1', '%Y-%m-%d')
end_date = datetime.datetime.strptime('2020-9-30', '%Y-%m-%d')

# define procedure to execute query
def update_seats():
    while True:
        pass
    
    
while True:
    IMPORTANT_MSG = False    
    begin = time.time()
    # ------ open query page --------
    print("\nrefreshing seats information....")
    try:
        time.sleep(0.5)    
        dlg_alert = driver.switch_to.alert.accept()
    except:
        pass

    # ------ query seats ------------
    seats_list = {}
    idx = 0
    for city in cities:
        idx+=1
        for day in days_list:
            date_day = datetime.datetime.strptime(day, '%Y-%m-%d')
            if date_day < start_date or date_day > end_date:
                continue
            print('\r[%d/%d] querying seats in %s, %s' % (idx, len(cities), city, day), end='')
            
            # query js
            js_query = r'return $.getJSON("testSeat/queryTestSeats",{city: "%s",testDay: "%s"});' %(city, day)
            query_results = query_js(js_query)
            if query_results['status'] == True:
                for seats in query_results['testSeats'].values():
                    for seat in seats:
                        if seat['seatBookStatus'] !=0 or seat['seatStatus'] != 0:
                            title = '%s' %(day)
                            content = seat['centerNameCn'] +', '+seat['cityCn']+ ', '+seat['provinceCn']
                            if not title in seats_list:
                                seats_list[title] = content
                            else:
                                seats_list[title] = seats_list[title] + '\n'+ content
                            print('\n\033[1;32;43m[seat found, %s.]\033[0m' % day, end='')
                            cur_date = datetime.datetime.strptime(title, '%Y-%m-%d') 
                            if cur_date < earliest_date:
                                earliest_date = cur_date
                                IMPORTANT_MSG = True
                        else:
                            print('\n[no seats remained.]', end='')
    content = ''
    for item in sorted(seats_list):
        content += item +'\n' + seats_list[item] +'\n\n' 
        
    print('\n=============== QUERY END ===============\n')
    title = '托福考位查询结果-%d分钟前查询' % ((time.time() - begin)/60)
    if content != '':
        if IMPORTANT_MSG == True:
            send_mail(title, content)
            notify_in_ubuntu(title, content)
            send_sms()
        else:
            print("\n=========== NO EARLIER SEATS =========\n")
    # driver.refresh()
    time.sleep(5)
