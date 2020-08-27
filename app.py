from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import time
import re

app = Flask(__name__)

client = MongoClient('mongodb://test:test@13.125.119.199', 27017)
# client = MongoClient('localhost', 27017)
db = client.ticketProject


## HTML 화면 보여주기
@app.route('/')
def homework():
    return render_template('index.html')


# 주문하기(POST) API
# @app.route('/order', methods=['POST'])
# def save_order():
#     recv_name = request.form['send_name']
#     recv_count = request.form['send_count']
#     recv_addr = request.form['send_addr']
#     recv_tel = request.form['send_tel']
#
#     send_info = {
#         'orderName': recv_name,
#         'orderCount': recv_count,
#         'orderAddr': recv_addr,
#         'orderTel': recv_tel
#     }
#     db.dbhomework2.insert_one(send_info)
#
#     return jsonify({'result': 'success'})


# 주문 목록보기(Read) API
@app.route('/ticketOpen', methods=['GET'])
def view_ticket_open():
    full_info = list(db.openinfo.find({}, {'_id': 0}).sort('open_time', 1))
    now = time.strftime('%Y%m%d%H', time.localtime(time.time()))
    #now_time = time.localtime(time.time())
    open_info = list()
    print(now)

    for element in full_info:
        open_time = replaceTimeFormat(element['open_time'])
        print(open_time)
        if open_time >= now:
            open_info.append(element)

    #print(now)
    print(len(full_info))

    return jsonify({'open_info': open_info})


def replaceTimeFormat(time_str):
    pattern = re.compile(r'\s+')
    time_str = re.sub('[.:()월화수목금토일]', '', time_str)
    time_str = re.sub(pattern, '', time_str)
    time_str = time_str[:10]

    return time_str


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
