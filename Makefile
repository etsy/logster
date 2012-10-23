install:
	/bin/mkdir -p /usr/share/logster
	/bin/mkdir -p /var/log/logster
	/usr/bin/install -m 0755 -t /usr/sbin bin/logster
	/usr/bin/install -m 0644 -t /usr/share/logster logster/logster_helper.py
	/usr/bin/install -m 0644 -t /usr/share/logster logster/parsers/*
