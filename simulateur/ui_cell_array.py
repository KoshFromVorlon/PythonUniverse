# -*- coding: utf-8 -*-

#####################
# cell array widget #
#####################

# includes
import pygtk
pygtk.require('2.0')
import gtk
import glib
import math
import Image

from config import *
import ui_editor

import monde
import composants

# cell array
class Cell_array (gtk.DrawingArea):
   # resize event
   def ca_ev_configure (self, widget, event):
      x, y, w, h = self.get_allocation ()
      
      # recreate new pixmap
      self.ca_pixmap = gtk.gdk.Pixmap (self.window, w, h)
      
      # colors graphic context
      colormap = self.ca_pixmap.get_colormap ()
      self.ca_gc = [
         self.ca_pixmap.new_gc (foreground = ui_color[0]),
         self.ca_pixmap.new_gc (foreground = ui_color[1]),
         self.ca_pixmap.new_gc (foreground = ui_color[2]),
         self.ca_pixmap.new_gc (foreground = ui_color[3])
         ]
      self.ca_grid_gc = self.ca_pixmap.new_gc (foreground = ui_color[4])
      self.ca_highlight_gc = self.ca_pixmap.new_gc (foreground = ui_color[5])
      self.ca_background_gc = self.ca_pixmap.new_gc (foreground = ui_color[6])
      
      # redraw
      self.ca_draw ()
      return True
   
   # event redraw part of screen
   def ca_ev_exposure (self, widget, event):
      x, y, w, h = event.area
      self.window.draw_drawable (self.get_style().fg_gc[gtk.STATE_NORMAL], self.ca_pixmap, x, y, x, y, w, h)
      return False
   
   # when one scrollbar is used
   def ca_ev_scroll (self, range, data):
      value = range.get_value ()
      if value != 0:
         screen_w, screen_h = self.ca_pixmap.get_size ()
         if data:
            self.ca_move (0, int (ui_config['cell_array_move_factor'] * screen_h * value / self.ca_zoom))
         else:
            self.ca_move (int (ui_config['cell_array_move_factor'] * screen_w * value / self.ca_zoom), 0)
         range.set_value (0)
         self.ca_draw ()
   
   # zoom changed
   def ca_ev_zoom (self, range, data = None):
      self.ca_zoom = int (math.sqrt (range.get_value ()))
      self.ca_draw ()
   
   # mouse event (click, move, enter/leave widget)
   def ca_ev_mouse (self, widget, event, code):
      # we only use mouse left button
      if (event.type != gtk.gdk.BUTTON_PRESS and event.type != gtk.gdk.BUTTON_RELEASE) or event.button == 1:
         x, y = event.get_coords ()
         screen_w, screen_h = self.ca_pixmap.get_size ()
         
         # cast to int
         x = int (x)
         y = int (y)

         # converting screen coordinates to virtual coordinates (infinite plan)
         vx = (x - (screen_w / 2)) / self.ca_zoom + self.ca_view_x
         vy = (y - (screen_h / 2)) / self.ca_zoom + self.ca_view_y

         self.ca_editor.do_event (code, (vx, vy))
      return True
      
   # create widget
   def __init__ (self):
      # create gtkImage widget
      gtk.DrawingArea.__init__ (self)
      self.set_size_request (ui_config['cell_array_resize_min_width'], ui_config['cell_array_resize_min_height'])
      self.add_events (gtk.gdk.BUTTON1_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK |
         gtk.gdk.EXPOSURE_MASK | gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)
      self.connect ('configure-event', self.ca_ev_configure)
      self.connect ('expose-event', self.ca_ev_exposure)
      self.connect ('button-press-event', self.ca_ev_mouse, ev_const.MOUSE_BUTTON_PRESS)
      self.connect ('button-release-event', self.ca_ev_mouse, ev_const.MOUSE_BUTTON_RELEASE)
      self.connect ('motion-notify-event', self.ca_ev_mouse, ev_const.MOUSE_MOTION)
      self.connect ('enter-notify-event', self.ca_ev_mouse, ev_const.MOUSE_ENTER)
      self.connect ('leave-notify-event', self.ca_ev_mouse, ev_const.MOUSE_LEAVE)
            
      # variables
      self.ca_zoom = ui_config['cell_array_default_zoom']
      self.ca_view_x = 0
      self.ca_view_y = 0
      self.ca_map = composants.Component (0, 0)
      self.ca_editor = ui_editor.Editor (self)
   
   # center the view on the map
   def ca_center (self):
      x, y = self.ca_map.get_orig ()
      w, h = self.ca_map.get_size ()
      self.ca_view_x = x + w / 2
      self.ca_view_y = y + h / 2
      self.ca_draw ()
      
   # move the view
   def ca_move (self, dx, dy):
      self.ca_view_x = self.ca_view_x + dx
      self.ca_view_y = self.ca_view_y + dy
   
   # compute an iteration
   def ca_iter (self):
      self.ca_map.iter_step ()
      
   # change cursor
   def ca_set_cursor (self, cursor):
      self.window.set_cursor (gtk.gdk.Cursor (cursor))
      
   # draw the map on the screen
   def ca_draw (self):
      # temp variables
      screen_w, screen_h = self.ca_pixmap.get_size ()
      map_x, map_y = self.ca_map.get_orig ()
      map_w, map_h = self.ca_map.get_size ()
      
      # opt
      center_x = screen_w / 2
      center_y = screen_h / 2
      orig_x = center_x + (map_x - self.ca_view_x) * self.ca_zoom
      orig_y = center_y + (map_y - self.ca_view_y) * self.ca_zoom
      zoom = self.ca_zoom
      
      # grid
      if ui_config['cell_array_grid_enabled'] and self.ca_zoom >= ui_config['cell_array_grid_min_zoom']:
         zoom = zoom - 1
         orig_x = orig_x + 1
         orig_y = orig_y + 1
      
      # determine visible range (index)
      range_x_l = max (0, -center_x / self.ca_zoom + self.ca_view_x - map_x)
      range_x_r = min (map_w, 1 + center_x / self.ca_zoom + self.ca_view_x - map_x)
      range_y_l = max (0, -center_y / self.ca_zoom + self.ca_view_y - map_y)
      range_y_r = min (map_h, 1 + center_y / self.ca_zoom + self.ca_view_y - map_y)
            
      # erase
      self.ca_pixmap.draw_rectangle (self.ca_background_gc, True, 0, 0, screen_w,screen_h)
      
      # print the map
      for x in range (range_x_l, range_x_r):
         for y in range (range_y_l, range_y_r):
            if self.ca_map.get_state(x, y) != sim_const.EMPTY or ui_config['cell_array_map_show']:
               self.ca_pixmap.draw_rectangle (self.ca_gc[self.ca_map.get_state(x, y)], True,
                  orig_x + x * self.ca_zoom,
                  orig_y + y * self.ca_zoom,
                  zoom,
                  zoom)
               
      # editor highlighted
      for x, y in self.ca_editor.get_highlighted ():
         self.ca_pixmap.draw_rectangle (self.ca_highlight_gc, True,
            center_x + (x - self.ca_view_x) * self.ca_zoom,
            center_y + (y - self.ca_view_y) * self.ca_zoom,
            self.ca_zoom,
            self.ca_zoom)
               
      # print grid
      if ui_config['cell_array_grid_enabled'] and self.ca_zoom >= ui_config['cell_array_grid_min_zoom']:
         for x in range (center_x, screen_w, self.ca_zoom):
            self.ca_pixmap.draw_line (self.ca_grid_gc, x, 0, x, screen_h)
         for x in range (center_x, -1, -self.ca_zoom):
            self.ca_pixmap.draw_line (self.ca_grid_gc, x, 0, x, screen_h)
         for y in range (center_y, screen_h, self.ca_zoom):
            self.ca_pixmap.draw_line (self.ca_grid_gc, 0, y, screen_w, y)
         for y in range (center_y, -1, -self.ca_zoom):
            self.ca_pixmap.draw_line (self.ca_grid_gc, 0, y, screen_w, y)

      # draw changes
      self.queue_draw ()
      
   # save to a file
   def ca_save (self, filename, dest_map):
      ret = True
      if dest_map:
         ca_map = self.ca_map
      else:
         ca_map = self.ca_editor.component_buffer
         
      # test if the map is empty
      w, h = ca_map.get_size ()
      if (w, h) != (0, 0):
         # create buffers
         pixbuf = gtk.gdk.Pixbuf (gtk.gdk.COLORSPACE_RGB, False, 8, w * self.ca_zoom, h * self.ca_zoom)
         pixmap = gtk.gdk.Pixmap (self.window, w * self.ca_zoom, h * self.ca_zoom)
         
         # print the map
         for x in range (w):
            for y in range (h):
               pixmap.draw_rectangle (self.ca_gc[ca_map.get_state(x, y)], True,
               x * self.ca_zoom,
               y * self.ca_zoom,
               self.ca_zoom,
               self.ca_zoom)
         
         # save image
         pixbuf.get_from_drawable (pixmap, pixmap.get_colormap (), 0, 0, 0, 0, -1, -1)
         try:
            pixbuf.save (filename, 'png')
         except glib.GError:
            ret = False
         del pixbuf
         del pixmap
      else:
         ret = False
      return ret

   # load from file
   def ca_load (self, filename, cell_size, dest_map):
      ret = True
      try:
         img = Image.open (filename)
      except IOError:
         ret = False
      if ret:
         size = img.getbbox ()
         if size != None:
            xs, ys, xe, ye = size
            w = (xe - xs) / cell_size
            h = (ye - ys) / cell_size
            if w > 0 and h > 0:
               colors = [
                  gtk.gdk.color_parse (ui_config['cell_array_color_empty']),
                  gtk.gdk.color_parse (ui_config['cell_array_color_wire']),
                  gtk.gdk.color_parse (ui_config['cell_array_color_head']),
                  gtk.gdk.color_parse (ui_config['cell_array_color_tail'])
                  ]
               ca_map = composants.Component (w, h)
               for x in range (w):
                  for y in range (h):
                     pix = img.getpixel ((xs + cell_size / 2 + x * cell_size, ys + cell_size / 2 + y * cell_size))
                     if len (pix) == 4:
                        r, g, b, _ = pix
                     elif len (pix) == 3:
                        r, g, b = pix
                     else:
                        return False
                     diff = map (lambda c:abs (r - c.red / 256) + abs (g - c.green / 256) + abs (b - c.blue / 256), colors)
                     i = diff.index (min (diff))
                     ca_map.set_state (x, y, i)
               if dest_map:
                  self.ca_map = ca_map
               else:
                  self.ca_editor.component_buffer = ca_map
               self.ca_center ()
            else:
               ret = False
         else:
            ret = False
      return ret
      
