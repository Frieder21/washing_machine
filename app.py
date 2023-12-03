from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets
import datetime
app = Flask(__name__)

class washing_machineor_tumble_dryer:
    def __init__(self, washing_machine_or_tumble_dryer: bool, max_duration: int = 240, unique_id: int = 0):
        """

        :type washing_machine_or_tumble_dryer: bool True = washing_machine, False = tumble_dryer
        :type max_duration: int in minutes
        """
        import secrets
        import datetime
        if washing_machine_or_tumble_dryer:
            self.device = "washing_machine"
        else:
            self.device = "tumble_dryer"
        self.max_duration = max_duration
        self.filled = False
        self.open = True
        self.end_time = datetime.datetime.now().timestamp()
        self.start_time = datetime.datetime.now().timestamp()
        self.unique_id = unique_id
        self.user_id = None

    def start(self, duration_minutes: int):
        if self.end_time > datetime.datetime.now().timestamp():
            return "already running"
        if duration_minutes > self.max_duration:
            return "duration too long"
        self.start_time = datetime.datetime.now().timestamp()
        self.end_time = self.start_time + duration_minutes * 60
        self.open = False
        self.filled = True
        self.user_id = secrets.token_hex(256)
        return [self.user_id, self.end_time]

    def end(self, user_id: str = ""):
        if self.end_time > datetime.datetime.now().timestamp():
            if user_id != self.user_id:
                return "wrong user id"
        self.end_time = datetime.datetime.now().timestamp()
        self.open = True
        self.filled = False
        self.user_id = None
        return "ended"

    def check_if_ready_and_end(self):
        if self.end_time < datetime.datetime.now().timestamp():
            self.end()

    def status(self):
        if self.end_time < datetime.datetime.now().timestamp():
            return {"status": "ready", "time_left": "00:00", "device": self.device, "open": self.open,
                    "filled": self.filled, "max_duration": self.max_duration, "unique_id": self.unique_id}
        else:
            return {"status": "running", "time_left": "{:02d}:{:02d}".format(datetime.datetime.fromtimestamp(self.end_time - datetime.datetime.now().timestamp()).hour, datetime.datetime.fromtimestamp(self.end_time - datetime.datetime.now().timestamp()).minute),
                    "device": self.device, "open": self.open, "filled": self.filled, "max_duration": self.max_duration,
                    "unique_id": self.unique_id}

    def status_for_web(self):
        self.check_if_ready_and_end()
        dict = {}
        if self.device == "washing_machine":
            dict["device"] = "washing machine"
            dict["device_id"] = "washing_machine"
            dict["device_picture"] = "/static/assets/img/machine3.png"
        if self.device == "tumble_dryer":
            dict["device"] = "tumble dryer"
            dict["device_id"] = "tumble_dryer"
            dict["device_picture"] = "/static/assets/img/machine4.png"
        if self.filled:
            dict["cloths_picture"] = "/static/assets/img/machine5.png"
        else:
            dict["cloths_picture"] = "/static/assets/img/machine8.png"
        if self.open:
            dict["open_picture"] = "/static/assets/img/machine1.png"
            dict["device_picture"] = "/static/assets/img/machine7.png"
        else:
            dict["open_picture"] = "/static/assets/img/machine2.png"
        if self.end_time < datetime.datetime.now().timestamp():
            dict["status"] = "ready"
            dict["time_left"] = "00:00"
            dict["x_animation"] = ""
            dict["rotate_animation"] = ""
        else:
            dict["status"] = "running"
            time = datetime.datetime.fromtimestamp(self.end_time - datetime.datetime.now().timestamp())
            dict["time_left"] = "{:02d}:{:02d}".format(time.hour-1, time.minute)
            dict["x_animation"] = "washing"
            dict["rotate_animation"] = "rotate"
        time = datetime.datetime.fromtimestamp(self.max_duration*60)
        dict["max_duration"] = "{:02d}:{:02d}".format(time.hour-1, time.minute)
        dict["unique_id"] = self.unique_id
        return dict




@app.route('/api', methods=['GET', 'POST'] )
def api():
    global devices
    if request.method == 'POST':
        if request.form['action'] == 'start':
            device = request.form['device_id']
            hours, minutes = request.form['duration'].split(":")
            duration = int(hours) * 60 + int(minutes)
            cookies = devices[int(device)].start(float(duration))
            resp = app.make_response(redirect(url_for('home', _scheme='https', _external=True)))
            resp.set_cookie(str(device), cookies[0], max_age=int(60 * float(duration)))
            return resp
        if request.form['action'] == 'end':
            device = request.form['device_id']
            try:
                user_id = request.cookies.get(str(device))
            except:
                user_id = ""
            if devices[int(device)].end(user_id) == "wrong user id":
                return "wrong user id"
            resp = app.make_response(redirect(url_for('home', _scheme='https', _external=True)))
            resp.set_cookie(str(device), '', max_age=0)
            return resp
    elif request.method == 'GET':
        if request.args.get('action') == 'start':
            device = request.args.get('device_id')
            hours, minutes = request.args.get('duration').split(":")
            duration = int(hours) * 60 + int(minutes)
            cookies = devices[int(device)].start(float(duration))
            resp = app.make_response(redirect(url_for('home', _scheme='https', _external=True)))
            resp.set_cookie(str(device), cookies[0], max_age=int(60 * float(duration)))
            return resp
        if request.args.get('action') == 'end':
            device = request.args.get('device_id')
            try:
                user_id = request.cookies.get(str(device))
            except:
                user_id = ""
            if devices[int(device)].end(user_id) == "wrong user id":
                return "wrong user id"
            resp = app.make_response(redirect(url_for('home', _scheme='https', _external=True)))
            resp.set_cookie(str(device), '', max_age=0)
            return resp
    return "error"


@app.route('/start/<device>/<duration>')
def start(device, duration):
    global devices
    cookies = [machine1, machine2][int(device)].start(float(duration))
    resp = app.make_response(redirect(url_for('home')))
    resp.set_cookie('user_id', cookies[0], max_age=int(60 * float(duration)))
    return resp

@app.route('/end/<device>')
def end(device):
    global devices
    try:
        user_id = request.cookies.get('user_id')
    except:
        user_id = ""
    devices[int(device)].end(user_id)
    resp = app.make_response(redirect(url_for('home')))
    resp.set_cookie('user_id', '', max_age=0)
    return resp


@app.route("/api/update")


@app.route('/')
def home():
    global devices
    global machine1
    global machine2
    global machine3
    global machine4
    try:
        machine1.check_if_ready_and_end()
        machine2.check_if_ready_and_end()
        machine3.check_if_ready_and_end()
        machine4.check_if_ready_and_end()
    except:
        machine1 = washing_machineor_tumble_dryer(True, unique_id=1)
        machine2 = washing_machineor_tumble_dryer(True, unique_id=2)
        machine3 = washing_machineor_tumble_dryer(True, unique_id=3)
        machine4 = washing_machineor_tumble_dryer(False, unique_id=4)
        devices = {
            1: machine1,
            2: machine2,
            3: machine3,
            4: machine4
        }
    return render_template('washing_machine-tumble_dryer.html',
                           wmotdd=[machine1.status_for_web(), machine2.status_for_web(), machine3.status_for_web(), machine4.status_for_web()], str=str)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='assets/img/favicon.ico', _scheme='https', _external=True))

if __name__ == '__main__':
    app.run()

