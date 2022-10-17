#!/usr/bin/make -f


CWD=source

# ---------------------------------------------------------------------------------------------------------------------

PREFIX     := /usr/local
BINDIR     := $(PREFIX)/bin
SBINDIR    := $(PREFIX)/sbin
LIBDIR     := $(PREFIX)/lib
DATADIR    := $(PREFIX)/share
DESTDIR    :=


all:
	echo "build finished"

install:

	# this one is special, it has to go in /etc
	install -d /etc/acpi/events
	install -m 644 etc/acpi/events/* /etc/acpi/events
	install -m 644 etc/acpi/studio.sh /etc/acpi

	# Everything else is $(DESTDIR)
	install -d $(DESTDIR)$(DATADIR)/applications
	install -d $(DESTDIR)$(DATADIR)/icons/hicolor/16x16/apps
	install -d $(DESTDIR)$(DATADIR)/icons/hicolor/22x22/apps
	install -d $(DESTDIR)$(DATADIR)/icons/hicolor/24x24/apps
	install -d $(DESTDIR)$(DATADIR)/icons/hicolor/48x48/apps
	install -d $(DESTDIR)$(DATADIR)/icons/hicolor/64x64/apps
	install -d $(DESTDIR)$(DATADIR)/icons/hicolor/128x128/apps
	install -d $(DESTDIR)$(DATADIR)/icons/hicolor/256x256/apps
	install -d $(DESTDIR)$(DATADIR)/icons/hicolor/scalable/apps
	install -d $(DESTDIR)$(DATADIR)/man/man1
	install -d $(DESTDIR)$(DATADIR)/man/man2
	install -d $(DESTDIR)$(DATADIR)/polkit-1/actions
	install -d $(DESTDIR)$(DATADIR)/studio-controls

	install -d $(DESTDIR)$(BINDIR)
	install -d $(DESTDIR)$(SBINDIR)
	install -d $(DESTDIR)$(LIBDIR)/systemd/user/default.target.wants
	install -d $(DESTDIR)$(LIBDIR)/systemd/user/indicator-messages.service.wants
	install -d $(DESTDIR)$(LIBDIR)/python3/dist-packages

	# now the files
	install -m 644	usr/share/applications/studio-controls.desktop \
		$(DESTDIR)$(DATADIR)/applications
	install -m 644 usr/share/icons/hicolor/16x16/apps/* \
		$(DESTDIR)$(DATADIR)/icons/hicolor/16x16/apps
	install -m 644 usr/share/icons/hicolor/22x22/apps/* \
		$(DESTDIR)$(DATADIR)/icons/hicolor/22x22/apps
	install -m 644 usr/share/icons/hicolor/24x24/apps/* \
		$(DESTDIR)$(DATADIR)/icons/hicolor/24x24/apps
	install -m 644 usr/share/icons/hicolor/48x48/apps/* \
		$(DESTDIR)$(DATADIR)/icons/hicolor/48x48/apps
	install -m 644 usr/share/icons/hicolor/64x64/apps/* \
		$(DESTDIR)$(DATADIR)/icons/hicolor/64x64/apps
	install -m 644 usr/share/icons/hicolor/128x128/apps/* \
		$(DESTDIR)$(DATADIR)/icons/hicolor/128x128/apps
	install -m 644 usr/share/icons/hicolor/256x256/apps/* \
		$(DESTDIR)$(DATADIR)/icons/hicolor/256x256/apps
	install -m 644 usr/share/icons/hicolor/scalable/apps/* \
		$(DESTDIR)$(DATADIR)/icons/hicolor/scalable/apps
	install -m 644 usr/share/man/man1/* \
		$(DESTDIR)$(DATADIR)/man/man1
	install -m 644 usr/share/man/man2/* \
		$(DESTDIR)$(DATADIR)/man/man2
	install -m 644 usr/share/polkit-1/actions/* \
		$(DESTDIR)$(DATADIR)/polkit-1/actions
	install -m 644 usr/share/studio-controls/* \
		$(DESTDIR)$(DATADIR)/studio-controls

	install -m 655 usr/bin/* \
		$(DESTDIR)$(BINDIR)
	install -m 655 usr/sbin/* \
		$(DESTDIR)$(SBINDIR)

	install -m 644 usr/lib/systemd/user/session-monitor.service \
		$(DESTDIR)$(LIBDIR)/systemd/user
	install -m 655 usr/lib/python3/dist-packages/* \
		$(DESTDIR)$(LIBDIR)/python3/dist-packages

	# make links
	ln -s $(DESTDIR)$(LIBDIR)/systemd/user/session-monitor.service \
		$(DESTDIR)$(LIBDIR)/systemd/user/indicator-messages.service.wants/session-monitor.service


# ---------------------------------------------------------------------------------------------------------------------

uninstall:
	rm -f /etc/acpi/studio-*
	rm -f /etc/acpi/studio.sh

	rm -f $(DESTDIR)$(DATADIR)/applications/studio-controls.desktop

	rm -f $(DESTDIR)$(DATADIR)/icons/hicolor/16x16/apps/studio-controls.png
	rm -f $(DESTDIR)$(DATADIR)/icons/hicolor/22x22/apps/studio-controls.png
	rm -f $(DESTDIR)$(DATADIR)/icons/hicolor/24x24/apps/studio-controls.png
	rm -f $(DESTDIR)$(DATADIR)/icons/hicolor/48x48/apps/studio-controls.png
	rm -f $(DESTDIR)$(DATADIR)/icons/hicolor/64x64/apps/studio-controls.png
	rm -f $(DESTDIR)$(DATADIR)/icons/hicolor/128x128/apps/studio-controls.png
	rm -f $(DESTDIR)$(DATADIR)/icons/hicolor/256x256/apps/studio-controls.png
	rm -f $(DESTDIR)$(DATADIR)/icons/hicolor/scalable/apps/studio-controls.svg

	rm -f $(DESTDIR)$(DATADIR)/man/man1/studio-controls.*
	rm -f $(DESTDIR)$(DATADIR)/man/man1/studio-cmd.*
	rm -f $(DESTDIR)$(DATADIR)/man/man2/autojack.*
	rm -f $(DESTDIR)$(DATADIR)/man/man2/studio-system.*

	rm -f $(DESTDIR)$(DATADIR)/polkit-1/actions/com.studiocontrols.pkexec.studio-controls.policy

	rm -rf $(DESTDIR)$(DATADIR)/studio-controls

	rm -f $(DESTDIR)$(BINDIR)/autojack
	rm -f $(DESTDIR)$(BINDIR)/studio-cmd
	rm -f $(DESTDIR)$(BINDIR)/studio-controls

	rm -f $(DESTDIR)$(SBINDIR)/studio-system

	rm -f $(DESTDIR)$(LIBDIR)/python3/dist-packages/auto_jack.py

	rm -f $(DESTDIR)$(LIBDIR)/systemd/user/session-monitor.service
	rm -f $(DESTDIR)$(LIBDIR)/systemd/user/indicator-messages.service.wants/session-monitor.service

