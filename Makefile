DESTDIR=

install:
	/bin/mkdir -p $(DESTDIR)/usr/sbin
	/bin/mkdir -p $(DESTDIR)/usr/share/logster/parsers
	/bin/mkdir -p $(DESTDIR)/var/log/logster
	/usr/bin/install -m 0755 -t $(DESTDIR)/usr/sbin bin/logster
	/usr/bin/install -m 0644 -t $(DESTDIR)/usr/share/logster logster/logster_helper.py
	/usr/bin/install -m 0644 -t $(DESTDIR)/usr/share/logster/parsers logster/parsers/*
