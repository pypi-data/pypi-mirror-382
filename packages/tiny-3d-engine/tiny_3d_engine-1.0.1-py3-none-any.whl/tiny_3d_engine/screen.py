"""
Screen utilities
----------------

All the graphical toolkit of the 3D engine.
This module take care of the declaration and packing of the canvas,
and the drawing of the polylines.
"""

__all__ = ["Screen", "shade_color"]


import tkinter
from tkinter import font, ttk


COLOR_SCHEMES = [
    ("#666699", "#9bf6ff"),
    ("#003f5c", "#ffd380"),
    ("#1c4e4f", "#c7522a"),
    ("#5e606c", "#e4babe"),
    ("#eaeaea", "#d74a49"),
    ("#fcf1ef", "#5e606c"),
]


def hex2rgb(str_rgb):
    """Convert hexadecimal color to rgb"""
    try:
        rgb = str_rgb[1:]

        if len(rgb) == 6:
            red, grn, blu = rgb[0:2], rgb[2:4], rgb[4:6]
        elif len(rgb) == 9:
            red, grn, blu = rgb[0:3], rgb[3:6], rgb[6:9]
        elif len(rgb) == 3:
            red, grn, blu = rgb[0] * 2, rgb[1] * 2, rgb[2] * 2
        else:
            raise ValueError()
    except:
        raise ValueError("Invalid value %r provided for rgb color." % str_rgb)

    return tuple(int(val, 16) for val in (red, grn, blu))


def rgb2hex(list_rgb):
    """Convert rgb list to hex"""
    return "#{:02x}{:02x}{:02x}".format(list_rgb[0], list_rgb[1], list_rgb[2])


def shade_color(hex_color, bg_hex_color, shade):
    """Return the same color, bkended with background.

    :param color: color in HEX
    :param shade: float : 0 no blend, 1 transparent"
    """
    shade = max(shade, 0)
    shade = min(shade, 1)
    rgb_color = hex2rgb(hex_color)
    rgb_back = hex2rgb(bg_hex_color)

    blend = list()
    for i in range(3):
        val = int(rgb_color[i] * (1.0 - shade) + shade * rgb_back[i])
        blend.append(val)

    return rgb2hex(blend)


class Screen:
    """Handle all the memory-to-screen dialog"""

    def __init__(self, width, height, background, root=None, title=None):
        """Startup class"""
        # initialize tkinter window for displaying graphics
        self.colorindex = 0
        self.holder = self._create_holder(root)
        # self.motion_allowed = True
        self.help_lbl = tkinter.Label(self.holder, text="Command help")
        self.help_lbl.bind("<Button-1>", self.spawn_help_panel)
        self.help_lbl.pack(side="bottom", fill="x")

        self.current_tag = None

        self.control_panel = ttk.Frame(self.holder)
        self.control_panel.pack(side="left", fill="y")

        self.can = tkinter.Canvas(
            self.holder,
            # width=width,
            # height=height,
            bg=background,
        )
        self.can.pack(side="left", fill="both", expand=True)

        # You cannont call this befor Tk is invoked
        self.font_hud = font.Font(family="Helvetica", size=24)
        self.update_background_color()
        self.colors = None
        if self.standalone:
            self.holder.title(title)

    def update_background_color(self):
        self.colorindex += 1
        if self.colorindex >= len(COLOR_SCHEMES):
            self.colorindex = 0
        self.bg_color, self.focus_color = COLOR_SCHEMES[self.colorindex]
        self.can.configure(bg=self.bg_color)

    def update(self, colors):
        """Update informations on parts to show"""
        self.colors = colors

    def spawn_help_panel(self, event):
        """add a help panel"""
        top = tkinter.Toplevel()
        top.title("Command help...")

        msg = tkinter.Message(
            top,
            text="""
=======================
Tiny 3D engine commands
=======================

Mouse + Buttn. 1 : rotation

Shift + Mouse + Buttn. 1 : translation

                              
Buttn. 2 : hide part

Shift + Buttn. 2 : hide family


""",
        )
        msg.pack()

    def _create_holder(self, root):
        """Creet the main window if needed"""
        if root is None:
            holder = tkinter.Tk()
            self.standalone = True
        else:
            # holder = tkinter.ttk.Frame(root, name="3D view holder")
            holder = root
            self.standalone = False
        return holder

    def createShape(self, points, tag, s_color):
        """draw shape on screen"""
        self.can.create_polygon(points, fill=s_color, outline=s_color, tags=tag)

    def add_tags_bindings(self, list_tags):
        """Add the tag bindings on all parts"""
        for tag in list_tags:
            self.can.tag_bind(
                tag, "<Enter>", lambda event, arg=tag: self.enter_tag(event, arg)
            )
            self.can.tag_bind(
                tag, "<Leave>", lambda event, arg=tag: self.leave_tag(event, arg)
            )

    def enter_tag(self, event, tag):
        """Callback whe the mouse enters on a tagged surface"""
        # self.motion_allowed = False
        self.current_tag = tag
        self.can.itemconfigure(tag, outline=self.focus_color, width=4)
        self.print_text_info(event.x + 11, event.y - 11, tag, "white")
        self.print_text_info(event.x + 13, event.y - 11, tag, "white")
        self.print_text_info(event.x + 11, event.y - 13, tag, "white")
        self.print_text_info(event.x + 13, event.y - 13, tag, "white")
        self.print_text_info(event.x + 12, event.y - 12, tag, "black")

    def leave_tag(self, event, tag):
        """Callback whe the mouse leaves a tagged surface"""
        # self.motion_allowed = True
        self.current_tag = None
        self.can.delete("info")
        self.can.itemconfigure(tag, outline=self.colors[tag], width=1)

    def print_text_info(self, xpix, ypix, text, color):
        """CPrint some text on the screen"""
        self.can.create_text(
            xpix,
            ypix,
            text=text,
            anchor="w",
            tags="info",
            fill=color,
            font=self.font_hud,
        )

    def clear(self):
        """clear the display"""
        self.can.delete("all")

    def mainloop(self):
        """Start the interactive mode of the screen"""
        self.holder.mainloop()
