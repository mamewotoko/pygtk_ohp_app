#!/usr/bin/env python3

#  Original code
#  Copyright (c) 2017 Kurt Jacobson
#  License: https://kcj.mit-license.org/@2017

#  Modified code
#  Copyright (c) 2020 Takashi Masuyama
#  License: https://kcj.mit-license.org/@2017

import argparse
import cairo
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
import os
import platform
import re
import signal

COMMAND_MASK = 0x10000010
ctlLINE_WIDTH = 5
FG_RED = 0
FG_GREEN = 1
FG_RED = 0
FONT_SIZE = 24
FONT_NAME = None
# Ctrl-z: undo
# Ctrl-y: redo
STATUS_BAR_HEIGHT = 30

class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class TransparentWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        self.connect('destroy', Gtk.main_quit)
        self.button_pressed = False
        self.drawing_line = False
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        # TODO use monitor api
        self.is_fullscreen = True
        self.width = screen.get_width()
        self.height = screen.get_height() - STATUS_BAR_HEIGHT
        self.set_size_request(self.width, self.height)
        self.set_resizable(True)

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK
                              | Gdk.EventMask.BUTTON1_MOTION_MASK
                              | Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add(self.darea)

        self.shapes = []
        self.redo_shapes = []
        self.coords = []
        self.link = []
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

    def fullscreen(self):
        screen = self.get_screen()
        self.height = screen.get_height() * 0.95
        self.set_size_request(self.width, self.height)
        self.resize(self.width, self.height)
        self.is_fullscreen = True

    def minimize(self):
        self.height = 10
        self.set_size_request(self.width, self.height)
        self.resize(self.width, self.height)
        self.is_fullscreen = False

    def clear(self):
        self.shapes = []
        self.redo_shapes = []
        self.coords = []
        self.link = []
        self.last_position = (0, 0)
        
    def shapes2svg(self):
        pass
        
    def on_key_press(self, wid, event):
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK) == Gdk.ModifierType.CONTROL_MASK or \
            (event.state & COMMAND_MASK) == COMMAND_MASK

        if ctrl and event.keyval == Gdk.KEY_z and 0 < len(self.shapes):
            self.redo_shapes.append(self.shapes[-1])
            del self.shapes[-1]
            self.darea.queue_draw()
        elif ctrl and event.keyval == Gdk.KEY_y and 0 < len(self.redo_shapes):
            self.shapes.append(self.redo_shapes[-1])
            del self.redo_shapes[-1]
            self.darea.queue_draw()
        # elif ctrl and event.keyval == Gdk.KEY_s:
        #     # AttributeError: 'GdkQuartzWindow' object has no attribute 'get_colormap'
        #     filename = "tmp.png"
        #     drawable = self.get_window()
        #     colormap = drawable.get_colormap()
        #     pixbuf = Gdk.Pixbuf(Gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        #     pixbuf = pixbuf.get_from_drawable(drawable, colormap,
        #                                       0, 0, 0, 0,
        #                                       *drawable.get_size())
        #     pixbuf.save(filename, 'png')
        elif ctrl and event.keyval == Gdk.KEY_f:
            # full screen <-> minimize
            if self.is_fullscreen:
                self.minimize()
            else:
                self.fullscreen()
        elif ctrl and event.keyval == Gdk.KEY_d:
            # clear
            self.clear()
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
                # text []()
                text = shape_info["text"]
                m = re.match(r"\[(.*)\]\((.*)\)", text)
                if m is not None:
                    display_text = m.group(1)
                    url = m.group(2)
                else:
                    display_text = text
                    url = None
                cr.set_source_rgb(FG_RED, FG_GREEN, FG_BLUE)
                cr.set_line_width(LINE_WIDTH)
                cr.set_font_size(FONT_SIZE)
                if FONT_NAME is not None:
                    cr.select_font_face(FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                (x, y) = shape_info["position"]

                cr.move_to(x, y)
                cr.show_text(display_text)

                if url is not None:
                    self.link.append({"position": [x, y], "url": url})
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
        # draw frame
        # frame width = 4
        current = (0, 0)
        cr.move_to(*current)
        cr.set_source_rgb(1, 0, 0)
        cr.set_line_width(4)
        for point in [(self.width, 0), (self.width, self.height), (0, self.height), (0, 0)]:
            cr.line_to(*point)
        cr.stroke()
            
    def link_clicked(self, l, x, y):
        lx = l["position"][0]
        ly = l["position"][1]
        box_size = 20
        # TODO modify size
        return lx - box_size <= x and x <= lx + box_size and \
            ly - box_size <= y and y <= ly + box_size

    def open_link(self, url):
        # mac
        os.system("open '%s'" % url)
    
    def on_button_press(self, w, e):
        if e.type == Gdk.EventType.BUTTON_PRESS \
           and e.button == MouseButtons.LEFT_BUTTON:

            for l in self.link:
                print("ex. ey %d, %d %d %d" % (e.x, e.y, l["position"][0], l["position"][1]))
                if self.link_clicked(l, e.x, e.y):
                    self.open_link(l["url"])
                    break
                else:
                    print("not clicked")
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
    parser.add_argument('-f', '--font', type=str, default=None)

    args = parser.parse_args()
    if args.font is not None:
        FONT_NAME = args.font
    else:
        os_release = platform.system()
        print(os_release)
        if os_release == "Darwin":
            # TODO: if japanese
            FONT_NAME = "Osaka"
        elif os_release == "Linux":
            # ubuntu?
            FONT_NAME = "takao"

    FG_RED = min(1, args.red)
    FG_GREEN = min(1, args.green)
    FG_BLUE = min(1, args.blue)
    LINE_WIDTH = args.line_width

    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
    TransparentWindow()
    Gtk.main()
