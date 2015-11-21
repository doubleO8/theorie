#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

if 'USED_LOGLEVEL' not in dir():
    USED_LOGLEVEL = logging.INFO


class AutomatLogger(object):
    __instance = None

    class __implementation:
        def __init__(self, loglevel=None):
            if not loglevel:
                global USED_LOGLEVEL
                loglevel = USED_LOGLEVEL
            self._initLogging(loglevel)

        def getId(self):
            return id(self)

        def _initLogging(self, loglevel):
            self.log = logging.getLogger("automatenlogger")
            if len(self.log.handlers) == 0:
                lhandler = logging.StreamHandler()
                lformatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
                lhandler.setFormatter(lformatter)
                self.log.addHandler(lhandler)
                self.log.setLevel(loglevel)
                self.log.debug(loglevel)

    def __init__(self, loglevel=None):
        if AutomatLogger.__instance is None:
            AutomatLogger.__instance = AutomatLogger.__implementation(loglevel)
        self.__dict__['_AutomatLogger__instance'] = AutomatLogger.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
