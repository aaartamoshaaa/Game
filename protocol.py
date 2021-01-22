PACKET_SIZE = 8


class Packet:
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

    def __init__(self, packet: bytes):
        if len(packet) != PACKET_SIZE:
            raise ValueError(f'Length of packet must be {PACKET_SIZE}')
        data = packet[0], packet[1:3], packet[3:5], packet[5:7], packet[7]
        self.__id = data[0]
        self.__x = int.from_bytes(data[1], 'big', signed=True)
        self.__y = int.from_bytes(data[2], 'big', signed=True)
        self.__angle = int.from_bytes(data[3], 'big', signed=True)
        self.__type = data[4]

    @property
    def data(self):
        return self.__id, self.__x, self.__y, self.__angle, self.__type


p = Packet(b'\x01\x00d\x00\x96\x00\xb4\x01')
print(p.data)