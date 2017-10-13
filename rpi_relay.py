from flask import Flask,render_template,request
from flask_wtf import FlaskForm
from wtforms import SubmitField,IntegerField,DateTimeField
from flask_bootstrap import Bootstrap
import RPi.GPIO as GPIO
import time,datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rp'
bootstrap = Bootstrap(app)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12,GPIO.OUT)

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

    on = SubmitField('常开')
    off = SubmitField('常关')


@app.route('/',methods=['GET','POST'])
def index():
    form = SwitchForm()
    if form.on.data:
        GPIO.output(12,False)
    if form.off.data:
        GPIO.output(12,True)
    if form.appointment_opening.data:
        minute = form.minute_open.data
        _datetime = form.date_open.data
        if minute:
            time.sleep(minute*60)
            GPIO.output(12, False)
        if _datetime:
            appointment = datetime.datetime.strptime(str(_datetime),"%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.now()
            t = appointment - now
            time.sleep(int(t.total_seconds()))
            GPIO.output(12, False)
    return render_template('index.html',form=form)

if __name__ == '__main__':
    app.run(port=5000,host='0.0.0.0')