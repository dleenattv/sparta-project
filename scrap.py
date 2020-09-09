import schedule
import time
import re

from selenium import webdriver
from bs4 import BeautifulSoup

from pymongo import MongoClient

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

client = MongoClient('mongodb://test:test@13.125.119.199', 27017)
# client = MongoClient('localhost', 27017)
db = client.ticketProject

# selenium 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

# path = '/home/ubuntu/sparta-project/chromedriver'
path = 'C://Users/YJ/Desktop/sparta/sparta-project/chromedriver.exe'


def get_interpark_info():
    driver_interpark = webdriver.Chrome(path, options=options)
    url_interpark = 'http://ticket.interpark.com/webzine/paper/TPNoticeList.asp#'
    driver_interpark.get(url_interpark)
    driver_interpark.switch_to.frame('iFrmNotice')
    frm_interpark = driver_interpark.page_source
    soup_interpark = BeautifulSoup(frm_interpark, 'html.parser')
    fulldata_interpark = soup_interpark.select(
        'div.section_notice > div.board > div.list > div.table > table > tbody > tr')

    for data in fulldata_interpark:
        type = data.select_one('td.type').text
        url = data.select_one('td.subject > a')['href']
        title = data.select_one('td.subject > a').text
        ticket_open_time = data.select_one('td.date').text
        detail_url = []
        if type == '뮤지컬' or type == '연극':
            detail_url.append('http://ticket.interpark.com/webzine/paper/')
            detail_url.append(url)
            detail_url = ''.join(detail_url)
            driver_interpark.get(detail_url)
            soup_interpark = BeautifulSoup(driver_interpark.page_source, "html.parser")

            # 티켓오픈 게시글 내용 스크래핑 (상단)
            detail_top = soup_interpark.select(
                '#wrapBody > div > div > div.board > div.detail_top > div.info')
            exclusive_sale = ''
            poster = ''
            reserve_url = ''

            for top in detail_top:
                poster = top.select_one('span.poster > img')['src']
                reserve_url = top.select_one('div.btn > a.btn_book')
                if reserve_url is not None:
                    reserve_url = top.select_one('div.btn > a.btn_book')['href']
                else:
                    reserve_url = ''

                additional_info = top.select_one('h3 > span')
                # print(time.strftime('%y%m%d%H%M', time.localtime(time.time())))
                # print(replaceTimeFormat(ticket_open_time))
                for a_info in additional_info:
                    if a_info == '단독판매':
                        exclusive_sale = a_info

            # 티켓오픈 게시글 내용 스크래핑 (하단/내용)
            detail_cont = soup_interpark.select('#wrapBody > div > div > div.board > div.desc')
            for detail in detail_cont:
                summary = detail.select_one('div.introduce > div.data > p')
                discount_info = detail.select_one('div.info_discount > div.data > p')
                content = detail.select_one('div.info1 > div.data > p')
                cast_company = detail.select('div.info2 > div.data > p')
                cast = ''
                company = ''
                for idx, str in enumerate(cast_company):
                    if idx == 0:
                        cast = str
                    if idx == 1:
                        company = str

                print(title)
                print(cast)
                print(company)
            # print(title, exclusive_sale, ticket_open_time, poster, reserve_url)

    driver_interpark.quit()


def get_yes24_info(ids):
    driver_yes24 = webdriver.Chrome(path, options=options)
    url_yes24 = f'{"http://ticket.yes24.com/New/Notice/NoticeMain.aspx#page="}{ids}'
    main_yes24 = "http://ticket.yes24.com/New/Notice/NoticeMain.aspx"
    print(url_yes24)
    time.sleep(2)
    driver_yes24.get(url_yes24)
    source_yes24 = driver_yes24.page_source
    soup_yes24 = BeautifulSoup(source_yes24, 'html.parser')
    fulldata_yes24 = soup_yes24.select('#NoticeMainDisplay > div#BoardList > div.noti-tbl > table > tbody > tr')

    for data in fulldata_yes24:
        type = data.select_one('td:nth-child(1)')
        if type is not None:
            type = data.select_one('td:nth-child(1)').text.strip()
            url = data.select_one('td:nth-child(2)')
            a_tag = data.select_one('td:nth-child(2) > a')
            ticket_open_time = data.select_one('td:nth-child(3)').text.strip()

            find_string = ['뮤지컬', '연극']
            title = ''
            exclusive_sale = ''
            full_url = []
            img_url = ''
            title_list = []

            if type == '티켓오픈':
                if a_tag is not None:
                    param = a_tag['href']
                    span = a_tag.select_one('em:nth-child(1) > span')
                    if span is not None:
                        out_title = data.select_one('em:nth-child(2)')
                        exclusive_sale = span.text
                    else:
                        out_title = data.select_one('em:nth-child(1)')

                    for str in find_string:
                        if out_title.text.find(str) != -1:
                            full_url.append(main_yes24)
                            full_url.append(param)
                            full_url = ''.join(full_url)
                            # 내부 크롤링
                            driver_yes24.get(full_url)
                            soup_yes24 = BeautifulSoup(driver_yes24.page_source, "html.parser")
                            detail_top = soup_yes24.select(
                                '#NoticeRead > div.noti-view-ticket > div.noti-vt-layout')
                            for data in detail_top:
                                title = data.select_one('div.noti-vt-right > p.noti-vt-tit')
                                img_url = data.select_one('div.noti-vt-left > img')['src']
                                span_elements = title.find_all("span")

                                for span in span_elements:
                                    span.extract()

                            yes24_doc = {
                                'title': title.text,
                                'link': full_url,
                                'img_url': img_url,
                                'type': type,
                                'open_time': ticket_open_time,
                                'exclusive_sale': exclusive_sale
                            }

                            db.openinfo.insert_one(yes24_doc)
                            print(title.text)
                            # print(full_url, type, ticket_open_time, exclusive_sale)
                            # print(img_url)

    driver_yes24.quit()


