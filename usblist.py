#!/usr/bin/env python2.7
import usb
import re
from datetime import *

now = datetime.now()
eatondates = {"E": 2014, "F":2015, "G": 2016, "H": 2017, "I": 2018, "J": 2019,
            "K": 2020, "L": 2021, "M": 2022, "N": 2023, "O": 2024, "P": 2025,
            "Q": 2026, "R": 2027, "S": 2028, "T": 2029}

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

testpattern="[P|G]117([E-T])(\d{2})(\w{3})$"
# print "Test pattern is {}".format(testpattern)

def chusb():
    dev = usb.core.find(idVendor=1123, idProduct=65535)
    result = {"sn": None, "valid": None, "twoYearOld": None,  "age": None}
    if dev:
        result["sn"] = usb.util.get_string(dev, dev.iSerialNumber)
        # print sn
        result["valid"] = (re.match(testpattern, result["sn"]))
        if result["valid"]:
            bbuyear = str(eatondates[result["valid"].group(1)])
            bbuweek = str(result["valid"].group(2))
            bbumfgdt=datetime.strptime(bbuyear+" "+bbuweek + " 0", "%Y %W %w")
            result["age"] = diff_month(now, bbumfgdt)
            result["twoYearOld"] = diff_month(now, bbumfgdt) > 24
    dev.reset()
    return result

while True:
    try:
        result = chusb()
        # print result
        if result["valid"] and not result["twoYearOld"]:
            raw_input("BBU SN: {} is OK. BBU production time {} months. Connect next BBU and press enter...".format(result["sn"],result["age"]))

        elif result['valid'] and result['twoYearOld']:
            print "Error! Manufacturing date  for SN: {} is too old ({} months). Please check!".format(result["sn"], result["age"])
            break

        elif result["sn"] and not result["valid"]:
            print "BBU SN: {} is not valid. Please check!".format(result["sn"])
            break

        else:
            print "Unhandled error, please check", result
            break
    # except(ValueError, AttributeError, NotImplementedError):
    except(NotImplementedError, ValueError):
        raw_input("BBU SN not found")
