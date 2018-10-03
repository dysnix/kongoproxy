## Configure

Please set params to `local_settings.py`

## Install

    cd kongoproxy
    pip install -r requirements.txt
    
    tee /etc/cron.d/kongoproxy << EOF
    */15 * * * *	root	ulimit -n 10000; cd /path/to/kongoproxy && python /path/to/kongoproxy/check_proxy.py 2>&1 | logger -t kongoproxy
    EOF
