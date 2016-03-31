#!/usr/bin/python
# Copyright (C) 2011 by Mark Visser <mjmvisser@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os, sys
from optparse import OptionParser
from adl3 import *
import collections
import json
from gpu import GPU


class ADLError(Exception):
    pass



def initialize():
    # check for unset DISPLAY, assume :0
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
    
    # the '1' means only retrieve info for active adapters
    if ADL_Main_Control_Create(ADL_Main_Memory_Alloc, 1) != ADL_OK:
        raise ADLError("Couldn't initialize ADL interface.")

def shutdown():
    if ADL_Main_Control_Destroy() != ADL_OK:
        raise ADLError("Couldn't destroy ADL interface global pointers.")

def get_adapter_info():
    adapter_info = []
    num_adapters = c_int(-1)
    if ADL_Adapter_NumberOfAdapters_Get(byref(num_adapters)) != ADL_OK:
        raise ADLError("ADL_Adapter_NumberOfAdapters_Get failed.")

    # allocate an array of AdapterInfo, see ctypes docs for more info
    AdapterInfoArray = (AdapterInfo * num_adapters.value)() 
    
    # AdapterInfo_Get grabs info for ALL adapters in the system
    if ADL_Adapter_AdapterInfo_Get(cast(AdapterInfoArray, LPAdapterInfo), sizeof(AdapterInfoArray)) != ADL_OK:
        raise ADLError("ADL_Adapter_AdapterInfo_Get failed.")

    deviceAdapter = collections.namedtuple('DeviceAdapter', ['AdapterIndex', 'AdapterID', 'BusNumber', 'UDID'])
    devices = []
    
    for adapter in AdapterInfoArray:
        index = adapter.iAdapterIndex
        busNum = adapter.iBusNumber
        udid = adapter.strUDID
        
        adapterID = c_int(-1)
        #status = c_int(-1)
        
        if ADL_Adapter_ID_Get(index, byref(adapterID)) != ADL_OK:
            raise ADLError("ADL_Adapter_Active_Get failed.")
        
        found = False
        for device in devices:
            if (device.AdapterID.value == adapterID.value):
                found = True
                break
        
        # save it in our list if it's the first controller of the adapter
        if (found == False):
            devices.append(deviceAdapter(index,adapterID,busNum,udid))
    
    for device in devices:
        adapter_info.append(AdapterInfoArray[device.AdapterIndex])
    
    return adapter_info

            
def show_status(adapter_list=None):
    adapter_info = get_adapter_info()
    output = []
    
    for index, info in enumerate(adapter_info):
        if adapter_list is None or index in adapter_list:
            gpu = GPU();

           
            ###ADD TO GPU OBJECT
            gpu.index = index
            gpu.name = info.strAdapterName
            gpu.display = info.strDisplayName

            activity = ADLPMActivity()
            activity.iSize = sizeof(activity)
            
            if ADL_Overdrive5_CurrentActivity_Get(info.iAdapterIndex, byref(activity)) != ADL_OK:
                raise ADLError("ADL_Overdrive5_CurrentActivity_Get failed.")
            
            ###ADD TO GPU OBJECT
            gpu.engine = (activity.iEngineClock/100.0)
            gpu.memory = (activity.iMemoryClock/100.0)
            gpu.volts = (activity.iVddc/1000.0)
            gpu.performance = (activity.iCurrentPerformanceLevel)
            gpu.utilization = (activity.iActivityPercent)

                
            fan_speed = {}
            for speed_type in (ADL_DL_FANCTRL_SPEED_TYPE_PERCENT, ADL_DL_FANCTRL_SPEED_TYPE_RPM):    
                fan_speed_value = ADLFanSpeedValue()
                fan_speed_value.iSize = sizeof(fan_speed_value)
                fan_speed_value.iSpeedType = speed_type
        
                if ADL_Overdrive5_FanSpeed_Get(info.iAdapterIndex, 0, byref(fan_speed_value)) != ADL_OK:
                    fan_speed[speed_type] = None
                    continue
            
                fan_speed[speed_type] = fan_speed_value.iFanSpeed
                user_defined = fan_speed_value.iFlags & ADL_DL_FANCTRL_FLAG_USER_DEFINED_SPEED
        
            if bool(fan_speed[ADL_DL_FANCTRL_SPEED_TYPE_PERCENT]) and bool(fan_speed[ADL_DL_FANCTRL_SPEED_TYPE_RPM]):
                ###ADD TO GPU OBJECT
                gpu.fan = fan_speed[ADL_DL_FANCTRL_SPEED_TYPE_PERCENT]


            elif bool(fan_speed[ADL_DL_FANCTRL_SPEED_TYPE_PERCENT]):
                ###ADD TO GPU OBJECT
                gpu.fan = fan_speed[ADL_DL_FANCTRL_SPEED_TYPE_PERCENT]


            elif bool(fan_speed[ADL_DL_FANCTRL_SPEED_TYPE_RPM]) is True:
                ###ADD TO GPU OBJECT
                gpu.fan = fan_speed[ADL_DL_FANCTRL_SPEED_TYPE_RPM]

            else:
                print "    unable to get fan speed"
                
            temperature = ADLTemperature()
            temperature.iSize = sizeof(temperature)
                
            if ADL_Overdrive5_Temperature_Get(info.iAdapterIndex, 0, byref(temperature)) != ADL_OK:
                raise ADLError("ADL_Overdrive5_Temperature_Get failed.")
           
            ###ADD TO GPU OBJECT
            gpu.temp = temperature.iTemperature/1000.0

            # Powertune level
            powertune_level_value = c_int()
            dummy = c_int()
            
            if ADL_Overdrive5_PowerControl_Get(info.iAdapterIndex, byref(powertune_level_value), byref(dummy)) != ADL_OK:
                raise ADLError("ADL_Overdrive5_PowerControl_Get failed.")

          
            ###ADD TO GPU OBJECT
            gpu.power = powertune_level_value.value
            gpu.setObject();
            if gpu is not None:
                output.append(gpu)

    return output


  
            


def i2c_get_core_voltage(adapter_list=None):
   adapter_info = get_adapter_info()
   
   for adapter_index, info in enumerate(adapter_info):
       if adapter_list is None or adapter_index in adapter_list:
           i2c_data = ADLI2C()
           i2c_data.iSize = sizeof(i2c_data)
           i2c_data.iLine = ADL_DL_I2C_LINE_OD_CONTROL
           i2c_data.iAddress = 0x70 << 1
           i2c_data.iOffset = 0x15 + 2
           i2c_data.iAction = ADL_DL_I2C_ACTIONREAD
           i2c_data.iSpeed = 10
           i2c_data.iDataSize = 1
           i2c_data.pcData = c_char_p("\0")
           
           if ADL_Display_WriteAndReadI2C(info.iAdapterIndex, byref(i2c_data)) != ADL_OK:
               raise ADLError("ADL_DisplayWriteAndReadI2C failed.")
           
           print "Voltage: %g" % (0.450 + 0.0125 * (i2c_data.pcData[0] & 0x7f))
       




    
# try:
#   initialize()
#   adapter_list = None
#   show_status(adapter_list=adapter_list)
#   result = 0
    
# except ADLError, err:
#   result = 1
#   print err
        
# finally:        
#   shutdown()
        
# sys.exit(result)