def replace_time_format(time):
    pattern = re.compile(r'\s+')
    time = re.sub('[.:()월화수목금토일]', '', time)
    time = re.sub(pattern, '', time)

    return time


def send_mail():
    get_day = time.strftime('%Y%m%d%H', time.localtime(time.time()))
    # test_day = '2020090201'
    msg_detail = []
    tmp_info = []
    # for Server
    print(get_day[8:])

    if get_day[8:] == '01':
        open_info = list(db.openinfo.find({}, {'_id': 0}).sort('open_time', 1))

        for info in open_info:
            open_time = info['open_time']

            open_time = replace_time_format(open_time)[0:8]
            if get_day[0:8] == open_time:
                open_title = info['title']
                img = info['img_url']
                data = {
                    'title': open_title,
                    'img': img
                }
                tmp_info.append(data)

                # print(reserv_title)
                # print(test_day, open_time)
                # print(len(reserv_title))
        print(tmp_info)
        if len(tmp_info) > 0:
            full_email = list(db.requestEmails.find({}, {'_id': 0}))
            for info in tmp_info:
                for saved_mail in full_email:
                    subject = []
                    admin_mail = 'maildontforget@gmail.com'
                    admin_pw = 'uazigsftmztmwiwr'
                    receiver_mail = saved_mail['email']

                    msg = MIMEMultipart('alternative')

                    subject.append('티켓오픈 알림 :: ')
                    subject.append(info['title'])
                    msg['Subject'] = ''.join(subject)
                    msg['From'] = admin_mail
                    msg['To'] = receiver_mail
                    print(info['title'])
                    msg_detail.append('<div style="margin:auto;text-align:center;"><h2>안녕하세요.<br/>')
                    msg_detail.append('오늘의 티켓오픈 정보를 전달드립니다.<br/>')
                    msg_detail.append('잊지말고 티켓팅하세요 :)<br/></h2>')
                    msg_detail.append('<div><img width="200px" src="')
                    msg_detail.append(info['img'])
                    msg_detail.append('"></div><br/><font size="4px">')
                    msg_detail.append(info['title'])
                    msg_detail.append('</font><br/><br/>')
                    # msg_detail.append('예매하러 가기 ▶ ')
                    # msg_detail.append('http://dailyticketopen.shop')
                    msg_detail.append('<a style="font-size: 18px;font-weight:bold;padding: 12px 18px;margin-bottom: 0;'
                                      'display: inline-block;text-decoration: none;text-align: center;'
                                      'white-space: nowrap;vertical-align: middle;-ms-touch-action: manipulation;'
                                      'touch-action: manipulation;cursor: pointer;-webkit-user-select: none;'
                                      '-moz-user-select: none;-ms-user-select: none;user-select: none;background-image: none;'
                                      'border: 1px solid transparent;color: #fff;background-color: #1777ff;border-color: #fff;border-radius:5px;" '
                                      'href="http://dailyticketopen.shop" role="button">예매하러 가기</a></div>')

                    msg_cont = ''.join(msg_detail)
                    mail_type = MIMEText(msg_cont, 'html')
                    del msg_detail[0:len(msg_detail)]
                    print(msg_cont)
                    msg.attach(mail_type)

                    mail_service = smtplib.SMTP_SSL('smtp.gmail.com')
                    mail_service.login(admin_mail, admin_pw)
                    mail_service.sendmail(admin_mail, receiver_mail, msg.as_string())
                    mail_service.quit()
                    print(receiver_mail, 'MAIL SEND DONE')


def job():
    # get_interpark_info()
    db.openinfo.remove({})
    get_yes24_info(1)
    get_yes24_info(2)
    send_mail()


def run():
    # On Server
    # schedule.every(1).hours.do(job)
    # For Test
    schedule.every(30).seconds.do(job)
    while True:
        schedule.run_pending()


if __name__ == "__main__":
    # run()
    job()

# time.sleep(2)
