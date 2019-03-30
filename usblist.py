#!/usr/bin/env python2.7
import usb
import re
testpattern="[P|G]117[a-zA-Z]\w{5}$"

print "Test pattern is {}".format(testpattern)
def chusb():
    dev = usb.core.find(idVendor=1123, idProduct=65535)
    dev.reset()
    sn = usb.util.get_string(dev, dev.iSerialNumber)
    # print sn
    valid = (re.match(testpattern, sn))
    if valid:
        return {"sn": sn, "valid": True}
    else:
        return {"sn": sn, "valid": False}

while True:
    try:
        result = chusb()
        if result['valid']:
            raw_input('{} is OK. Connect next BBU and press enter...'.format(result['sn']))
        else:
            print "Error! SN: {} is invalid. Please check! Interrupted.".format(result['sn'])
            break
    except(ValueError, AttributeError, NotImplementedError):
        raw_input('BBU SN not found')
