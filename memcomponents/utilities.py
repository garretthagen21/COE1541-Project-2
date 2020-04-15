# Get the address and offset of the address string in decimal
def parseAddressString(rawAddress):
    hexData = rawAddress.split('x')[1]
    addrPortion = hexData[0:-3]
    offsetPortion = rawAddress[-3:]
    return addrPortion,offsetPortion

# Convenience dict lookup
def dictLookup(dict,key):
    try:
        return dict[key]
    except KeyError:
        return None