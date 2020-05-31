#!/usr/bin/env python3

#  Original code
#  https://gist.github.com/KurtJacobson/374c8cb83aee4851d39981b9c7e2c22c
#  Copyright (c) 2017 Kurt Jacobson
#  License: https://kcj.mit-license.org/@2017

#  Modified code
#  Copyright (c) 2020 Takashi Masuyama

import argparse
import cairo
import os
import platform
import re
import signal
import svgwrite
import sys
import traceback
try:
    import thread
except ImportError:
    import _thread as thread
import uuid
import websocket
import xml.etree.ElementTree as ET
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk  # noqa E402
from gi.repository import Gdk  # noqa E402
from gi.repository import GLib  # noqa E402
from gi.repository import GdkPixbuf  # noqa E402

APP_DEFAULT_TITLE = "Gtk3 OHP"
CLEAR_SHAPES_ON_MESSAGE = False
# initial of color name should be different
COLOR_KEYS = ["red", "navy", "green", "black", "pink", "yellow",
              "murasaki", "white", "aqua", "orange"]
COLOR_CONFIG = {
    "red": "FF0000",
    "navy": "00008D",
    "green": "00FF00",
    "black": "000000",
    "pink": "FF1493",
    "yellow": "FFFF00",
    "murasaki": "800080",
    "white": "FFFFFF",
    "aqua": "00FFFF",
    "orange": "FFA500",
    "blue": "0000FF",
    "gray": "808080",
    "purple": "800080",
    "fuchsia": "FF00FF",
}
PEN_WIDTH_LIST = [1, 2, 3, 5, 8, 13, 21, 34, 55]
FONT_SIZE_LIST = [12, 24, 48, 72, 96, 120, 240, 360, 480]
FRAME_WIDTH = 4
FRAME_COLOR = (1, 0, 0)

COMMAND_MASK = 0x10000010
LINE_WIDTH = 5
DEFAULT_FONT_SIZE = 24
FONT_NAME = None
# Ctrl-z: undo
# Ctrl-y: redo
COLOR_NAME2COLOR = None
KEY2COLOR_NAME = None


