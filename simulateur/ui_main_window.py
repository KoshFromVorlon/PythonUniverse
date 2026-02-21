# -*- coding: utf-8 -*-

####################################
# main window interface with pygtk #
####################################

# includes
import pygtk
pygtk.require('2.0')
import gtk
import glib

from config import *
import ui_cell_array
import ui_dialog
import ui_widget
import composants

# utils
def gtk_widget_show_list (widgets):
   for w in widgets:
      w.show ()
      
def gtk_widget_hide_list (widgets):
   for w in widgets:
      w.hide ()

def gtk_widget_enable_list (widgets, state):
   for w in widgets:
      w.set_sensitive (state)

# main window class
class Main_window (object):
   #### signals ####
   # quit signal
   def ev_window_delete_event (self, widget, event, data = None):
      return False
   
   # menu quit signal
   def ev_menu_quit (self, item, data = None):
      self.window.destroy ()
   
   # end of gtk loop
   def ev_window_destroy (self, widget, data = None):
      gtk.main_quit ()
      
   # menu save event
   def ev_menu_save (self, item, data):
      # run a filechooser dialog
      answer, filename = ui_dialog.save_dialog (self.window)
            
      # display information to user
      if answer == gtk.RESPONSE_ACCEPT:
         if self.ca_cell_array.ca_save (filename, data):
            ui_dialog.msg_box.spawn (gtk.MESSAGE_INFO, 'Map successfully saved in %s' % filename)
         else:
            ui_dialog.msg_box.spawn (gtk.MESSAGE_ERROR, 'Error while saving map in %s' % filename)

   
   # menu load event
   def ev_menu_load (self, item, data):      
      # run a filechooser dialog
      answer, filename, cell_size = ui_dialog.load_dialog (self.window)
         
      if answer == gtk.RESPONSE_ACCEPT:
         # load and display information to user
         if self.ca_cell_array.ca_load (filename, cell_size, data):
            ui_dialog.msg_box.spawn (gtk.MESSAGE_INFO, 'Map successfully loaded from %s' % filename)
         else:
            ui_dialog.msg_box.spawn (gtk.MESSAGE_ERROR, 'Error while loading map from %s' % filename)

   # menu grid checkbox
   def ev_menu_checkbox_grid (self, item, data = None):
      ui_config['cell_array_grid_enabled'] = not ui_config['cell_array_grid_enabled']
      self.ca_cell_array.ca_draw ()
      
   # menu map checkbox
   def ev_menu_checkbox_map (self, item, data = None):
      ui_config['cell_array_map_show'] = not ui_config['cell_array_map_show']
      self.ca_cell_array.ca_draw ()
      
   # menu grid checkbox
   def ev_menu_checkbox_selection (self, item, data = None):
      ui_config['editor_action_preview_enabled'] = not ui_config['editor_action_preview_enabled']
     
   # toggle mode button
   def ev_tb_toggle_clicked (self, widget, data = None):
      # swap menu bar
      self.v_mode = 1 - self.v_mode
      if self.v_mode == ui_const.MODE_RUN:
         gtk_widget_hide_list (self.v_edit_bar_widgets)
         gtk_widget_show_list (self.v_run_bar_widgets)
         self.tb_toggle.u_set_label ('Run _mode')
         self.ca_cell_array.ca_editor.autocrop ()
         self.ca_cell_array.ca_map = self.ca_cell_array.ca_map.turn_to_map ()
      else:
         gtk_widget_show_list (self.v_edit_bar_widgets)
         gtk_widget_hide_list (self.v_run_bar_widgets)
         self.tb_toggle.u_set_label ('Edit _mode')
         self.ca_cell_array.ca_map = composants.create_from_map (self.ca_cell_array.ca_map)
      # menu
      gtk_widget_enable_list ([self.mbf_save, self.mbf_load, self.mbf_save_buf, self.mbf_load_buf],
      self.v_mode == ui_const.MODE_EDIT)
      # reset tool, and redraw
      self.tbeb_tool_move.set_active (True)
      self.ca_cell_array.ca_editor.toggle_edit ()
      self.ca_cell_array.ca_draw ()
   
   # iterate n times
   def ev_tbrb_iter_n_time_clicked (self, widget, data = None):
      bound = self.tbrb_iter_num_w.get_value_as_int ()
      # if only one iteration, doesn't freeze the ui
      if bound > 1:
         percent = 0
         # disable ui and reset progress bar
         self.w_vbox.set_sensitive (False)
         self.tb_progress.u_set (0)
         for i in range(bound):
            self.ca_cell_array.ca_iter ()
            # update progress bar
            new_percent = (100 * i) / bound
            if (new_percent > percent):
               self.tb_progress.u_set (percent)
               percent = new_percent
            # let gtk running
            gtk.main_iteration (False)
         # restart ui, reset progress bar
         self.w_vbox.set_sensitive (True)
         self.tb_progress.u_clear ()

      else:
         self.ca_cell_array.ca_iter ()
      self.ca_cell_array.ca_draw ()
      
   # iterate, with drawing
   def ev_tbrb_toggle_play (self, widget, data = None):
      self.v_is_running = not self.v_is_running
      if self.v_is_running:
         # change icon
         widget.set_stock_id (gtk.STOCK_MEDIA_PAUSE)
         # launch iterations
         self.v_running_time = 0
         self.v_running_id = glib.timeout_add (int (1000 / self.tbrb_play_speed_w.get_value ()), self.iteration_idle,
            int (1000 / self.tbrb_play_speed_w.get_value ()), int (1000 / self.tbrb_draw_speed_w.get_value ()))
      else:
         # change icon
         widget.set_stock_id (gtk.STOCK_MEDIA_PLAY)
         # stop iterations
         glib.source_remove (self.v_running_id)
         # redraw to show the real state of the map
         self.ca_cell_array.ca_draw ()
      gtk_widget_enable_list (self.v_running_widgets, not self.v_is_running)
   
   # center
   def ev_tb_center (self, button, data = None):
      self.ca_cell_array.ca_center ()
      
   # crop
   def ev_tb_crop (self, button, data = None):
      self.ca_cell_array.ca_editor.autocrop ()
      
   # change current color
   def ev_eb_color_change (self, button, color):
      if button.get_active ():
         self.ca_cell_array.ca_editor.set_current_color (color)
         
   # change current mode puppet
   def ev_eb_mode_change (self, button, mode):
      if button.get_active ():
         self.ca_cell_array.ca_editor.set_current_mode (mode)
      
   #### init window ####
   def __init__ (self):
      # variables
      self.v_mode = ui_const.MODE_EDIT
      self.v_is_running = False
      self.v_running_id = None
      self.v_running_time = 0
      self.v_edit_bar_widgets = []
      self.v_run_bar_widgets = []
      self.v_running_widgets = []
      
      # create the main window, and main vbox
      self.window = gtk.Window ()
      self.window.set_title ('Simulateur wireworld')
      self.window.set_default_size (ui_config['main_window_default_width'], ui_config['main_window_default_height'])
      self.w_vbox = gtk.VBox ()
      self.window.add (self.w_vbox)
      self.window.connect ('delete_event', self.ev_window_delete_event)
      self.window.connect ('destroy', self.ev_window_destroy)
      
      self.window.get_settings ().set_long_property ('gtk-toolbar-icon-size', gtk.ICON_SIZE_SMALL_TOOLBAR, '')
      
      # menu bar
      self.m_bar = gtk.MenuBar ()
      self.w_vbox.pack_start (self.m_bar, False, False, 0)
      
      # file
      self.mb_file = gtk.MenuItem ('_File')
      self.m_bar.append (self.mb_file)
      
      self.mbf_menu = gtk.Menu ()
      self.mb_file.set_submenu (self.mbf_menu)
      
      self.mbf_save = gtk.MenuItem ('_Save...')
      self.mbf_menu.append (self.mbf_save)
      self.mbf_save.connect ('activate', self.ev_menu_save, True)
      
      self.mbf_load = gtk.MenuItem ('_Open...')
      self.mbf_menu.append (self.mbf_load)
      self.mbf_load.connect ('activate', self.ev_menu_load, True)
      
      self.mbf_separator1 = gtk.SeparatorMenuItem ()
      self.mbf_menu.append (self.mbf_separator1)
      
      self.mbf_save_buf = gtk.MenuItem ('_Export buffer...')
      self.mbf_menu.append (self.mbf_save_buf)
      self.mbf_save_buf.connect ('activate', self.ev_menu_save, False)
      
      self.mbf_load_buf = gtk.MenuItem ('_Import buffer...')
      self.mbf_menu.append (self.mbf_load_buf)
      self.mbf_load_buf.connect ('activate', self.ev_menu_load, False)
      
      self.mbf_separator2 = gtk.SeparatorMenuItem ()
      self.mbf_menu.append (self.mbf_separator2)
      
      self.mbf_quit = gtk.MenuItem ('_Quit')
      self.mbf_menu.append (self.mbf_quit)
      self.mbf_quit.connect ('activate', self.ev_menu_quit)
      
      # settings
      self.mb_settings = gtk.MenuItem ('_Settings')
      self.m_bar.append (self.mb_settings)
      
      self.mbs_menu = gtk.Menu ()
      self.mb_settings.set_submenu (self.mbs_menu)
      
      self.mbs_grid_enable = gtk.CheckMenuItem ('_Grid')
      self.mbs_grid_enable.set_active (ui_config['cell_array_grid_enabled'])
      self.mbs_menu.append (self.mbs_grid_enable)
      self.mbs_grid_enable.connect ('toggled', self.ev_menu_checkbox_grid)
      
      self.mbs_selection_enable = gtk.CheckMenuItem ('_Action preview')
      self.mbs_selection_enable.set_active (ui_config['editor_action_preview_enabled'])
      self.mbs_menu.append (self.mbs_selection_enable)
      self.mbs_selection_enable.connect ('toggled', self.ev_menu_checkbox_selection)
      
      self.mbs_map_enable = gtk.CheckMenuItem ('_Show internal map')
      self.mbs_map_enable.set_active (ui_config['cell_array_map_show'])
      self.mbs_menu.append (self.mbs_map_enable)
      self.mbs_map_enable.connect ('toggled', self.ev_menu_checkbox_map)

      # button bar
      self.t_bar = gtk.Toolbar ()
      self.t_bar.set_style (gtk.TOOLBAR_ICONS)
      self.w_vbox.pack_start (self.t_bar, False, False, 0)
      
      self.tb_toggle = ui_widget.BoundToolButtonText (self.t_bar)
      self.tb_toggle.set_tooltip_text ('Toggle beetween edit and run mode')
      self.v_running_widgets.append (self.tb_toggle)
      self.tb_toggle.connect ('clicked', self.ev_tb_toggle_clicked)
      
      self.tb_separator1 = ui_widget.BoundSeparatorToolItem (self.t_bar)
      
      # edit bar
      self.tbeb_color_empty = ui_widget.BoundRadioToolButton (None, 'cell_array_color_empty', self.t_bar)
      self.tbeb_color_empty.set_tooltip_text ('Empty state')
      self.v_edit_bar_widgets.append (self.tbeb_color_empty)
      self.tbeb_color_empty.connect ('toggled', self.ev_eb_color_change, sim_const.EMPTY)
      
      self.tbeb_color_wire = ui_widget.BoundRadioToolButton (self.tbeb_color_empty, 'cell_array_color_wire', self.t_bar)
      self.tbeb_color_wire.set_tooltip_text ('Wire state')
      self.v_edit_bar_widgets.append (self.tbeb_color_wire)
      self.tbeb_color_wire.connect ('toggled', self.ev_eb_color_change, sim_const.WIRE)
      
      self.tbeb_color_head = ui_widget.BoundRadioToolButton (self.tbeb_color_empty, 'cell_array_color_head', self.t_bar)
      self.tbeb_color_head.set_tooltip_text ('Electron head state')
      self.v_edit_bar_widgets.append (self.tbeb_color_head)
      self.tbeb_color_head.connect ('toggled', self.ev_eb_color_change, sim_const.HEAD)
      
      self.tbeb_color_tail = ui_widget.BoundRadioToolButton (self.tbeb_color_empty, 'cell_array_color_tail', self.t_bar)
      self.tbeb_color_tail.set_tooltip_text ('Electron tail state')
      self.v_edit_bar_widgets.append (self.tbeb_color_tail)
      self.tbeb_color_tail.connect ('toggled', self.ev_eb_color_change, sim_const.TAIL)
      
      self.tbeb_separator = ui_widget.BoundSeparatorToolItem (self.t_bar)
      self.v_edit_bar_widgets.append (self.tbeb_separator)
      
      self.tbeb_tool_move = ui_widget.BoundRadioToolButton (None, 'cell_array_tool_move', self.t_bar)
      self.tbeb_tool_move.set_tooltip_text ('Move tool')
      self.v_edit_bar_widgets.append (self.tbeb_tool_move)
      self.tbeb_tool_move.connect ('toggled', self.ev_eb_mode_change, ui_const.TOOL_MOVE)
      
      self.tbeb_tool_pencil = ui_widget.BoundRadioToolButton (self.tbeb_tool_move, 'cell_array_tool_pencil', self.t_bar)
      self.tbeb_tool_pencil.set_tooltip_text ('Pencil & line tool')
      self.v_edit_bar_widgets.append (self.tbeb_tool_pencil)
      self.tbeb_tool_pencil.connect ('toggled', self.ev_eb_mode_change, ui_const.TOOL_PENCIL)
      
      self.tbeb_tool_astar = ui_widget.BoundRadioToolButton (self.tbeb_tool_move, 'cell_array_tool_astar', self.t_bar)
      self.tbeb_tool_astar.set_tooltip_text ('A* path tool (without frequency)')
      self.v_edit_bar_widgets.append (self.tbeb_tool_astar)
      self.tbeb_tool_astar.connect ('toggled', self.ev_eb_mode_change, ui_const.TOOL_ASTAR)
      
      self.tbeb_tool_eraser = ui_widget.BoundRadioToolButton (self.tbeb_tool_move, 'cell_array_tool_eraser', self.t_bar)
      self.tbeb_tool_eraser.set_tooltip_text ('Eraser tool')
      self.v_edit_bar_widgets.append (self.tbeb_tool_eraser)
      self.tbeb_tool_eraser.connect ('toggled', self.ev_eb_mode_change, ui_const.TOOL_ERASER)
      
      self.tbeb_tool_copy = ui_widget.BoundRadioToolButton (self.tbeb_tool_move, 'cell_array_tool_copy', self.t_bar)
      self.tbeb_tool_copy.set_tooltip_text ('Copy selection to buffer')
      self.v_edit_bar_widgets.append (self.tbeb_tool_copy)
      self.tbeb_tool_copy.connect ('toggled', self.ev_eb_mode_change, ui_const.TOOL_COPY)
      
      self.tbeb_tool_paste = ui_widget.BoundRadioToolButton (self.tbeb_tool_move, 'cell_array_tool_paste', self.t_bar)
      self.tbeb_tool_paste.set_tooltip_text ('Paste buffer content')
      self.v_edit_bar_widgets.append (self.tbeb_tool_paste)
      self.tbeb_tool_paste.connect ('toggled', self.ev_eb_mode_change, ui_const.TOOL_PASTE)
      
      self.tbeb_tool_resize = ui_widget.BoundRadioToolButton (self.tbeb_tool_move, 'cell_array_tool_resize', self.t_bar)
      self.tbeb_tool_resize.set_tooltip_text ('Resize internal map to the selection rectangle')
      self.v_edit_bar_widgets.append (self.tbeb_tool_resize)
      self.tbeb_tool_resize.connect ('toggled', self.ev_eb_mode_change, ui_const.TOOL_RESIZE)
      
      self.tbeb_tool_path = ui_widget.BoundRadioToolButton (self.tbeb_tool_move, 'cell_array_tool_path', self.t_bar)
      self.tbeb_tool_path.set_tooltip_text ('Link two cells with the same phase (for a given frequency)')
      self.v_edit_bar_widgets.append (self.tbeb_tool_path)
      self.tbeb_tool_path.connect ('toggled', self.ev_eb_mode_change, ui_const.TOOL_PATH)
      
      self.tbeb_separator2 = ui_widget.BoundSeparatorToolItem (self.t_bar)
      self.v_edit_bar_widgets.append (self.tbeb_separator2)
      
      self.tbeb_center = ui_widget.BoundToolButtonStock ('cell_array_action_center', self.t_bar)
      self.tbeb_center.set_tooltip_text ('Center view on the map')
      self.v_edit_bar_widgets.append (self.tbeb_center)
      self.tbeb_center.connect ('clicked', self.ev_tb_center)
      
      self.tbeb_crop = ui_widget.BoundToolButtonStock ('cell_array_action_crop', self.t_bar)
      self.tbeb_crop.set_tooltip_text ('Eliminate empty parts of the map')
      self.v_edit_bar_widgets.append (self.tbeb_crop)
      self.tbeb_crop.connect ('clicked', self.ev_tb_crop)
      
      # run bar
      self.tbrb_toggle_play = ui_widget.BoundToolButtonStock (gtk.STOCK_MEDIA_PLAY, self.t_bar)
      self.tbrb_toggle_play.set_tooltip_text ('Toggle beetween play / pause')
      self.v_run_bar_widgets.append (self.tbrb_toggle_play)
      self.tbrb_toggle_play.connect ('clicked', self.ev_tbrb_toggle_play)
      
      self.tbrb_play_speed_w = ui_widget.NumericSpinButton (1, 300)
      self.tbrb_play_speed_w.set_tooltip_text ('Maximum iterations per second')
      self.tbrb_play_speed = ui_widget.BoundToolItem (self.tbrb_play_speed_w, self.t_bar)
      self.v_run_bar_widgets.append (self.tbrb_play_speed)
      self.v_running_widgets.append (self.tbrb_play_speed)
      
      self.tbrb_draw_speed_w = ui_widget.NumericSpinButton (1, 30)
      self.tbrb_draw_speed_w.set_tooltip_text ('Maximum redrawings per second')
      self.tbrb_draw_speed = ui_widget.BoundToolItem (self.tbrb_draw_speed_w, self.t_bar)
      self.v_run_bar_widgets.append (self.tbrb_draw_speed)
      self.v_running_widgets.append (self.tbrb_draw_speed)
      
      self.tbrb_separator = ui_widget.BoundSeparatorToolItem (self.t_bar)
      self.v_run_bar_widgets.append (self.tbrb_separator)
      
      self.tbrb_iter_n_time = ui_widget.BoundToolButtonStock (gtk.STOCK_MEDIA_NEXT, self.t_bar)
      self.tbrb_iter_n_time.set_tooltip_text ('Start an iteration sequence')
      self.v_run_bar_widgets.append (self.tbrb_iter_n_time)
      self.v_running_widgets.append (self.tbrb_iter_n_time)
      self.tbrb_iter_n_time.connect ('clicked', self.ev_tbrb_iter_n_time_clicked)
      
      self.tbrb_iter_num_w = ui_widget.NumericSpinButton (1, 10000)
      self.tbrb_iter_num_w.set_tooltip_text ('Number of iterations wanted')
      self.tbrb_iter_num = ui_widget.BoundToolItem (self.tbrb_iter_num_w, self.t_bar)
      self.v_run_bar_widgets.append (self.tbrb_iter_num)
      self.v_running_widgets.append (self.tbrb_iter_num)
      
      ## shared progress bar
      self.tb_separator2 = ui_widget.BoundSeparatorToolItem (self.t_bar)
      
      self.tb_progress = ui_widget.BoundProgressBarToolItem (self.t_bar)

      self.v_running_widgets.append (self.tb_progress)
      
      # cell array
      self.ca_table = gtk.Table (2, 3)
      self.ca_table.set_border_width (4)
      self.w_vbox.pack_start (self.ca_table, True, True, 0)
      
      self.ca_cell_array = ui_cell_array.Cell_array ()
      self.ca_table.attach (self.ca_cell_array, 0, 1, 0, 1, gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL, 2, 2)
      
      self.ca_vscroll = gtk.VScrollbar ()
      self.ca_vscroll.set_range (-1, 1)
      self.ca_vscroll.set_value (0)
      self.ca_vscroll.set_update_policy (gtk.UPDATE_DISCONTINUOUS)
      self.ca_table.attach (self.ca_vscroll, 1, 2, 0, 1, gtk.FILL, gtk.FILL, 2, 2)
      self.ca_vscroll.connect ('value-changed', self.ca_cell_array.ca_ev_scroll, True)
      
      self.ca_hscroll = gtk.HScrollbar ()
      self.ca_hscroll.set_range (-1, 1)
      self.ca_hscroll.set_value (0)
      self.ca_hscroll.set_update_policy (gtk.UPDATE_DISCONTINUOUS)
      self.ca_table.attach (self.ca_hscroll, 0, 1, 1, 2, gtk.FILL, gtk.FILL, 2, 2)
      self.ca_hscroll.connect ('value-changed', self.ca_cell_array.ca_ev_scroll, False)
      
      self.ca_scale = gtk.VScale ()
      self.ca_scale.set_range (1, ui_config['cell_array_max_zoom'] * ui_config['cell_array_max_zoom'])
      self.ca_scale.set_value (ui_config['cell_array_default_zoom'] * ui_config['cell_array_default_zoom'])
      self.ca_scale.set_update_policy (gtk.UPDATE_DISCONTINUOUS)
      self.ca_scale.set_draw_value (False)
      self.ca_scale.set_inverted (True)
      self.ca_scale.set_tooltip_text ('Set zoom')
      self.ca_table.attach (self.ca_scale, 2, 3, 0, 2, gtk.FILL, gtk.FILL, 2, 2)
      self.ca_scale.connect ('value-changed', self.ca_cell_array.ca_ev_zoom)

      # show all widgets
      self.window.show_all ()
      
      ui_dialog.msg_box.base_window = self.window
      
      # bar settings
      gtk_widget_hide_list (self.v_run_bar_widgets)
      self.tb_toggle.u_set_label ('Edit _mode')

      self.tbeb_tool_move.set_active (True)
      self.tbeb_color_empty.set_active (True)
      self.ca_cell_array.ca_set_cursor (gtk.gdk.HAND2)

   # main loop
   def main (self):
      # main loop
      gtk.main ()
      
   # iteration idle function
   def iteration_idle (self, iter_interval, draw_interval):
      # iterate
      self.ca_cell_array.ca_iter ()
      # compute the time elapsed since the last draw
      self.v_running_time = self.v_running_time + iter_interval
      # draw if time greater than max refresh interval
      if (self.v_running_time >= draw_interval):
         self.v_running_time = 0
         self.ca_cell_array.ca_draw ()
      return True
