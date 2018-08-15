## Configure

Please set params to `local_settings.py`

## Install

    cd kongoproxy
    pip install -r requirements.txt
    
    tee /etc/cron.d/kongoproxy << EOF
    */15 * * * *	root	ulimit -n 10000; cd /home/kongoproxy/kongoproxy && /home/kongoproxy/.virtualenvs/kongoproxy/bin/python /home/kongoproxy/kongoproxy/check_proxy.py 2>&1 | logger -t kongoproxy
    EOF
    
## Run squid

For this solution we need use patched Squid for allow bind many ports.

You can use prepared docker image and easy start in one command:

    /etc/init.d/squid stop; docker run -d -v /srv/squid/spool:/var/spool/squid -v /etc/squid/squid.conf:/etc/squid/squid.conf -v /home/kongoproxy/kongoproxy/etc/forwarding.conf:/home/kongoproxy/kongoproxy/etc/forwarding.conf --network host --name squid --restart=always arilot/squid