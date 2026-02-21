# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import glib
import sys

# constants
class ui_const:
   MODE_EDIT = 0
   MODE_RUN = 1
   TOOL_MOVE = 2
   TOOL_PENCIL = 3
   TOOL_ASTAR = 4
   TOOL_ERASER = 5
   TOOL_COPY = 6
   TOOL_PASTE = 7
   TOOL_RESIZE = 8
   TOOL_PATH = 9

class ev_const:
   MOUSE_BUTTON_PRESS = 0
   MOUSE_BUTTON_RELEASE = 1
   MOUSE_MOTION = 2
   MOUSE_ENTER = 3
   MOUSE_LEAVE = 4

class sim_const:
   EMPTY = 0
   WIRE = 1
   HEAD = 2
   TAIL = 3

# configuration data (often default configuration)
ui_config = {
   'main_window_default_width' : 640,
   'main_window_default_height' : 480,
   'cell_array_map_show' : True,
   'cell_array_resize_min_width' : 200,
   'cell_array_resize_min_height' : 100,
   'cell_array_default_zoom' : 5,
   'cell_array_max_zoom' : 50,
   'cell_array_grid_enabled' : True,
   'cell_array_grid_min_zoom' : 4,
   'cell_array_move_factor' : 0.5,
   'cell_array_color_empty' : '#000',
   'cell_array_color_wire' : '#A50',
   'cell_array_color_head' : '#FFF',
   'cell_array_color_tail' : '#00A',
   'cell_array_color_grid' : '#AAA',
   'cell_array_color_highlight' : '#F00',
   'cell_array_color_background' : '#222',
   'editor_action_preview_enabled' : True
}

# configuration functions
ui_color = [
   gtk.gdk.colormap_get_system ().alloc_color (ui_config['cell_array_color_empty']),
   gtk.gdk.colormap_get_system ().alloc_color (ui_config['cell_array_color_wire']),
   gtk.gdk.colormap_get_system ().alloc_color (ui_config['cell_array_color_head']),
   gtk.gdk.colormap_get_system ().alloc_color (ui_config['cell_array_color_tail']),
   gtk.gdk.colormap_get_system ().alloc_color (ui_config['cell_array_color_grid']),
   gtk.gdk.colormap_get_system ().alloc_color (ui_config['cell_array_color_highlight']),
   gtk.gdk.colormap_get_system ().alloc_color (ui_config['cell_array_color_background'])
   ]

def gtk_create_user_icons ():
   icon_factory = gtk.IconFactory ()
   pixmap = gtk.gdk.Pixmap (None, 1, 1, 24)
   
   # colors
   pixbuf = gtk.gdk.Pixbuf (gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
   pixmap.draw_point (pixmap.new_gc (foreground = ui_color[0]), 0, 0)
   icon_factory.add ('cell_array_color_empty', gtk.IconSet (pixbuf.get_from_drawable (pixmap, pixmap.get_colormap (), 0, 0, 0, 0, -1, -1)))
   pixbuf = gtk.gdk.Pixbuf (gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
   pixmap.draw_point (pixmap.new_gc (foreground = ui_color[1]), 0, 0)
   icon_factory.add ('cell_array_color_wire', gtk.IconSet (pixbuf.get_from_drawable (pixmap, pixmap.get_colormap (), 0, 0, 0, 0, -1, -1)))
   pixbuf = gtk.gdk.Pixbuf (gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
   pixmap.draw_point (pixmap.new_gc (foreground = ui_color[2]), 0, 0)
   icon_factory.add ('cell_array_color_head', gtk.IconSet (pixbuf.get_from_drawable (pixmap, pixmap.get_colormap (), 0, 0, 0, 0, -1, -1)))
   pixbuf = gtk.gdk.Pixbuf (gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
   pixmap.draw_point (pixmap.new_gc (foreground = ui_color[3]), 0, 0)
   icon_factory.add ('cell_array_color_tail', gtk.IconSet (pixbuf.get_from_drawable (pixmap, pixmap.get_colormap (), 0, 0, 0, 0, -1, -1)))
   del pixbuf

   try:
      # edit tools
      icon_factory.add ('cell_array_tool_move', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-tool-move.png')))
      icon_factory.add ('cell_array_tool_pencil', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-tool-pencil.png')))
      icon_factory.add ('cell_array_tool_astar', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-tool-astar.png')))
      icon_factory.add ('cell_array_tool_eraser', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-tool-eraser.png')))
      icon_factory.add ('cell_array_tool_copy', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-tool-copy.png')))
      icon_factory.add ('cell_array_tool_paste', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-tool-paste.png')))
      icon_factory.add ('cell_array_tool_resize', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-tool-resize.png')))
      icon_factory.add ('cell_array_tool_path', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-tool-path.png')))

      # other actions
      icon_factory.add ('cell_array_action_center', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-action-center.png')))
      icon_factory.add ('cell_array_action_crop', gtk.IconSet (gtk.gdk.pixbuf_new_from_file ('file/icon/stock-action-crop.png')))
   except glib.GError as gerror:
      dialog = gtk.MessageDialog (None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, gerror.message)
      dialog.run ()
      dialog.destroy ()
      sys.exit (0)
   # add these icons to default
   icon_factory.add_default ()

def config_init ():
   gtk_create_user_icons ()
