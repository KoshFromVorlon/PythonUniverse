# -*- coding: utf-8 -*-

import pygtk
pygtk.require ('2.0')
import gtk

import ui_widget

class Message_box ():
   base_window = None
   def spawn (self, icon, message, parent = None):
      if parent == None:
         parent = self.base_window
      dialog = gtk.MessageDialog (parent, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
      icon, gtk.BUTTONS_OK, message)
      dialog.run ()
      dialog.destroy ()
      
msg_box = Message_box ()
   
def save_dialog (parent):
   # create file chooser
   dialog = gtk.FileChooserDialog ('Save map as PNG picture...', parent,
   gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
   gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
   dialog.set_do_overwrite_confirmation (True)
   
   # run
   answer = dialog.run ()
   
   # get filename
   filename = dialog.get_filename ()
   if answer == gtk.RESPONSE_ACCEPT and (len (filename) < 4 or filename[-4:] != '.png'):
      filename = filename + '.png'
      
   # destroy dialog and return data
   dialog.destroy ()
   return (answer, filename)
      
def load_dialog (parent):
   # create dialog
   dialog = gtk.FileChooserDialog ('Load map from a PNG picture...', parent,
   gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
   gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
   dialog.action_area.pack_start (gtk.Label ('Cell size in pixels :'))   
   spinbutton = ui_widget.NumericSpinButton (1, 200)
   dialog.action_area.pack_start (spinbutton)
   dialog.action_area.show_all ()
   
   # run
   answer = dialog.run ()
   
   # gather data
   filename = dialog.get_filename ()
   cell_size = spinbutton.get_value_as_int ()
   
   # destroy dialog and retrn choice
   dialog.destroy ()
   return (answer, filename, cell_size)
   
def frequency_dialog (parent):
   # create dialog
   dialog = gtk.Dialog ('Link frequency...', parent,
   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
   gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
   hbox = gtk.HBox ()
   hbox.pack_start (gtk.Label ('Link frequency in iterations/signal :'))   
   spinbutton = ui_widget.NumericSpinButton (1, 200)
   hbox.pack_end (spinbutton)
   dialog.vbox.pack_start (hbox)
   dialog.vbox.show_all ()
   
   # run
   answer = dialog.run ()
   
   # gather data
   freq = spinbutton.get_value_as_int ()
   
   # destroy dialog and retrn choice
   dialog.destroy ()
   return (answer, freq)