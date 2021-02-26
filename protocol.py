PACKET_SIZE = 8


class PacketType:
    MOVEMENT = 0
    DEFAULT = 1
    EXPLOSIVE = 2
    ALL_CONNECTED = 10
    DEATH = 11


def from_bytes(packet: bytes):
    """
    PACKET STRUCTURE
[ who (id of player) ] [ x coordinate ] [ y coordinate ] [ angle ] [ type of message ]
|______ 1 byte ______| |__ 2  bytes __| |__ 2  bytes __| |2 bytes| |____ 1  byte ____|
    id:
        unique numbers given from server to user on connecting
    x, y, angle:
        coordinates of player model/ summing bullet / using perk
    type of message:
        can be 1 of these:
            0 - movement ( [who] will be moved to [where] )
            1 - shoot ( bullet will be summoned [where] and moved in [angle] )
            2+ - perks ( see specs )
    """
    if len(packet) != PACKET_SIZE:
        raise ValueError(f'Length of packet must be {PACKET_SIZE}. Get: {packet} where len = {len(packet)}')
    data = packet[0], packet[1:3], packet[3:5], packet[5:7], packet[7]
    _id = data[0]
    x = int.from_bytes(data[1], 'big', signed=True)
    y = int.from_bytes(data[2], 'big', signed=True)
    angle = int.from_bytes(data[3], 'big', signed=True)
    _type = data[4]
    return _id, x, y, angle, _type


def from_data(_id, x, y, angle, _type):
    """
    PACKET STRUCTURE
    [ who (id of player) ] [ x coordinate ] [ y coordinate ] [ angle ] [ type of message ]
    |______ 1 byte ______| |__ 2  bytes __| |__ 2  bytes __| |2 bytes| |____ 1  byte ____|
    id:
        unique numbers given from server to user on connecting
    x, y, angle:
        coordinates of player model/ summing bullet / using perk
    type of message:
        can be 1 of these:
            0 - movement ( [who] will be moved to [where] )
            1 - shoot ( bullet will be summoned [where] and moved in [angle] )
            2+ - perks ( see specs )
    """
    _id = _id.to_bytes(1, 'big', signed=True)
    _x = x.to_bytes(2, 'big', signed=True)
    _y = y.to_bytes(2, 'big', signed=True)
    _angle = angle.to_bytes(2, 'big', signed=True)
    _type = _type.to_bytes(1, 'big', signed=True)
    return _id + _x + _y + _angle + _type
