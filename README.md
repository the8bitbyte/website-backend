# website-backend
the backend for my website, decided i needed one because some skid nuked my webhook

## how it works

the webserver im using is apache2 which just takes all traffic directed to /api and sends it to the backend with loopback, heres my 000-default.conf

```

<VirtualHost *:80>
        ServerAdmin webmaster@localhost
        ServerName tainted-purity.rip
        DocumentRoot /var/www/html

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        ProxyPreserveHost On
        ProxyPass /api http://127.0.0.1:5000/
        ProxyPassReverse /api http://127.0.0.1:5000/

        RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}s"

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost>
```

Since it’s using loopback, the backend sees the IP address as 127.0.0.1, which isn’t the intended functionality. To resolve this, it sends the IP address as a header, and the backend reads that IP.

The backend adds each IP address to a list. If the IP address isn’t on the list when the request is sent, it increments the view counter by 1 and sends me a message on Discord, letting me know someone visited my website for the first time. Then, it adds the IP address to the list.

### Potental issue

I’m aware this could lead to issues with VPNs. Someone could use a VPN to repeatedly increment the counter, and if someone already visited the website using the same VPN server as you, the view wouldn’t be counted. Despite this, the percentage of users on a VPN is low, so I’m not too concerned.
