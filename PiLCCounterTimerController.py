from sardana import State
from sardana.pool.controller import CounterTimerController
from sardana.pool.controller import Type, Description, DefaultValue, Access, DataAccess, Memorized, Memorize
from tango import DeviceProxy
import time
import numpy as np


class PiLCCounterTimerController(CounterTimerController):
    """PiLCTriggerGateController

    Use the DESY PiLC as Trigger/Gate controller

    """
    ctrl_properties = {'tangoFQDN': {Type: str,
                                     Description: 'The FQDN of the PiLCTriggerGateGenerator Tango DS',
                                     DefaultValue: 'domain/family/member'},
                       }
    
    ctrl_attributes = {
        "TriggerMode": {
                Type: int,
                Description: "mode of PiLC gate: 0 - free running 1 - triggered 2 - triggered & ccd",
                Access : DataAccess.ReadWrite,
                Memorized: Memorize,
            },
    }

    MaxDevice = 1

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        CounterTimerController.__init__(self, inst, props, *args, **kwargs)
        self._log.info('PiLCTriggerGateGenerator Initialization on {:s} ...'.format(self.tangoFQDN))
        self.proxy = DeviceProxy(self.tangoFQDN)
        self._log.info('SUCCESS')
        self.__start_time = None

    def AddDevice(self, axis):
        self._log.debug('AddDevice(%d): entering...' % axis)

    def ReadOne(self, axis):
        self._log.info('ReadOne(%d): entering...' % axis)
        return time.time()-self.__start_time

    def StateOne(self, axis):
        """Get the state"""        
        self._log.debug('StateOne(%d): entering...' % axis)

        state = self.proxy.command_inout("State")
        status = self.proxy.command_inout("Status")

        return state, status

    def PrepareOne(self, axis, value, repetitions, latency_time, nb_starts):
        self._log.info('PrepareOne(%d): entering...' % axis)

        self.proxy.exposure = value*1000 # from s to ms
        self.proxy.prepare()
        self.proxy.mode = self.__trigger_mode

    def LoadOne(self, axis, value, repetitions, latency_time):
        self._log.info('LoadOne(%d): entering...' % axis)
        self.proxy.stop()

    def PreStartOne(self, axis, value):
        self._log.info('PreStartOne(%d): entering...' % axis)
        return True

    def StartOne(self, axis, value):
        self._log.info('StartOne(%d): entering...' % axis)

        self.proxy.start()

        self.__start_time = time.time()

    def StopOne(self, axis):
        self._log.debug('StopOne(%d): entering...' % axis)
        self.proxy.stop()

    def AbortOne(self, axis):
        self._log.debug('AbortOne(%d): entering...' % axis)        
        self.proxy.stop()

    def getTriggerMode(self):
        return self.__trigger_mode

    def setTriggerMode(self, value):
        if value in [0, 1, 2]:
            self.__trigger_mode = int(value)
        else:
            self._log.warning('trigger mode must be 0, 1, or 2!')
