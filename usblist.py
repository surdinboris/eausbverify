#!/usr/bin/env python2.7
import usb
import re
from datetime import *
import logging

now = datetime.now()
logging.basicConfig(filename='easnverify_{}.log'.format(now.strftime("%d%m%Y%H%M")), filemode='w', format='{} : %(message)s'.format(now.strftime("%d %b %Y %H:%M")), level=logging.DEBUG)
logger = logging.getLogger("newlog")

eatondates = {"E": 2014, "F":2015, "G": 2016, "H": 2017, "I": 2018, "J": 2019,
            "K": 2020, "L": 2021, "M": 2022, "N": 2023, "O": 2024, "P": 2025,
            "Q": 2026, "R": 2027, "S": 2028, "T": 2029}

def confirm(prompt=None, resp=False):
    if prompt is None:
        prompt = 'Confirm'
    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

validatesn=confirm(prompt="Do you want to barcode validation for serial numbers during test? y/n")

logger.info('Starting test. {} barcode validation.'.format("With" if validatesn else "Without"))
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
    # dev.reset()
    return result

while True:
    try:
        result = chusb()
        # print result
        if result["valid"] and not result["twoYearOld"]:
            logger.info('BBU SN: {} is OK. BBU production time {} months.'.format(result["sn"],result["age"]))
            if validatesn:
                scannedsn = raw_input("Please scan device's barcode:")
                if scannedsn != str(result["sn"]):
                    logger.info("Scanned barcode SN: {} not equal device's memory SN: {}.".format(scannedsn,str(result["sn"])))
                    print "Error. Scanned barcode SN: {} not equal device's memory SN: {}. Please check".format(scannedsn,result["sn"])
                    break
            raw_input("BBU SN: {} is OK. BBU production time {} months. Connect next BBU and press enter...".format(result["sn"],result["age"]))

        elif result['valid'] and result['twoYearOld']:
            logger.info('BBU SN: {} MFG date expired. BBU production time {} months.'.format(result["sn"], result["age"]))
            print "Error! Manufacturing date  for SN: {} is too old ({} months). Please check!".format(result["sn"], result["age"])
            break

        elif result["sn"] and not result["valid"]:
            logger.info('BBU SN: {} invalid.'.format(result["sn"]))
            print "BBU SN: {} is not valid. Please check!".format(result["sn"])
            break

        else:
            print "Unhandled error, please check", result
            logger.info('Error'.format(result))
            break
    # except(ValueError, AttributeError, NotImplementedError):
    except(NotImplementedError, ValueError), e:
        logger.info('Error'.format(e))
        raw_input("BBU SN not found")