class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class TransparentWindow(Gtk.Window):
    def to_color(self, s):
        m = re.match(r"rgb\(([0-9.]+)%,([0-9.]+)%,([0-9.]+)%\)", s)
        if m is not None:
            color = (int(float(m.group(1))),
                     int(float(m.group(2))),
                     int(float(m.group(3))))
        else:
            color = COLOR_NAME2COLOR.get(s, (0, 0, 0))
        return color

    def visit(self, element, transform, result):
        for child in element:
            if child.tag in ["{http://www.w3.org/2000/svg}g",
                             "{http://www.w3.org/2000/svg}svg"]:
                transform_str = child.attrib.get("transform")
                if transform_str is not None:
                    m = re.match(r"matrix\(([0-9.]+),([0-9.]+),([0-9.]+),([0-9.]+),([0-9.]+),([0-9.]+)\)", transform_str)
                    if m is not None:
                        transform_new = cairo.Matrix(float(m.group(1)),
                                                     float(m.group(2)),
                                                     float(m.group(3)),
                                                     float(m.group(4)),
                                                     float(m.group(5)),
                                                     float(m.group(6)))
                        print(transform)
                        transform = transform.multiply(transform_new)
                self.visit(child, transform, result)
            elif child.tag == "{http://www.w3.org/2000/svg}polyline":
                points = list(map(lambda s: tuple(map(lambda x: int(float(x)), s.split(","))),
                                  child.attrib["points"].split(" ")))
                stroke = child.attrib["stroke"]
                color = self.to_color(stroke)
                stroke_width = int(float(child.attrib["stroke-width"]))
                result.append({"type": "line",
                               "points": points,
                               "color": color,
                               "width": stroke_width})
            elif child.tag == "{http://www.w3.org/2000/svg}text":
                position = (int(float(child.attrib["x"])), int(float(child.attrib["y"])))
                stroke = child.attrib.get("stroke")
                if stroke is None:
                    stroke = child.attrib.get("stroke", "red")
                font_size = int(child.attrib.get("font_size", str(DEFAULT_FONT_SIZE)))
                color = self.to_color(stroke)
                t = ET.tostring(child,
                                encoding="utf-8",
                                method="text").decode("utf-8")
                text = ET.tostring(child,
                                   encoding="utf-8",
                                   method="xml").decode("utf-8")
                result.append({"type": "text",
                               "position": position,
                               "font_size": font_size,
                               "color": color,
                               "text": text})
            elif child.tag == "{http://www.w3.org/2000/svg}rect":
                width = child.attrib["width"]
                height = child.attrib["height"]
                # TODO; use attribute not stylesheet
                color_name = child.attrib.get("fill")
                if color_name is None:
                    class_name = child.attrib.get("class")
                    if class_name is not None:
                        color_name = class_name.split("_")[0]
                    else:
                        color_name = "red"
                if color_name == "none":
                    continue
                color = self.to_color(color_name)
                x = float(child.attrib.get("x", 0))
                y = float(child.attrib.get("y", 0))
                width = float(child.attrib.get("width", 10))
                height = float(child.attrib.get("height", 10))
                position = transform.transform_point(x, y)
                result.append({"type": "rect",
                               "position": position,
                               "color": color,
                               "width": width,
                               "height": height})

            # image
            # elif child.tag == "{http://www.w3.org/2000/svg}image":
        return result

    def load_svg_file(self, svgfile):
        tree = ET.parse(svgfile)
        root = tree.getroot()
        idm = cairo.Matrix(1, 0, 0, 1, 0, 0)
        return self.visit(root, idm, [])

    def add_tmp_file(self):
        self.page_filename_list.append(uuid.uuid4().hex + ".svg")
        self.pages = [[]]

    def insert_next_page(self, overwrap=False):
        if overwrap:
            shapes = self.get_current_shapes().copy()
        else:
            shapes = []
        self.page_index += 1
        print("insert_next_page {} {}".format(overwrap, self.page_index))
        self.page_filename_list.insert(self.page_index,
                                       uuid.uuid4().hex + ".svg")
        self.pages.insert(self.page_index, shapes)
        self.redraw()

    def insert_previous_page(self):
        self.page_filename_list.insert(self.page_index,
                                       uuid.uuid4().hex + ".svg")
        self.pages.insert(self.page_index, [])
        self.redraw()

    def delete_current_page(self):
        if len(self.pages) == 1:
            return
        del self.pages[self.page_index]
        self.page_index = min(self.page_index, len(self.pages)-1)
        self.redraw()

    def next_page(self):
        self.page_index += 1
        self.page_index = self.page_index % len(self.pages)
        self.redraw()

    def previous_page(self):
        self.page_index -= 1
        if self.page_index < 0:
            self.page_index = len(self.pages) - 1
        self.redraw()

    def get_current_shapes(self):
        return self.pages[self.page_index]

    def __init__(self,
                 output_filename="ohp.svg",
                 svgfiles=[],
                 geometry=None,
                 transparent=True,
                 foregrond_color=(0, 1, 0),
                 background_color=(1, 1, 1),
                 background_image=None,
                 line_width=5,
                 font_size=DEFAULT_FONT_SIZE,
                 title=APP_DEFAULT_TITLE,
                 websock_url=None):
        Gtk.Window.__init__(self)
        dirname = os.path.abspath(os.path.dirname(__file__))
        icon_path = "icon/suke_icon.png"
        icon_abs_path = os.path.join(dirname, icon_path)
        if os.path.exists(icon_abs_path):
            self.set_icon(GdkPixbuf.Pixbuf.new_from_file(icon_abs_path))
        self.page_index = 0
        self.pages = []
        self.page_filename_list = []
        self.foregrond_color = foregrond_color
        self.background_color = background_color
        self.background_image = background_image
        self.background_image_pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.background_image)
        self.line_width = line_width
        self.font_size = font_size
        self.title = title
        self.lambdalast_load_len = 0
        self.connect("destroy", Gtk.main_quit)
        self.button_pressed = False
        self.drawing_line = False
        self.output_filename = output_filename
        # self.tmp_filename = uuid.uuid4().hex + ".svg"

        screen = self.get_screen()
        self.transparent = transparent
        if self.transparent:
            visual = screen.get_rgba_visual()
            if visual and screen.is_composited():
                self.set_visual(visual)

        self.set_hide_titlebar_when_maximized(True)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        # TODO use monitor api
        self.is_fullscreen = True
        if geometry is None:
            self.width = screen.get_width()
            self.height = screen.get_height()
            self.x_offset = 0
            self.y_offset = 0
        else:
            (self.width, self.height, self.x_offset, self.y_offset) = geometry
        self.move(self.x_offset, self.y_offset)
        self.set_size_request(self.width, self.height)
        self.set_resizable(True)
        self.set_title(self.title)

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.darea.set_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON1_MOTION_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        self.add(self.darea)
        self.insert_previous_page()
        self.redo_shapes = []
        self.coords = []
        self.link = []
        self.last_position = (0, 0)

        self.darea.connect("button-press-event", self.on_button_press)
        self.darea.connect("button-release-event", self.on_button_release)
        self.darea.connect("motion-notify-event", self.on_move)
        self.connect("key-press-event", self.on_key_press)

        self.connect("delete-event", Gtk.main_quit)
        self.set_app_paintable(True)
        self.set_keep_above(True)

        shapes = self.get_current_shapes()
        for svgfile in svgfiles:
            result = self.load_svg_file(svgfile)
            shapes.extend(result)

        self.present()

        def on_open(ws):
            print("on_open")

        def on_message(ws, message):
            # TODO merge shapes, craate svg element for loaded image
            shapes = self.get_current_shapes()
            local_shapes = shapes[self.last_load_len:]
            shapes.clear()
            tmp_filename = self.page_filename_list[self.page_index]
            with open(tmp_filename, "w") as f:
                f.write(message)
            shapes.extend(self.load_svg_file(tmp_filename))
            shapes.extend(local_shapes)
            self.redraw()

        def on_close(ws):
            print("websocket closed")
            self.start_websocket()

        def on_error(ws, error):
            print(error)
            self.start_websocket()

        self.websock_running = False
        if websock_url is not None:
            self.websock_url = websock_url
            print(self.websock_url)
            # websocket.enableTrace(True)
            self.websock = websocket.WebSocketApp(websock_url,
                                                  on_open=on_open,
                                                  on_message=on_message,
                                                  on_error=on_error,
                                                  on_close=on_close)
            self.start_websocket()
        else:
            self.websock_url = None
            self.websock = None

        self.show_all()

    def start_websocket(self):
        def run(*args):
            try:
                print("thread run")
                self.websock_running = True
                self.websock.run_forever()
            except Exception:
                print(traceback.format_exc())
            finally:
                print("websock finished")
                self.websock_running = False
        if not self.websock_running:
            thread.start_new_thread(run, ())

    def fullscreen(self):
        self.set_size_request(self.width, self.height)
        self.resize(self.width, self.height)
        self.is_fullscreen = True

    def minimize(self):
        # 10: min height
        min_height = 10
        self.set_size_request(self.width, min_height)
        self.resize(self.width, min_height)
        self.is_fullscreen = False

    def clear(self):
        self.pages[self.page_index].clear()
        self.redo_shapes = []
        self.coords = []
        self.link = []
        self.last_position = (0, 0)

    def redraw(self):
        self.darea.queue_draw()

    def send(self):
        if self.websock is None:
            print("no websock")
            return
        with open(self.output_filename) as f:
            self.websock.send(f.read())

    def save(self):
        dwg = svgwrite.Drawing(self.output_filename, profile="full")
        shapes = self.get_current_shapes()
        for shape in shapes:
            shape_type = shape["type"]
            if shape_type == "line":
                # color 0 - 1.0 -> percentage
                color = tuple(map(lambda x: min(x * 100, 100), shape["color"]))
                pline = dwg.polyline(
                    points=shape["points"],
                    stroke=svgwrite.rgb(color[0], color[1], color[2], "%"),
                    stroke_width=shape["width"],
                    fill_opacity=0,
                )
                dwg.add(pline)
            elif shape_type == "text":
                text = shape["text"]
                color = tuple(map(lambda x: min(x * 100, 100), shape["color"]))
                dwg.add(
                    dwg.text(
                        text,
                        font_size=self.font_size,
                        font_family=FONT_NAME,
                        insert=shape["position"],
                        stroke=svgwrite.rgb(*color, "%"),
                    )
                )
            elif shape_type == "rect":
                width = shape["width"]
                height = shape["height"]
                color = tuple(map(lambda x: min(x * 100, 100), shape["color"]))
                position = shape["position"]
                dwg.add(
                    dwg.rect(
                        insert=position,
                        size=(width, height),
                        fill=svgwrite.rgb(*color, "%"),
                    )
                )

            # elif shape_type == "image":
        dwg.save()

    def on_key_press(self, wid, event):
        ctrl = (
            (event.state & Gdk.ModifierType.CONTROL_MASK)
            == Gdk.ModifierType.CONTROL_MASK
            or (event.state & COMMAND_MASK) == COMMAND_MASK
        )
        shift = (
            (event.state & Gdk.ModifierType.SHIFT_MASK)
            == Gdk.ModifierType.SHIFT_MASK
        )
        shapes = self.get_current_shapes()
        print(event.keyval)
        print(Gdk.KEY_plus)
        if ctrl and event.keyval == Gdk.KEY_q:
            # TODO: ask save data or not
            Gtk.main_quit()
        elif ctrl and event.keyval == Gdk.KEY_z and 0 < len(shapes):
            self.redo_shapes.append(shapes[-1])
            del shapes[-1]
            self.redraw()
        elif ctrl and event.keyval == Gdk.KEY_y and 0 < len(self.redo_shapes):
            shapes.append(self.redo_shapes[-1])
            del self.redo_shapes[-1]
            self.redraw()
        elif ctrl and event.keyval == Gdk.KEY_s:
            self.save()
            self.send()
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
                shapes.append(
                    {
                        "position": self.last_position,
                        "type": "text",
                        "font_size": self.font_size,
                        "color": self.foregrond_color,
                        "text": text,
                    }
                )
                self.redraw()
                return
            image = self.clipboard.wait_for_image()
            if image is not None:
                shapes.append(
                    {
                        "position": self.last_position,
                        "type": "image",
                        "image": image
                    }
                )
                self.redraw()
        elif event.keyval == Gdk.KEY_plus:
            # add page and copy current shapes
            self.insert_next_page(True)
        elif (ctrl and event.keyval == Gdk.KEY_t):
            self.insert_next_page()
        elif (ctrl and event.keyval == Gdk.KEY_T):
            # shift -> copy
            self.insert_next_page(True)
        elif (ctrl and shift and event.keyval == Gdk.KEY_N):
            self.insert_next_page()
        elif ctrl and shift and event.keyval == Gdk.KEY_P:
            self.insert_previous_page()
        elif ctrl and event.keyval == Gdk.KEY_n:
            self.next_page()
        elif ctrl and event.keyval == Gdk.KEY_p:
            self.previous_page()
        elif ctrl and event.keyval == Gdk.KEY_w:
            self.delete_current_page()
        elif ctrl and event.keyval == Gdk.KEY_o:
            self.transparent = not self.transparent
            self.redraw()
        else:
            color_name = KEY2COLOR_NAME.get(event.keyval)
            if color_name is not None:
                self.foregrond_color = COLOR_NAME2COLOR[color_name]
            if event.keyval in range(ord("1"), ord(str(len(PEN_WIDTH_LIST))) + 1):
                self.line_width = PEN_WIDTH_LIST[event.keyval - ord("1")]
            if event.keyval in range(ord("1"), ord(str(len(FONT_SIZE_LIST))) + 1):
                self.font_size = FONT_SIZE_LIST[event.keyval - ord("1")]

    def draw_line(self, wid, cr, points):
        if len(points) < 2:
            return

        start = points[0]
        cr.move_to(start[0], start[1])

        for p in points[1:]:
            cr.move_to(start[0], start[1])
            cr.line_to(p[0], p[1])
            start = p
        cr.stroke()

    def draw_shapes(self, wid, cr, shapes):
        for shape_info in shapes:
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
                color = shape_info["color"]
                cr.set_source_rgb(*color)
                cr.set_line_width(self.line_width)
                font_size = shape_info.get("font_size", DEFAULT_FONT_SIZE)
                cr.set_font_size(font_size)
                if FONT_NAME is not None:
                    cr.select_font_face(
                        FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
                    )
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
            elif shape_type == "line":
                points = shape_info["points"]
                color = shape_info["color"]
                width = shape_info["width"]
                cr.set_source_rgb(color[0], color[1], color[2])
                cr.set_line_width(width)
                self.draw_line(wid, cr, points)
            elif shape_type == "rect":
                position = shape_info["position"]
                color = shape_info["color"]
                width = shape_info["width"]
                height = shape_info["height"]
                position = shape_info["position"]
                cr.set_source_rgb(color[0], color[1], color[2])
                cr.rectangle(position[0],
                             position[1],
                             width,
                             height)
                cr.fill()
            else:
                print("unknown shpae: " + shape_type)

    def on_draw(self, wid, cr):
        # TODO: reduce operation
        if self.background_image_pixbuf is not None:
            Gdk.cairo_set_source_pixbuf(cr,
                                        self.background_image_pixbuf,
                                        0,
                                        0)
            cr.paint()
        else:
            if not self.transparent:
                cr.set_source_rgba(*self.background_color)
                cr.rectangle(0, 0, self.width, self.height)
                cr.fill()

        self.draw_shapes(wid, cr, self.get_current_shapes())

        if self.drawing_line:
            cr.set_source_rgb(*self.foregrond_color)
            cr.set_line_width(self.line_width)

            self.draw_line(wid, cr, self.coords)
        # draw frame
        current = (0, 0)
        cr.move_to(*current)
        cr.set_source_rgb(*FRAME_COLOR)
        cr.set_line_width(FRAME_WIDTH)
        for point in [
            (self.width, 0),
            (self.width, self.height),
            (0, self.height),
            (0, 0),
        ]:
            cr.line_to(*point)
        cr.stroke()

    def link_clicked(self, link, x, y):
        lx = link["position"][0]
        ly = link["position"][1]
        box_size = 20
        # TODO modify size
        return (
            lx - box_size <= x
            and x <= lx + box_size
            and ly - box_size <= y
            and y <= ly + box_size
        )

    def open_link(self, url):
        # mac
        os.system("open '%s'" % url)

    def on_button_press(self, w, e):
        if (
            e.type == Gdk.EventType.BUTTON_PRESS
            and e.button == MouseButtons.LEFT_BUTTON
        ):

            for link in self.link:
                if self.link_clicked(link, e.x, e.y):
                    self.open_link(link["url"])
                    break
            self.last_position = (e.x, e.y)
            self.coords.append([e.x, e.y])
            self.button_pressed = True
            self.drawing_line = True

    def on_button_release(self, w, e):
        if (
            e.type == Gdk.EventType.BUTTON_RELEASE
            and e.button == MouseButtons.LEFT_BUTTON
        ):
            shapes = self.get_current_shapes()
            if 1 < len(self.coords):

                shapes.append(
                    {
                        "type": "line",
                        "color": self.foregrond_color,
                        "width": self.line_width,
                        "points": self.coords,
                    }
                )
            self.coords = []
            self.last_position = (e.x, e.y)
            self.button_pressed = False
            self.drawing_line = False
            self.redraw()

    def on_move(self, w, e):
        if self.button_pressed:
            self.coords.append([e.x, e.y])
            self.last_position = (e.x, e.y)
            self.redraw()


