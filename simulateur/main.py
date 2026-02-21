#!/usr/bin/python -O
# -*- coding: utf-8 -*-

import ui_main_window
import config

config.config_init ()

window = ui_main_window.Main_window ()
window.main ()
