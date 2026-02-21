# -*- coding: utf-8 -*-

import pygtk
pygtk.require ('2.0')
import gtk

class NumericSpinButton (gtk.SpinButton):
   def __init__ (self, a, b):
      gtk.SpinButton.__init__ (self)
      self.set_increments (1, 10)
      self.set_range (a, b)
      self.set_numeric (True)
      self.set_snap_to_ticks (True)

class BoundToolItem (gtk.ToolItem):
   def __init__ (self, child, toolbar):
      gtk.ToolItem.__init__ (self)
      self.set_homogeneous (False)
      self.add (child)
      toolbar.insert (self, -1)
      
class BoundToolButtonStock (gtk.ToolButton):
   def __init__ (self, stock, toolbar):
      gtk.ToolButton.__init__ (self, stock)
      self.set_homogeneous (False)
      toolbar.insert (self, -1)
      
class BoundToolButtonText (gtk.ToolButton):
   def __init__ (self, toolbar):
      gtk.ToolButton.__init__ (self, None, '')
      self.set_homogeneous (False)
      self.set_icon_widget (gtk.Label (''))
      self.get_icon_widget ().set_use_underline (True)
      toolbar.insert (self, -1)
   
   def u_set_label (self, text):
      self.get_icon_widget ().set_label (text)
      
class BoundRadioToolButton (gtk.RadioToolButton):
   def __init__ (self, group, stock, toolbar):
      gtk.RadioToolButton.__init__ (self, group, stock)
      self.set_homogeneous (False)
      toolbar.insert (self, -1)
      
class BoundSeparatorToolItem (gtk.SeparatorToolItem):
   def __init__ (self, toolbar):
      gtk.SeparatorToolItem.__init__ (self)
      self.set_homogeneous (False)
      toolbar.insert (self, -1)
      
class BoundProgressBarToolItem (BoundToolItem):
   def __init__ (self, toolbar):
      BoundToolItem.__init__ (self, gtk.ProgressBar (), toolbar)
      self.set_expand (True)
      
   def u_clear (self):
      self.get_child ().set_fraction (0)
      self.get_child ().set_text ('')
      
   def u_set (self, percent):
      self.get_child ().set_fraction (percent / 100.)
      self.get_child ().set_text (str (percent) + ' %')