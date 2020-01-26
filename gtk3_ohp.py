#!/usr/bin/env python3

#  Copyright (c) 2017 Kurt Jacobson
#  License: https://kcj.mit-license.org/@2017

import argparse
import cairo
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
import signal

COMMAND_MASK = 0x10000010
LINE_WIDTH = 5
FG_RED = 0
FG_GREEN = 1
FG_RED = 0


class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class TransparentWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        self.connect('destroy', Gtk.main_quit)
        # self.connect('draw', self.draw)
        self.button_pressed = False
        self.drawing_line = False
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        # TODO use monitor api
        self.set_size_request(screen.get_width(), screen.get_height()*0.95)

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK
                              | Gdk.EventMask.BUTTON1_MOTION_MASK
                              | Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add(self.darea)

        self.shapes = []
        self.coords = []
        self.last_position = (0, 0)

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
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK) == Gdk.ModifierType.CONTROL_MASK or \
            (event.state & COMMAND_MASK) == COMMAND_MASK

        if ctrl and event.keyval == Gdk.KEY_z and 0 < len(self.shapes):
            del self.shapes[-1]
            self.darea.queue_draw()
        elif ctrl and event.keyval == Gdk.KEY_v:
            text = self.clipboard.wait_for_text()
            if text is not None:
                text = text.strip()
                self.shapes.append({"position": self.last_position,
                                    "type": "text",
                                    "text": text})
                self.darea.queue_draw()
                return
            image = self.clipboard.wait_for_image()
            if image is not None:
                self.shapes.append({"position": self.last_position,
                                    "type": "image",
                                    "image": image})
                self.darea.queue_draw()
                return

    def draw_line(self, wid, cr, points):
        if len(points) < 2:
            return
        cr.set_source_rgb(FG_RED, FG_GREEN, FG_BLUE)
        cr.set_line_width(LINE_WIDTH)
        
        start = points[0]
        cr.move_to(start[0], start[1])

        for p in points[1:]:
            cr.move_to(start[0], start[1])
            cr.line_to(p[0], p[1])
            start = p
        cr.stroke()
        
    def on_draw(self, wid, cr):
        for shape_info in self.shapes:
            shape_type = shape_info["type"]
            if shape_type == "text":
                cr.set_source_rgb(FG_RED, FG_GREEN, FG_BLUE)
                cr.set_line_width(LINE_WIDTH)
                cr.set_font_size(20)
                (x, y) = shape_info["position"]
                text = shape_info["text"]
                cr.move_to(x, y)
                cr.show_text(text)
            elif shape_type == "image":
                (x, y) = shape_info["position"]
                pixbuf = shape_info["image"]
                Gdk.cairo_set_source_pixbuf(cr, pixbuf, x, y)
                cr.paint()
                #cr.fill()
            elif shape_type == "line":
                points = shape_info["points"]
                self.draw_line(wid, cr, points)
            else:
                print("unknown shpae: " + shape_type)

        if self.drawing_line:
            self.draw_line(wid, cr, self.coords)
            
    def on_button_press(self, w, e):
        if e.type == Gdk.EventType.BUTTON_PRESS \
           and e.button == MouseButtons.LEFT_BUTTON:
            self.last_position = (e.x, e.y)
            self.coords.append([e.x, e.y])
            self.button_pressed = True
            self.drawing_line = True

    def on_button_release(self, w, e):
        if e.type == Gdk.EventType.BUTTON_RELEASE \
           and e.button == MouseButtons.LEFT_BUTTON:

            if 1 < len(self.coords):
                self.shapes.append({"type": "line",
                                    "points": self.coords})
            self.coords = []
            self.last_position = (e.x, e.y)
            self.button_pressed = False
            self.drawing_line = False
            self.darea.queue_draw()
            
    def on_move(self, w, e):
        if self.button_pressed:
            self.coords.append([e.x, e.y])
            self.last_position = (e.x, e.y)
            self.darea.queue_draw()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--red', type=float, default=0.0)
    parser.add_argument('-g', '--green', type=float, default=1.0)
    parser.add_argument('-b', '--blue', type=float, default=0.0)
    parser.add_argument('-l', '--line-width', type=float, default=4.0)

    args = parser.parse_args()
    FG_RED = min(1, args.red)
    FG_GREEN = min(1, args.green)
    FG_BLUE = min(1, args.blue)
    LINE_WIDTH = args.line_width

    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
    TransparentWindow()
    Gtk.main()
