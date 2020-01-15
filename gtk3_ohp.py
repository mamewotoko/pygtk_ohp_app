#!/usr/bin/env python

#  Copyright (c) 2017 Kurt Jacobson
#  License: https://kcj.mit-license.org/@2017

import cairo
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class TransparentWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_size_request(1000, 1000)

        self.connect('destroy', Gtk.main_quit)
        # self.connect('draw', self.draw)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)        
        self.add(self.darea)
        
        self.coords = []
                     
        self.darea.connect("button-press-event", self.on_button_press)

        self.set_title("Lines")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.set_app_paintable(True)
        self.show_all()
            
    def on_draw(self, wid, cr):
        print('on draw')
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        
        for i in self.coords:
            for j in self.coords:
                
                cr.move_to(i[0], i[1])
                cr.line_to(j[0], j[1]) 
                cr.stroke()

        del self.coords[:]            
                         
    def on_button_press(self, w, e):
        if e.type == Gdk.EventType.BUTTON_PRESS \
            and e.button == MouseButtons.LEFT_BUTTON:
            
            self.coords.append([e.x, e.y])
            
        if e.type == Gdk.EventType.BUTTON_PRESS \
            and e.button == MouseButtons.RIGHT_BUTTON:
            
            self.darea.queue_draw()           

if __name__ == '__main__':
    TransparentWindow()
    Gtk.main()