def hex2float(h):
    (rx, gx, bx) = (h[0:2], h[2:4], h[4:6])
    return (int(rx, 16) / 0xFF, int(gx, 16) / 0xFF, int(bx, 16) / 0xFF)


def make_color_table():
    key2color_name = {}
    color_name2color = {}

    for name in COLOR_KEYS:
        color_code = COLOR_CONFIG[name]
        keycode = ord(name[0:1].upper())
        key2color_name[keycode] = name

    for (name, color) in COLOR_CONFIG.items():
        color_code = COLOR_CONFIG[name]
        color = hex2float(color_code)
        color_name2color[name] = color

    return (key2color_name, color_name2color)


def int_or_zero(s):
    if s is None:
        return 0
    else:
        return int(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--foreground-color", type=str, default="0,1,0")
    parser.add_argument("--background-color", type=str, default="1,1,1")
    parser.add_argument("--background-image", type=str, default=None)
    parser.add_argument("--line-width", type=float, default=4.0)
    parser.add_argument("--font", type=str, default=None)
    parser.add_argument("-o", "--output", type=str, default="ohp.svg")
    parser.add_argument("-s", "--socket", type=str, default=None)
    parser.add_argument("--geometry", type=str, default=None)
    parser.add_argument("--title", type=str, default=APP_DEFAULT_TITLE)
    parser.add_argument("--opaque", action="store_true")

    parser.add_argument("svgfiles", metavar="svgfile", type=str, nargs="*", default=[])

    args = parser.parse_args()
    os_release = platform.system()

    if args.font is not None:
        FONT_NAME = args.font
    else:
        if os_release == "Darwin":
            # TODO: if japanese
            FONT_NAME = "Osaka"
        elif os_release == "Linux":
            # ubuntu?
            FONT_NAME = "TakaoGothic"
        elif os_release == "Windows":
            FONT_NAME = "meiryo"
    geometry = None
    if args.geometry:
        m = re.match(r"(\d+)x(\d+)(\+(\d+))?(\+(\d+))?", args.geometry)
        if m is not None:
            geometry = (int(m.group(1)),
                        int(m.group(2)),
                        int_or_zero(4),
                        int_or_zero(6))

    (r, g, b) = args.foreground_color.split(",")
    foreground_color = (min(1, float(r)),
                        min(1, float(g)),
                        min(1, float(b)))
    (r, g, b) = args.background_color.split(",")
    background_color = (min(1, float(r)),
                        min(1, float(g)),
                        min(1, float(b)))
    line_width = args.line_width
    (KEY2COLOR_NAME, COLOR_NAME2COLOR) = make_color_table()

    Gtk.init(sys.argv)
    if os_release != "Windows":
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
    TransparentWindow(output_filename=args.output,
                      svgfiles=args.svgfiles,
                      geometry=geometry,
                      transparent=not args.opaque,
                      foregrond_color=foreground_color,
                      background_color=(1, 1, 1),
                      background_image=args.background_image,
                      line_width=line_width,
                      title=args.title,
                      font_size=DEFAULT_FONT_SIZE,
                      websock_url=args.socket)

    Gtk.main()
