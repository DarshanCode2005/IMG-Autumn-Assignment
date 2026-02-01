import 'package:flutter/material.dart';
import '../api/websocket_service.dart';

class WebSocketProvider extends ChangeNotifier {
  final WebSocketService _service = WebSocketService();

  Stream<Map<String, dynamic>> get stream => _service.stream;

  void connect(int userId) {
    _service.connect(userId);
  }

  void disconnect() {
    _service.disconnect();
  }

  @override
  void dispose() {
    _service.dispose();
    super.dispose();
  }
}
