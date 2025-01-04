# apis
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
