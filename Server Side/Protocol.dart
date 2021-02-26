import 'dart:typed_data';

const int MOVEMENT = 0;
const int ALL_CONNECTED = 10;

List<int> fromBytes(Uint8List bytes) {
  return [
    bytes[0],
    bytes
        .sublist(1, 3)
        .buffer
        .asByteData(0)
        .getInt16(0),
    bytes
        .sublist(3, 5)
        .buffer
        .asByteData(0)
        .getInt16(0),
    bytes
        .sublist(5, 7)
        .buffer
        .asByteData(0)
        .getInt16(0),
    bytes[7]
  ];
}

List<int> fromData(int id, int x, int y, int angle, int type) {
  return [
    ...id.toBytes(1),
    ...x.toBytes(2),
    ...y.toBytes(2),
    ...angle.toBytes(2),
    ...type.toBytes(1)
  ];
}

extension ByteConverting on int {
  Uint8List toBytes(int length) {
    var data = Uint8List(4)
      ..buffer.asByteData().setInt32(0, this, Endian.big);
    return data.sublist(data.length - length, data.length);
  }
}
