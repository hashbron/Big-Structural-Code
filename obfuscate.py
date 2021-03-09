import string

# returns "encrypted" EID from vanid. does not include "EID" prefix
def van_obfuscate(vanid):
    alphabet = string.ascii_uppercase

    return (hex(vanid)[2:][::-1] + alphabet[(vanid % 17)]).upper()

# returns "unencrypted" vanid from EID. accepts strings with or without EID prefix
def van_unobfuscate(eid):
    eid = eid.upper()
    if("EID" in eid):
        eid = eid.replace("EID", "", 1)

    hex_part = eid[:-1]
    first_hex = hex_part[::-1]
    dec = int(first_hex, 16)
    return dec
