from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets
import datetime
import random
import toml
import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
app = Flask(__name__)
app.secret_key = secrets.token_hex(256)
def open_toml_file(filename, file_location: str = ""):
    if file_location == "":
        file_path = os.path.join(os.path.split(__file__)[0], filename)
    elif os.path.exists(file_location):
        file_path = os.path.join(file_location, filename)
    elif os.path.exists(os.path.join(os.path.split(__file__)[0], file_location)):
        file_path = os.path.join(os.path.split(__file__)[0], file_location)
    else:
        file_path = filename
    with open(file_path, "r", encoding="utf-8") as file:
        return toml.load(file)


def random_duration():
    return str(str(random.randint(2, 15)) + "s")

def read_views(filename="views", file_location: str = ""):
    if file_location == "":
        file_path = os.path.join(os.path.split(__file__)[0], filename)
    elif os.path.exists(file_location):
        file_path = os.path.join(file_location, filename)
    elif os.path.exists(os.path.join(os.path.split(__file__)[0], file_location)):
        file_path = os.path.join(os.path.split(__file__)[0], file_location)
    else:
        file_path = filename
    with open(file_path, "r",encoding="utf-8") as file:
        return int(file.read())

def write_views(views, filename="views", file_location: str = ""):
    if file_location == "":
        file_path = os.path.join(os.path.split(__file__)[0], filename)
    elif os.path.exists(file_location):
        file_path = os.path.join(file_location, filename)
    elif os.path.exists(os.path.join(os.path.split(__file__)[0], file_location)):
        file_path = os.path.join(os.path.split(__file__)[0], file_location)
    else:
        file_path = filename
    with open(file_path, "w",encoding="utf-8") as file:
        file.write(str(views))


class washing_machineor_tumble_dryer:
    def __init__(self, washing_machine_or_tumble_dryer: bool, max_duration: int = 240, unique_id: str = 0,
                 time_left: int = 0, user_id: str = ""):
        """

        :type washing_machine_or_tumble_dryer: bool True = washing_machine, False = tumble_dryer
        :type max_duration: int in minutes
        :type unique_id: int
        :type time_left: int in minutes
        """
        import secrets
        import datetime
        if washing_machine_or_tumble_dryer:
            self.device = "washing_machine"
        else:
            self.device = "tumble_dryer"
        self.max_duration = max_duration
        if time_left > 0:
            self.filled = True
            self.open = False
            if time_left > max_duration:
                time_left = max_duration
            self.end_time = datetime.datetime.now().timestamp() + time_left * 60
        else:
            self.filled = False
            self.open = True
            self.end_time = datetime.datetime.now().timestamp()
        self.start_time = datetime.datetime.now().timestamp()
        self.unique_id = unique_id
        if user_id == "":
            self.user_id = None
        else:
            self.user_id = user_id

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

def gen_qr_code(config):
    if config["qr_code"] == "auto":
        link = url_for('home', _scheme='https', _external=True)
    elif config["qr_code"] != "none" or config["qr_code"] != "":
        link = config["qr_code"]
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(link)
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
    img.save(os.path.join(os.path.split(__file__)[0],"static/assets/img/qrcode.png"))

def load_config():
    global full_config
    global devices
    global config
    try:
        full_config_new = open_toml_file("config.toml")
    except:
        return [False, "[Error] full_config.toml not found"]
    try:
        if full_config == full_config:
            pass
    except:
        full_config = {"washer": {}, "dryer": {}, "config": {}}
    if not full_config == full_config_new:
        if not (full_config["washer"] == full_config_new["washer"] and full_config["dryer"] == full_config_new["dryer"]):
            devices = {}
            full_config = full_config_new
            if "washer" in full_config.keys():
                i = 0
                for device in full_config["washer"]:
                    devices["washer"+str(i)] = washing_machineor_tumble_dryer(True, unique_id=str("washer"+str(i)), max_duration=int(full_config["washer"][device]["max_duration"]))
                    i += 1
            if "dryer" in full_config.keys():
                i = 0
                for device in full_config["dryer"]:
                    devices["dryer"+str(i)] = washing_machineor_tumble_dryer(False, unique_id=str("dryer"+str(i)), max_duration=int(full_config["dryer"][device]["max_duration"]))
                    i += 1
        full_config = full_config_new
        config = full_config_new["config"]
        gen_qr_code(config)
        return [True, "config loaded successfully"]
    return [True, "success full_config not updated"]



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
            cookies = devices[device].start(float(duration))
            resp = app.make_response(redirect(url_for('home', _scheme='https', _external=True)))
            resp.set_cookie(str(device), cookies[0], max_age=int(60 * float(duration)))
            return resp
        if request.args.get('action') == 'end':
            device = request.args.get('device_id')
            try:
                user_id = request.cookies.get(str(device))
            except:
                user_id = ""
            if devices[device].end(user_id) == "wrong user id":
                return "wrong user id"
            resp = app.make_response(redirect(url_for('home', _scheme='https', _external=True)))
            resp.set_cookie(str(device), '', max_age=0)
            return resp
    return "error"


@app.route('/start/<device>/<duration>')
def start(device, duration):
    global devices
    cookies = devices[int(device)].start(float(duration))
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
def nothing():
    pass

def initial_run():
    try:
        read_views()
    except:
        write_views(0)
    try:
        read_views("totalviews")
    except:
        write_views(0, "totalviews")



@app.route('/', methods=['GET', 'POST'])
def home():
    global initial
    global config
    global devices

    config_success = load_config()
    if config_success[0]:
        print(config_success[1])
    else:
        return config_success[1]

    try:
        if initial == True:
            pass
    except:
        initial = True
        initial_run()

    if config["count_views"]:
        show_views = config["show_views"]
        show_total_views = config["show_total_views"]
        views = read_views()
        if not "user_id" in session:
            session["user_id"] = secrets.token_hex(256)
            views += 1
            write_views(views)
        total_views = read_views("totalviews")+1
        write_views(total_views, "totalviews")
    else:
        show_views = False
        views = 0
        show_total_views = False
        total_views = 0

    if config["cookie_warning_text"] == "none" or config["cookie_warning_text"] == "":
        cookie_warning = False
        cookie_warning_text = ""
    elif config["cookie_warning_text"] == "default":
        cookie_warning = True
        cookie_warning_text = "this website uses technical cookies"
    else:
        cookie_warning = True
        cookie_warning_text = config["cookie_warning_text"]

    title = config["title"]

    if config["qr_code"] == "none" or config["qr_code"] == "":
        show_qr_code = False
    else:
        show_qr_code = True

    wmotdd = []
    for device in devices:
        wmotdd.append(devices[device].status_for_web())

    return render_template('washing_machine-tumble_dryer.html', cookie_warning=cookie_warning, cookie_warning_text=cookie_warning_text, title=title, show_qr_code=show_qr_code,
                           wmotdd=wmotdd, str=str, random_duration=random_duration, show_views=show_views, views=views, show_total_views=show_total_views, total_views=total_views)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='assets/img/favicon.ico', _scheme='https', _external=True))

if __name__ == '__main__':
    app.run()

