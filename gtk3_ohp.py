#!/usr/bin/env python3

#  Copyright (c) 2017 Kurt Jacobson
#  License: https://kcj.mit-license.org/@2017

import cairo
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
import signal


class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class TransparentWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        self.connect('destroy', Gtk.main_quit)
        # self.connect('draw', self.draw)
        self.button_pressed = False
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        # TODO use monitor api
        self.set_size_request(screen.get_width(), screen.get_height()*0.95)

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK
                              | Gdk.EventMask.BUTTON1_MOTION_MASK
                              | Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add(self.darea)

        self.lines = []
        self.coords = []

        self.darea.connect("button-press-event", self.on_button_press)
        self.darea.connect("button-release-event", self.on_button_release)
        self.darea.connect("motion-notify-event", self.on_move)
        self.connect("key-press-event", self.on_key_press)

        self.set_title("Lines")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.set_app_paintable(True)
        self.show_all()

    def on_key_press(self, wid, event):
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval == Gdk.KEY_z and 0 < len(self.lines):
            del self.lines[-1]
            self.darea.queue_draw()           
        
    def on_draw(self, wid, cr):
        cr.set_source_rgb(0, 1, 0)
        cr.set_line_width(5)

        for line in self.lines + [self.coords]:
            if len(line) < 2:
                continue
            start = line[0]
            cr.move_to(start[0], start[1])

            for p in line[1:]:
                cr.move_to(start[0], start[1])
                cr.line_to(p[0], p[1])
                start = p

            cr.stroke()
            # cr.close_path()

    def on_button_press(self, w, e):
        if e.type == Gdk.EventType.BUTTON_PRESS \
            and e.button == MouseButtons.LEFT_BUTTON:

            self.coords.append([e.x, e.y])
            self.button_pressed = True

    def on_button_release(self, w, e):
        if e.type == Gdk.EventType.BUTTON_RELEASE \
            and e.button == MouseButtons.LEFT_BUTTON:
            self.lines.append(self.coords)
            self.coords = []
            self.button_pressed = False
            
    def on_move(self, w, e):
        if self.button_pressed:
            self.coords.append([e.x, e.y])
            self.darea.queue_draw()


if __name__ == '__main__':
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
    TransparentWindow()
    Gtk.main()
    
