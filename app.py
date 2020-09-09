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
def show_index():
    return render_template('index.html')


@app.route('/ticketOpen', methods=['POST'])
def save_emails():
    recv_email = request.form['req_email']
    saved_emails = list(db.requestEmails.find({'email': recv_email}, {'_id': 0}))
    find_count = 0
    print(saved_emails)
    if len(saved_emails) > 0:
        for mail in saved_emails:
            print(find_count)
            print(mail['email'], recv_email)

            if mail['email'] == recv_email:
                find_count += 1
                result = 'overlap'
                return jsonify({'result': result})
    else:
        if find_count == 0:
            db.requestEmails.insert_one({'email': recv_email})
            result = 'success'
            return jsonify({'result': result})


@app.route('/ticketOpen', methods=['GET'])
def view_ticket_open():
    full_info = list(db.openinfo.find({}, {'_id': 0}).sort('open_time', 1))
    now = time.strftime('%Y%m%d%H', time.localtime(time.time()))
    open_info = list()

    for element in full_info:
        open_time = replace_time_format(element['open_time'])
        if open_time >= now:
            open_info.append(element)

    print(open_info)
    return jsonify({'open_info': open_info})


def replace_time_format(time_str):
    pattern = re.compile(r'\s+')
    time_str = re.sub('[.:()월화수목금토일]', '', time_str)
    time_str = re.sub(pattern, '', time_str)
    time_str = time_str[:10]

    return time_str


if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)
    # app.run('0.0.0.0', port=5000, debug=True)
