from flask import Flask,render_template,session
from flask_wtf import FlaskForm
from wtforms import SubmitField,IntegerField,DateTimeField
from flask_bootstrap import Bootstrap
from gevent import monkey
from gevent.pywsgi import WSGIServer
import RPi.GPIO as GPIO
import time,datetime
import pydblite

monkey.patch_all()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rp'
bootstrap = Bootstrap(app)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12,GPIO.OUT)

db = pydblite.Base(':memory:')
db.create('state')

class Func():
    @staticmethod
    def appointment_time_ConvertTo_seconds(appmnt):
        appointment = datetime.datetime.strptime(str(appmnt), "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        t = appointment - now
        return int(t.total_seconds())

    @staticmethod
    def output(bool):
        GPIO.output(12, bool)

class SwitchForm(FlaskForm):
    minute_open = IntegerField('分钟')
    date_open = DateTimeField('时间')
    appointment_opening = SubmitField('预约开')

    minute_close = IntegerField('分钟')
    date_close = DateTimeField('时间')
    appointment_closing = SubmitField('预约关')

    minute_loop_open = IntegerField('开(分钟)')
    minute_loop_close = IntegerField('关(分钟)')
    loop = SubmitField('循环')
    exit_loop = SubmitField('退出循环')

    on = SubmitField('常开')
    off = SubmitField('常关')


@app.route('/',methods=['GET','POST'])
def index():
    form = SwitchForm()
    if form.on.data:
        Func.output(False)

    if form.off.data:
        Func.output(True)

    if form.appointment_opening.data:
        open_minute = form.minute_open.data
        open_datetime = form.date_open.data
        if open_minute:
            time.sleep(open_minute*60)
            Func.output(False)
        if open_datetime:
            t = Func.appointment_time_ConvertTo_seconds(open_datetime)
            time.sleep(t)
            Func.output(False)

    if form.appointment_closing.data:
        close_minute = form.minute_close.data
        close_datetime = form.date_close.data
        if close_minute:
            time.sleep(close_minute*60)
            Func.output(True)
        if close_datetime:
            t = Func.appointment_time_ConvertTo_seconds(close_datetime)
            time.sleep(t)
            Func.output(True)

    if form.loop.data:
        loop_open = form.minute_loop_open.data
        loop_close = form.minute_loop_close.data
        while True:
            Func.output(False)
            time.sleep(loop_open*60)
            Func.output(True)
            time.sleep(loop_close*60)
            s = db(state='quit')
            if s!=[]:
                db.delete(s)
                break

    if form.exit_loop.data:
        db.insert(state='quit')

    return render_template('index.html',form=form)

if __name__ == '__main__':
    #app.run(port=5000,host='192.168.2.100')
    http_server = WSGIServer(('192.168.2.100',5000),app)
    http_server.serve_forever()