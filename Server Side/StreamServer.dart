import 'dart:io';
import 'Protocol.dart';
import 'dart:typed_data';

//! GLOBAL VARIABLES
List<Client> clients = [];
List<List<int>> spawns = [
  [100, 200],
  [500, 200],
];
int MAX_USERS = 2;
List<int> IDS = [0, 1];

//! FUNCTIONS
void main() async {
  var sys_ip = await NetworkInterface.list();
  var ip = sys_ip.first.addresses.first.address.toString();
  var port = 255;
  print('Server openned on ${ip}:$port');
  ServerSocket.bind(ip, port).then((ServerSocket server) {
    server.listen(registerClient, onError: (error) {
      print(error.message);
      server.close();
    });
  });
}

void registerClient(Socket client) {
  var client_data = '${client.remoteAddress.address}:${client.remotePort}';
  print('$client_data >>> Connect');
  var rival_id = IDS.first;
  IDS.remove(rival_id);
  var enemy_id = (MAX_USERS - rival_id - 1).abs();
  var rival_data =
      fromData(rival_id, spawns[rival_id][0], spawns[rival_id][1], 0, 0);
  print('$client_data >>> Take id $rival_id');
  var enemy_data =
      fromData(enemy_id, spawns[enemy_id][0], spawns[enemy_id][1], 0, 0);
  client.add(rival_data);
  client.add(enemy_data);
  clients.add(Client(client, rival_id));
}

//! CLASSES
class Client {
  Socket socket;
  String address;
  int port;
  int id;

  Client(Socket user_socket, id) {
    this.id = id;
    this.socket = user_socket;
    this.address = this.socket.remoteAddress.address;
    this.port = this.socket.remotePort;

    this.socket.listen(messageHandler,
        onError: this.errorHandler, onDone: this.finishHandler);
  }

  void finishHandler() {
    print('${this.address}:${this.port} >>> Disconnect');
    removeClient();
  }

  void errorHandler(error) {
    print('${this.address}:${this.port} >>> Error: $error');
    this.socket.close();
    removeClient();
  }

  void removeClient() {
    this.socket.close();
    var client_data =
        '${this.socket.remoteAddress.address}:${this.socket.remotePort}';
    var isSuccessfully = clients.remove(this);
    IDS.add(this.id);
    print('$client_data >>> Return id ${this.id}');
    if (isSuccessfully) {
      print('$client_data >>> Removed successully');
    } else {
      print('$client_data >>> Can not be removed');
    }
  }

  void messageHandler(Uint8List bytes) {
    this.distributeMessage(this, bytes);
  }

  void distributeMessage(Client client, Uint8List data) {
    for (Client c in clients) {
      if (c != client) {
        try {
          c.socket.add(data);
        } catch (SocketException) {
          this.removeClient();
        }
      }
    }
  }
}
