from sardana import State
from sardana.pool.controller import CounterTimerController
from sardana.pool.controller import Type, Description, DefaultValue, Access, DataAccess, Memorized, Memorize
from tango import DeviceProxy
import time


class PiLCCounterTimerController(CounterTimerController):
    """PiLCTriggerGateController

    Use the DESY PiLC as Trigger/Gate controller

    """
    ctrl_properties = {'tangoFQDN': {Type: str,
                                     Description: 'The FQDN of the CAEN FastPS Tango DS',
                                     DefaultValue: 'domain/family/member'},
                       }
    
    ctrl_attributes = {
        "FreeRunning": {
                Type: bool,
                Description: "set PiLC gate to free-running mode",
                Access : DataAccess.ReadWrite,
                Memorized: Memorize,
            },
    }

    MaxDevice = 1

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        CounterTimerController.__init__(self, inst, props, *args, **kwargs)
        print('PiLC Initialization on {:s} ...'.format(self.tangoFQDN))
        self._log.info('PiLC Initialization ...')
        self.proxy = DeviceProxy(self.tangoFQDN)
        print('SUCCESS')
        self.__start_time = None

    def AddDevice(self, axis):
        self._log.debug('AddDevice(%d): entering...' % axis)

    def ReadOne(self, axis):
        return time.time()-self.__start_time

    def StateOne(self, axis):
        """Get the dummy trigger/gate state"""
        try:
            self._log.debug('StateOne(%d): entering...' % axis)
            sta = State.On
            status = "Stopped"
            
            if self.proxy.ReadFPGA(0x06) > 0:
                sta = State.Moving
                status = "Moving"
            self._log.debug('StateOne(%d): returning (%s, %s)' %
                            (axis, sta, status))
        except Exception as e:
            print(e)
        return sta, status

    def PrepareOne(self, axis, value, repetitions, latency_time, nb_starts):
        self._log.debug('PrepareOne(%d): entering...' % axis)
        # stop gate first
        self.proxy.WriteFPGA([0x01,0])
        # define gate width in micorseconds
        self.proxy.WriteFPGA([0x03, int(value*1e6)])

    def LoadOne(self, axis, value, repetitions, latency_time):
        pass

    def StartOne(self, axis, value=None):
        self._log.debug('StartOne(%d): entering...' % axis)
        if self.__freerunning:
            self.proxy.WriteFPGA([0x01,2])
        else:  # triggered
            self.proxy.WriteFPGA([0x01,1])

        self.__start_time = time.time()

    def StopOne(self, axis):
        self._log.debug('AbortOne(%d): entering...' % axis)
        self.proxy.WriteFPGA([0x01,0])

    def AbortOne(self, axis):
        pass

    def getFreeRunning(self):
        return self.__freerunning

    def setFreeRunning(self, value):
        self.__freerunning = bool(value)
