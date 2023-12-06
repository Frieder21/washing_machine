# WMTD
sometimes I'm really bored and in the next moment (15h later) there is a new running website in front of me...

[![wmtd.png](https://beta.frieda-univers.me/static/assets/images/wmtd.png)](https://beta.frieda-univers.me/static/assets/images/wmtd.png)

this is a website you could host on your own for sharing people in your dorm that the washing machine or the tumble dryer is/n't ready to use.
## What was the best part creating it?
I liked to design the washing machine and the tumble dryer. I also liked to create the backend.
## Do you want me to host it for you?
Yes, I could host it for you but I'm broke, so I would be happy if you donate a small amount. Just massage me on [Matrix: @frieda:catgirl.cloud](https://matrix.to/#/@frieda:catgirl.cloud), [Email](mailto:feedo@posteo.de) or Discord: friedaaaaaaa.
## How to install it on a raspberry pi the way I did
### Install the raspberry pi
There are a lot of tutorials out there. I did it without one. I installed [ubuntu server](https://ubuntu.com/download/raspberry-pi) on my raspberry pi 4, but it should work on most debian based systems. While installing it I enabled ssh.
### Installing and ubdating the packages
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3, python3-pip, nginx, git, certbot
pip3 install flask
```
this is the minimum you need to run the website. I also installed [gunicorn](https://gunicorn.org/) to run the website and [certbot](https://certbot.eff.org/) to get a ssl certificate.
### Installing the website
```bash
cd /var/www/html
sudo git clone git@github.com:Frieder21/washing_machine.git
sudo chown -R www-data:www-data washing_machine
```
here I cloned the website into the default nginx folder and changed the owner to www-data. This is the user that nginx uses to run the website.

### Conifguring gunicon
now we need to configure gunicorn. I used the default config and changed the bind and the number of workers.
```bash
sudo nano /var/www/html/washing_machine/gunicorn-config.py
```
```python
bind = '<your ip>:<your port>'
workers = 1 # more workers will break the website because the website has no database and uses a global variable
```

### Configuring systemd
now we need to configure systemd to run the website. For this we need to know where the path to gunicon is.
```bash
which gunicorn
```
```bash
sudo cp /var/www/html/washing_machine/wmtd.service /etc/systemd/system/
sudo nano /etc/systemd/system/wmtd.service
```
```systemd
[Unit]
Description=WMTD
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/html/washing_machine/
ExecStart=<path/to/gunicorn> app:app -c /var/www/html/washing_machine/gunicorn_config.py
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enabled --now wmtd
```

### Configuring nginx
that you can access the website from the internet you need to configure nginx. I removed the default config and created a new one.
```bash
sudo rm /etc/nginx/sites-enabled/default # remove the default config
sudo nano /etc/nginx/sites-enabled/washing_machine
```
```nginx
server {
    server_name <your domain>;

    location / {
        proxy_pass http://localhost:<your port>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Configuring certbot
that you can access the website with https you need to configure certbot.
```bash
sudo certbot --nginx
```
### Configuring the website
now you need to configure how many washing machines or tumble dryers you have and how long they maximum need to run. For this you need to edit the app.py file.
```bash
sudo nano /var/www/html/washing_machine/app.py
```
here is an example where I removed two washing machines from app.py:
```python
@app.route('/')
def home():
    global devices
    global machine1 # washing machine
    global machine2 # tumble dryer
    try:
        machine1.check_if_ready_and_end()
        machine2.check_if_ready_and_end()
    except:
        machine1 = washing_machineor_tumble_dryer(True, unique_id=1, max_duration=<in minutes>)
        machine2 = washing_machineor_tumble_dryer(False, unique_id=2)
        devices = {
            1: machine1,
            2: machine2,
        }
    return render_template('washing_machine-tumble_dryer.html',
                           wmotdd=[machine1.status_for_web(), machine2.status_for_web()], # wmotdd = washing machine or tumble dryer data
                           str=str, random_duration=random_duration, views=views, total_views=total_views)
```

## Future plans
- [ ] adding database
- [ ] easier configuration
- [ ] maybe a install_script


