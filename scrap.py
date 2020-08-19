from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

client = MongoClient('localhost', 27017)
db = client.openinfo
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

path = 'C:/Users/YJ/Desktop/sparta/chromedriver'
driver_interpark = webdriver.Chrome(path, options=options)
driver_yes24 = webdriver.Chrome(path, options=options)
url_interpark = 'http://ticket.interpark.com/webzine/paper/TPNoticeList.asp#'
url_yes24 = 'http://ticket.yes24.com/New/Notice/NoticeMain.aspx'

driver_interpark.get(url_interpark)
driver_yes24.get(url_yes24)
driver_interpark.switch_to.frame('iFrmNotice')

frm_interpark = driver_interpark.page_source
source_yes24 = driver_yes24.page_source
# time.sleep(2)

soup_interpark = BeautifulSoup(frm_interpark, 'html.parser')
soup_yes24 = BeautifulSoup(source_yes24, 'html.parser')
fulldata_interpark = soup_interpark.select('div.section_notice > div.board > div.list > div.table > table > tbody > tr')
fulldata_yes24 = soup_yes24.select('#NoticeMainDisplay > div#BoardList > div.noti-tbl > table > tbody > tr')

# for data in fulldata_interpark:
#     type = data.select_one('td.type').text
#     if type == '뮤지컬' or type == '연극':
#         data.append('----------interpark')
#         print(data)


for data in fulldata_yes24:
    type = data.select_one('td:nth-child(1)')
    if type is not None:
        type = data.select_one('td:nth-child(1)').text.strip()
        url = data.select_one('td:nth-child(2)')
        a_tag = data.select_one('td:nth-child(2) > a')
        ticket_open_time = data.select_one('td:nth-child(3)').text.strip()
        find_string = ['뮤지컬', '연극']
        title = ''
        param = ''
        exclusive_sale = ''
        full_url = []
        if type == '티켓오픈':
            if a_tag is not None:
                param = a_tag['href']
                span = a_tag.select_one('em:nth-child(1) > span')
                # print(param)
                if span is not None:
                    title = data.select_one('em:nth-child(2)')
                    exclusive_sale = span.text
                else:
                    span2 = ''
                    title = data.select_one('em:nth-child(1)')

                for str in find_string:
                    if title.text.find(str) != -1:
                        full_url.append(url_yes24)
                        full_url.append(param)
                        full_url = ''.join(full_url)
                        print(full_url, type, ticket_open_time, exclusive_sale, title.text)


driver_interpark.quit()
driver_yes24.quit()
