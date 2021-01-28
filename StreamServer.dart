import 'dart:io';
import 'Protocol.dart';
import 'dart:typed_data';

//! GLOBAL VARIABLES
List<Client> clients = [];
List<List<int>> spawns = [
  [100, 200],
  [500, 200],
];

//! FUNCTIONS
void main() {
  var ip = InternetAddress.anyIPv4;
  var port = 255;
  print('Server openned on ${ip.address}:$port');
  ServerSocket.bind(ip, port).then((ServerSocket server) {
    server.listen(registerClient);
  });  
}

void registerClient(Socket client) {
  print('Connection from ${client.remoteAddress.address}:${client.remotePort}');
  clients.add(Client(client));
  var rival_id = clients.length - 1;
  var enemy_id = (1 - rival_id).abs();
  var rival_data =
      fromData(rival_id, spawns[rival_id][0], spawns[rival_id][1], 0, 0);
  print(rival_data);
  var enemy_data =
      fromData(enemy_id, spawns[enemy_id][0], spawns[enemy_id][1], 0, 0);
  print(enemy_data);
  client.add(rival_data);
  client.add(enemy_data);
}

//! CLASSES
class Client {
  Socket socket;
  String address;
  int port;
  int id, x, y, angle, type;

  Client(Socket user_socket) {
    this.socket = user_socket;
    this.address = this.socket.remoteAddress.address;
    this.port = this.socket.remotePort;

    this.socket.listen(messageHandler,
        onError: this.errorHandler, onDone: this.finishHandler);
  }

  void finishHandler() {
    print('Disconnect from ${this.address}:${this.port}');
    removeClient();
  }

  void errorHandler(error) {
    print('${this.address}:${this.port} Error: $error');
    this.socket.close();
  }

  void removeClient() {
    var result = clients.remove(this);
    if (result) {
      print('Client removed successully');
    } else {
      print('Client cant be removed');
    }
  }

  void messageHandler(Uint8List bytes) {
    this.distributeMessage(this, bytes);
  }

  void distributeMessage(Client client, Uint8List data) {
    for (Client c in clients) {
       c.socket.add(data);
    }
  }
}