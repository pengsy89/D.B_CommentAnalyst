# -*- encoding:utf-8 -*-
 
import requests
from bs4 import BeautifulSoup
import re
import random
import time
 
#使用session来保存登陆信息
s = requests.session()
 
#获取动态ip，防止ip被封
def get_ip_list(url, headers):
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list
#随机从动态ip链表中选择一条ip
def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://' + ip)
    proxy_ip = random.choice(proxy_list)
    proxies = {'http': proxy_ip}
    return proxies
 
#实现模拟登陆
def Login(headers,loginUrl,formData):
    r = s.post(loginUrl, data=formData, headers=headers)
    print (r.url)
    print (formData["redir"])
    if r.url == formData["redir"]:
        print ("登陆成功")
    else:
        print ("第一次登陆失败")
        page = r.text
        soup = BeautifulSoup(page, "html.parser")
        captchaAddr = soup.find('img', id='captcha_image')['src']
        print (captchaAddr)
 
        reCaptchaID = r'<input type="hidden" name="captcha-id" value="(.*?)"/'
        captchaID = re.findall(reCaptchaID, page)
 
        captcha = raw_input('输入验证码：')
 
        formData['captcha-solution'] = captcha
        formData['captcha-id'] = captchaID
 
        r = s.post(loginUrl, data=formData, headers=headers)
        print (r.status_code)
        return r.cookies
#获取评论内容和下一页链接
def get_data(html):
    # soup = BeautifulSoup(html,"lxml")
    soup = BeautifulSoup(html,"html.parser")
    comment_list=[]
    comment_div_list = soup.find_all("div",class_="comment")
    for item in comment_div_list:
        comment_dict={}
        #if t in range(0,50,10): 
        item_score = item.find_all("h3")[0]
        item_score = item_score.find_all("span")[4]
        comment_dict["得分"]=(str)(item_score["class"])
        ret= re.findall(r"u'allstar(.*?)0', u'rating'", (str)(item_score["class"]))
        # comment_dict["评级"]=item_score["title"]
        if len(ret) > 0:
            comment_list.append(ret[0])
    print (comment_list)
    # comment_list = soup.select('.comment > .rating')
    next_page = soup.select('.next')[0].get('href')
    return comment_list,next_page
 
if __name__ =="__main__":
    absolute = 'https://movie.douban.com/subject/27089387/comments'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
    loginUrl = 'https://www.douban.com/accounts/login?source=movie'
    formData = {
        "redir":"https://movie.douban.com/subject/27089387/comments?start=201&limit=20&sort=new_score&status=P&percent_type=",
        "form_email":"",
        "form_password":"",
        "login":u'登录'
    }
    #获取动态ip
    url = 'http://www.xicidaili.com/nn/'
    cookies = Login(headers,loginUrl,formData)
    # ip_list = get_ip_list(url, headers=headers)
    ip_list=["1111"]
    proxies = get_random_ip(ip_list)
 
    current_page = absolute
    next_page = ""
    comment_list = []
    temp_list = []
    num = 0

    while(1):
        html = s.get(current_page, cookies=cookies, headers=headers).content.decode("UTF-8")
        temp_list,next_page = get_data(html)
        if next_page is None:
            break
        current_page = absolute + next_page
        comment_list = comment_list + temp_list
        #time.sleep(1 + float(random.randint(1, 100)) / 20)
        num = num + 1
        #每20次更新一次ip
        if num % 20 == 0:
            proxies = get_random_ip(ip_list)
        print (current_page)
    #将爬取的评论写入txt文件中
    with open("D:/Code/D.B_CommentAnalyst/D.B_CommentAnalyst/output/d1.txt", 'a')as f:
        for node in comment_list:
            comment = (str)(node)
            f.write(comment + "\n")
    f.close()
