#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys

from colorlog import ColoredFormatter

logger = logging.getLogger('test')
console_fms = "%(log_color)s[%(asctime)s.%(msecs)03d %(levelname)s] %(message)s"
# datefmt = "%Y-%m-%d %H:%M:%S"
date_fmt = "%H:%M:%S"

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter(console_fms,
                                              datefmt=date_fmt,
                                              reset=True,
                                              log_colors={
                                                  'DEBUG': 'cyan',
                                                  'INFO': 'white',
                                                  'WARNING': 'yellow',
                                                  'ERROR': 'red',
                                                  'CRITICAL': 'red'
                                              },
                                              secondary_log_colors={},
                                              style='%'))
logger.addHandler(console_handler)
