#!/usr/bin/env python

from pyxhook import HookManager

watched_keys = ["Control_R", "Control_L"]

def handle_event (event):
        if event.Key in watched_keys:
            print "KeyRelease"


hm = HookManager()
hm.HookKeyboard()
hm.KeyUp = handle_event
hm.start()
