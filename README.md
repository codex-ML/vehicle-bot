# apis

sudo apt update
sudo apt install apt-transport-https

curl -s https://deb.torproject.org/torproject.org/keys.asc | gpg --dearmor > /usr/share/keyrings/tor-archive-keyring.gpg


python3 -m venv env

source env/bin/activate

sudo env/bin/python3 api.py


echo "deb [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org focal main" | sudo tee /etc/apt/sources.list.d/torproject.list

sudo apt update

sudo apt install tor deb.torproject.org-keyring

sudo systemctl start tor

sudo systemctl enable tor

sudo systemctl status tor

sudo service tor start

ControlPort 9051
CookieAuthentication 1

/etc/tor/torrc

sudo service tor restart
to verify port
telnet 127.0.0.1 9051


chmod 777 setup.sh
bash setup.sh

sudo pip install requests[socks] stem
sudo pip install markupsafe
sudo pip install jinja2


sudo service privoxy start

# Edit /etc/privoxy/config
# Add the following line to the end of the file
# forward-socks5 /http://127.0.0.1:5000/?regno=AS01EJ4055
