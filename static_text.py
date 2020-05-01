#!/usr/bin/env python3

#  Original code
#  Copyright (c) 2017 Kurt Jacobson
#  License: https://kcj.mit-license.org/@2017

#  Modified code
#  Copyright (c) 2020 Takashi Masuyama
#  License: https://kcj.mit-license.org/@2017

import argparse
import cairo
import os
import platform
import re
import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk  # noqa E402
from gi.repository import Gdk # noqa E402
from gi.repository import GLib # noqa E402

FG_RED = 0
FG_GREEN = 1
FG_RED = 0
FONT_SIZE = 24
FONT_NAME = None


class TransparentTextWindow(Gtk.Window):
    def __init__(self, text):
        Gtk.Window.__init__(self)

        self.connect('destroy', Gtk.main_quit)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        # visual = screen.get_rgba_visual()
        # if visual and screen.is_composited():
        #     self.set_visual(visual)
        self.text = " ".join(text)
        print(self.text)
        self.width = screen.get_width()
        self.height = 35
        self.set_size_request(self.width, self.height)
        self.set_resizable(True)
        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.add(self.darea)
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.show_all()        

    def on_draw(self, wid, cr):
        cr.select_font_face(FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(20)
        cr.set_source_rgb(FG_RED, FG_GREEN, FG_BLUE)
        cr.move_to(15, 25)
        cr.show_text(self.text)
        cr.stroke()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--red', type=float, default=0.0)
    parser.add_argument('-g', '--green', type=float, default=1.0)
    parser.add_argument('-b', '--blue', type=float, default=0.0)
    parser.add_argument('-f', '--font', type=str, default=None)
    parser.add_argument('text', nargs='+', help='text')

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

    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
    TransparentTextWindow(args.text)
    Gtk.main()
