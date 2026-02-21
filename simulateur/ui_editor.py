# -*- coding: utf-8 -*-

################################
# edit functions and callbacks #
################################

import pygtk
pygtk.require ('2.0')
import gtk

import ui_dialog
from config import *
from composants import *
from a_star import *

def is_in_map (world, coord):
   mx, my = world.get_orig ()
   w, h = world.get_size ()
   xo, yo = coord
   return mx <= xo and xo < mx + w and my <= yo and yo < my + h
   
def is_valid_a_star (world, coord):
   b = True
   x, y = coord
   xo, yo = world.get_orig ()
   for i in [-1, 0, 1]:
      for j in [-1, 0, 1]:
         b = b and ((not is_in_map (world, (x + i, y + j))) or world.get_state (x - xo + i, y - yo + j) == sim_const.EMPTY)
   return b and is_in_map (world, coord)

# draw a line with bresenham algorithm
def line ((xs, ys), (xe, ye)): # TODO optimiser en passant à e en entier
   line_points = []
   if xs == xe and ys == ye:
      line_points = [(xs, ys)]
   elif abs (xs - xe) > abs (ys - ye):
      if xs > xe:
         xs, xe = xe, xs
         ys, ye = ye, ys
      y = ys
      e = 0.0
      c = (float (ye) - float (ys)) / (float (xe) - float (xs))
      if c > 0:
         sig = 1
      else:
         sig = -1
      c = abs (c)
      for x in range (xs, xe + 1):
         line_points.append ((x, y))
         e = e + c
         if e > 0.5:
            y = y + sig
            e = e - 1.
   elif abs (ys - ye) >= abs (xs - xe):
      if ys > ye:
         xs, xe = xe, xs
         ys, ye = ye, ys
      x = xs
      e = 0.0
      c = (float (xe) - float (xs)) / (float (ye) - float (ys))
      if c > 0:
         sig = 1
      else:
         sig = -1
      c = abs (c)
      for y in range (ys, ye + 1):
         line_points.append ((x, y))
         e = e + c
         if e > 0.5:
            x = x + sig
            e = e - 1.
   return line_points

