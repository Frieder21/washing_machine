# WMTD
sometimes I'm really bored and in the next moment (15h later) there is a new running website in front of me...

[![wmtd.png](../static/assets/images/wmtd.png)](../static/assets/images/wmtd.png)

this is a website you could host on your own for sharing people in your dorm that the washing machine or the tumble dryer is/n't ready to use.
## What was the best part?
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
pip3 install flask, gunicorn, qrcode[pil], toml
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
sudo nano /var/www/html/washing_machine/config.toml.example
```

here is an example with two washing machines and one tumble dryer:
```toml
[config]

title = "washing in the dorm building 41/42"
cookie_warning_text = "default" #  default, custom (my cookie warning text), none
count_views = true
show_views = true
show_total_views = true
show_qr = true
qr_code = "auto" # auto, custom (https://subdomain.domain.toplevel/idk), none

# updating the devices list will reset all devices state
[washer]
[washer.0]
max_duration = 300 # in minutes
[washer.1]
max_duration = 120 # in minutes

[dryer]
[dryer.0]
max_duration = 60 # in minutes
```
## Future plans

-[ ] adding database
-[x] easier configuration