class Editor (object):
   def __init__ (self, cell_array):
      # internal data
      self.ca = cell_array
      
      # edit options
      self.current_color = sim_const.EMPTY
      self.current_mode = ui_const.TOOL_MOVE
      
      # edit var
      self.highlighted = []
      self.last_coord = None
      self.component_buffer = Component (0, 0)
      self.data = None
   
   # move by drag and drop
   def move (self, dx, dy):
      self.ca.ca_move (dx, dy)
      self.ca.ca_draw ()
      
   # expand the map to include the given point
   def include (self, x, y):
      map_x, map_y = self.ca.ca_map.get_orig ()
      map_w, map_h = self.ca.ca_map.get_size ()
      if (map_w, map_h) == (0, 0):
         self.ca.ca_map.set_orig (x, y)
         self.ca.ca_map.resize (0, 0, 1, 1)
      else:
         self.ca.ca_map.resize (max (0, map_x - x), max (0, map_y - y), max (0, x - map_x - map_w + 1), max (0, y - map_y - map_h + 1))
         
   # autocrop : resize image by eliminate empty rows/cols
   def autocrop (self):
      # horizontal axis
      mw, mh = self.ca.ca_map.get_size ()
      # left
      cl = 0
      while cl < mw:
         y = 0
         while y < mh and self.ca.ca_map.get_state (cl, y) == sim_const.EMPTY:
            y = y + 1
         if y != mh:
            break
         cl = cl + 1
      cr = 0
      if cl == mw:
         # if completely erased
         cl = mw
      else :
         # right
         while cr < mw - cl:
            y = 0
            while y < mh and self.ca.ca_map.get_state (mw - cr - 1, y) == sim_const.EMPTY:
               y = y + 1
            if y != mh:
               break
            cr = cr + 1
      # resize
      self.ca.ca_map.resize (-cl, 0, -cr, 0)
      # vertical axis
      mw, mh = self.ca.ca_map.get_size ()
      # top
      ct = 0
      while ct < mh:
         x = 0
         while x < mw and self.ca.ca_map.get_state (x, ct) == sim_const.EMPTY:
            x = x + 1
         if x != mw:
            break
         ct = ct + 1
      cb = 0
      if ct == mh:
         ct = mh
      else :
         # bottom
         while cb < mh - ct:
            x = 0
            while x < mw and self.ca.ca_map.get_state (x, mh - cb - 1) == sim_const.EMPTY:
               x = x + 1
            if x != mw:
               break
            cb = cb + 1
      # resize
      self.ca.ca_map.resize (0, -ct, 0, -cb)
         
   # edit a cell, assuming its included in the map
   def edit (self, x, y):
      mx, my = self.ca.ca_map.get_orig ()
      self.ca.ca_map.set_state (x - mx, y - my, self.current_color)
         
   # parameter changes due to ui
   def set_current_color (self, color):
      self.current_color = color
      
   def set_current_mode (self, mode):
      self.current_mode = mode
      self.reset_modes ()
   
   def reset_modes (self):
      # clean shared vars
      self.highlighted = []
      self.last_coord = None
      self.data = None
      # reset cursor
      if self.current_mode == ui_const.TOOL_MOVE:
         self.ca.ca_set_cursor (gtk.gdk.HAND2)
      else:
         self.ca.ca_set_cursor (gtk.gdk.TCROSS)
      
   def toggle_edit (self):
      self.current_mode = ui_const.TOOL_MOVE
      self.reset_modes ()

   def get_highlighted (self):
      return self.highlighted
   
   # cell_array events, catch shared events
   def do_event (self, event_type, coord):
      if event_type == ev_const.MOUSE_LEAVE or event_type == ev_const.MOUSE_ENTER:
         if self.current_mode != ui_const.TOOL_PATH:
            self.reset_modes ()
            if event_type == ev_const.MOUSE_LEAVE:
               self.ca.ca_draw ()
      elif self.current_mode == ui_const.TOOL_MOVE:
         self.do_event_move (event_type, coord)
      elif self.current_mode == ui_const.TOOL_PENCIL:
         self.do_event_pencil (event_type, coord)
      elif self.current_mode == ui_const.TOOL_ASTAR:
         self.do_event_astar (event_type, coord)
      elif self.current_mode == ui_const.TOOL_ERASER:
         self.do_event_eraser (event_type, coord)
      elif self.current_mode == ui_const.TOOL_COPY:
         self.do_event_copy (event_type, coord)
      elif self.current_mode == ui_const.TOOL_RESIZE:
         self.do_event_resize (event_type, coord)
      elif self.current_mode == ui_const.TOOL_PASTE:
         self.do_event_paste (event_type, coord)
      elif self.current_mode == ui_const.TOOL_PATH:
         self.do_event_path (event_type, coord)
         
   # drag & drop
   def do_event_move (self, event_type, coord):
      if event_type == ev_const.MOUSE_BUTTON_PRESS:
         # origin
         self.last_coord = coord
         self.ca.ca_set_cursor (gtk.gdk.HAND1)
      elif event_type == ev_const.MOUSE_MOTION:
         # if dynamic actions move then map whenever it's needed
         if ui_config['editor_action_preview_enabled'] and self.last_coord != None and coord != self.last_coord:
            nx, ny = coord
            ox, oy = self.last_coord
            self.move (ox - nx, oy - ny)
      elif event_type == ev_const.MOUSE_BUTTON_RELEASE:
         if self.last_coord != None:
            # move the map if non dynamic, nothing to do if dynamic (already moved)
            if not ui_config['editor_action_preview_enabled']:
               nx, ny = coord
               ox, oy = self.last_coord
               self.move (ox - nx, oy - ny)
         # reset mode variables
         self.reset_modes ()
   
   # edit cells
   def do_event_pencil (self, event_type, coord):
      if event_type == ev_const.MOUSE_BUTTON_PRESS:
         # origin
         self.last_coord = [coord, coord]
         self.highlighted = [coord]
         self.ca.ca_draw ()
      elif (event_type == ev_const.MOUSE_MOTION and ui_config['editor_action_preview_enabled'] and
         # if dynamic draw the future line beetween cursor and origin
         self.last_coord != None and coord != self.last_coord[1]):
         self.highlighted = line (self.last_coord[0], coord)
         self.last_coord[1] = coord
         self.ca.ca_draw ()
      elif event_type == ev_const.MOUSE_BUTTON_RELEASE:
         if self.last_coord != None:
            # draw the line on the map, and resize it if needed
            self.include (*self.last_coord[0])
            self.include (*coord)
            for point in line (self.last_coord[0], coord):
               self.edit (*point)
         self.reset_modes ()
         self.ca.ca_draw ()
            
   # erase cells
   def do_event_eraser (self, event_type, coord):
      if event_type == ev_const.MOUSE_BUTTON_PRESS:
         # origin
         self.last_coord = [coord, coord]
         self.highlighted = [coord]
         self.ca.ca_draw ()
      elif (event_type == ev_const.MOUSE_MOTION and ui_config['editor_action_preview_enabled'] and
         self.last_coord != None and coord != self.last_coord[1]):
         # print a rectangle showing the selection
         xs, ys = self.last_coord[0]
         xe, ye = coord
         self.highlighted = [(xs, ys), (xe, ys), (xs, ye), (xe, ye)]
         for x in range (min (xs, xe) + 1, max (xs, xe)):
            self.highlighted.append ((x, ys))
            self.highlighted.append ((x, ye))
         for y in range (min (ys, ye) + 1, max (ys, ye)):
            self.highlighted.append ((xs, y))
            self.highlighted.append ((xe, y))
         self.last_coord[1] = coord
         self.ca.ca_draw ()
      elif event_type == ev_const.MOUSE_BUTTON_RELEASE:
         if self.last_coord != None:
            # erase the rectangle
            xs, ys = self.last_coord[0]
            xe, ye = coord
            mx, my = self.ca.ca_map.get_orig ()
            mw, mh = self.ca.ca_map.get_size ()
            for x in range (max (min (xs, xe), mx), min (max (xs, xe) + 1, mx + mw)):
               for y in range (max (min (ys, ye), my), min (max (ys, ye) + 1, my + mh)):
                  self.ca.ca_map.set_state (x - mx, y - my, sim_const.EMPTY)
         self.reset_modes ()
         self.ca.ca_draw ()
   
   # A* path (without frequency)
   def do_event_astar (self, event_type, coord):
      if is_valid_a_star (self.ca.ca_map, coord):
         xo, yo = self.ca.ca_map.get_orig ()
         x, y = coord
         try:
            if event_type == ev_const.MOUSE_BUTTON_PRESS:
               self.last_coord = coord
               hl, self.data = dynamic_a_star (Point (x - xo, y - yo), Data (Point (x - xo, y - yo), self.ca.ca_map))
               self.highlighted = map (lambda e:(xo + e.x, yo + e.y), hl)
               self.ca.ca_draw ()
            elif event_type == ev_const.MOUSE_MOTION:
               if self.last_coord != None and coord != self.last_coord:
                  self.last_coord = coord
                  hl, self.data = dynamic_a_star (Point (x - xo, y - yo), self.data)
                  self.highlighted = map (lambda e:(xo + e.x, yo + e.y), hl)
                  self.ca.ca_draw ()
            elif event_type == ev_const.MOUSE_BUTTON_RELEASE:
               if self.last_coord != None:
                  for i, j in self.highlighted:
                     self.ca.ca_map.set_state (i - xo, j - yo, self.current_color)
               self.reset_modes ()
               self.ca.ca_draw ()
         except Exception as text:
            ui_dialog.msg_box.spawn (gtk.MESSAGE_ERROR, 'Unable to link these cells : %s' % text)
            self.reset_modes ()
            self.ca.ca_draw ()
      else:
         ui_dialog.msg_box.spawn (gtk.MESSAGE_ERROR, 'The cursor must stay in the map and must not touch non-empty cells')
         self.reset_modes ()
         self.ca.ca_draw ()
         
   # copy tool
   def do_event_copy (self, event_type, coord):
      if is_in_map (self.ca.ca_map, coord):
         if event_type == ev_const.MOUSE_BUTTON_PRESS:
            # origin
            self.last_coord = [coord, coord]
            self.highlighted = [coord]
            self.ca.ca_draw ()
         elif (event_type == ev_const.MOUSE_MOTION and ui_config['editor_action_preview_enabled'] and
            self.last_coord != None and coord != self.last_coord[1]):
            # print a rectangle showing the selection
            xs, ys = self.last_coord[0]
            xe, ye = coord
            self.highlighted = [(xs, ys), (xe, ys), (xs, ye), (xe, ye)]
            for x in range (min (xs, xe) + 1, max (xs, xe)):
               self.highlighted.append ((x, ys))
               self.highlighted.append ((x, ye))
            for y in range (min (ys, ye) + 1, max (ys, ye)):
               self.highlighted.append ((xs, y))
               self.highlighted.append ((xe, y))
            self.last_coord[1] = coord
            self.ca.ca_draw ()
         elif event_type == ev_const.MOUSE_BUTTON_RELEASE:
            if self.last_coord != None:
               # copy the rectangle
               xs, ys = self.last_coord[0]
               xe, ye = coord
               mx, my = self.ca.ca_map.get_orig ()
               self.component_buffer = self.ca.ca_map.copy_component (Point (xs - mx, ys - my),
               Point (xe - mx + 1, ye - my + 1))
            self.reset_modes ()
            self.ca.ca_draw ()
      else:
         ui_dialog.msg_box.spawn (gtk.MESSAGE_ERROR, 'The cursor must stay in the map')
         self.reset_modes ()
         self.ca.ca_draw ()
         
   # resize tool
   def do_event_resize (self, event_type, coord):
      if event_type == ev_const.MOUSE_BUTTON_PRESS:
         # origin
         self.last_coord = [coord, coord]
         self.highlighted = [coord]
         self.ca.ca_draw ()
      elif (event_type == ev_const.MOUSE_MOTION and ui_config['editor_action_preview_enabled'] and
         self.last_coord != None and coord != self.last_coord[1]):
         # print a rectangle showing the selection
         xs, ys = self.last_coord[0]
         xe, ye = coord
         self.highlighted = [(xs, ys), (xe, ys), (xs, ye), (xe, ye)]
         for x in range (min (xs, xe) + 1, max (xs, xe)):
            self.highlighted.append ((x, ys))
            self.highlighted.append ((x, ye))
         for y in range (min (ys, ye) + 1, max (ys, ye)):
            self.highlighted.append ((xs, y))
            self.highlighted.append ((xe, y))
         self.last_coord[1] = coord
         self.ca.ca_draw ()
      elif event_type == ev_const.MOUSE_BUTTON_RELEASE:
         if self.last_coord != None:
            # copy the rectangle
            xs, ys = self.last_coord[0]
            xe, ye = coord
            l = min (xs, xe)
            t = min (ys, ye)
            r = max (xs, xe)
            b = max (ys, ye)
            mx, my = self.ca.ca_map.get_orig ()
            mw, mh = self.ca.ca_map.get_size ()
            self.ca.ca_map.resize (mx - l, my - t, r - mx - mw + 1, b - my - mh + 1)
         self.reset_modes ()
         self.ca.ca_draw ()

   # paste tool
   def do_event_paste (self, event_type, coord):
      if event_type == ev_const.MOUSE_BUTTON_PRESS:
         # origin
         self.last_coord = [coord, coord]
         self.highlighted = [coord]
         self.ca.ca_draw ()
      elif (event_type == ev_const.MOUSE_MOTION and ui_config['editor_action_preview_enabled'] and
         self.last_coord != None and coord != self.last_coord[1]):
         # print origin if cursor is above it
         if self.last_coord[0] == self.last_coord[1]:
            self.highlighted = [self.last_coord[0]]
         else:
            self.highlighted = []
         self.last_coord[1] = coord
         self.ca.ca_draw ()
      elif event_type == ev_const.MOUSE_BUTTON_RELEASE:
         if self.last_coord != None and self.last_coord[0] == coord:
            # copy the rectangle
            xs, ys = self.last_coord[0]
            mw, mh = self.component_buffer.get_size ()
            self.include (xs, ys)
            self.include (xs + mw - 1, ys + mh - 1)
            mx, my = self.ca.ca_map.get_orig ()
            self.ca.ca_map.put_component (xs - mx, ys - my, self.component_buffer)
         self.reset_modes ()
         self.ca.ca_draw ()
         
   # A* path, with frequency
   def do_event_path (self, event_type, coord):
      if is_valid_a_star (self.ca.ca_map, coord) or (event_type == ev_const.MOUSE_MOTION and
      is_in_map (self.ca.ca_map, coord)):
         try:
            if event_type == ev_const.MOUSE_BUTTON_PRESS:
               self.last_coord = [coord, coord]
               self.highlighted = [coord]
               self.ca.ca_draw ()
            elif event_type == ev_const.MOUSE_MOTION:
               if self.last_coord != None and coord != self.last_coord[1] and ui_config['editor_action_preview_enabled']:
                  self.last_coord[1] = coord
                  self.highlighted = self.last_coord
                  self.ca.ca_draw ()
            elif event_type == ev_const.MOUSE_BUTTON_RELEASE:
               if self.last_coord != None:
                  mx, my = self.ca.ca_map.get_orig ()
                  xs, ys = self.last_coord[0]
                  xe, ye = coord
                  answer, freq = ui_dialog.frequency_dialog (None)
                  if answer == gtk.RESPONSE_ACCEPT:
                     self.ca.ca_map.add_connection (Connection (freq, xs - mx, ys - my))
                     self.ca.ca_map.add_connection (Connection (freq, xe - mx, ye - my))
                     self.ca.ca_map.link_connections_low (0, 1)
               self.reset_modes ()
               self.ca.ca_draw ()
         except Exception as text:
            ui_dialog.msg_box.spawn (gtk.MESSAGE_ERROR, 'Unable to link these cells : %s' % text)
            self.reset_modes ()
            self.ca.ca_draw ()
      else:
         ui_dialog.msg_box.spawn (gtk.MESSAGE_ERROR, 'The cursor must stay in the map and must not touch non-empty cells')
         self.reset_modes ()
         self.ca.ca_draw ()
   