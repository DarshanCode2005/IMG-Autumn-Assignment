import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../utils/constants.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final StreamController<Map<String, dynamic>> _controller = StreamController.broadcast();
  bool _isConnected = false;

  Stream<Map<String, dynamic>> get stream => _controller.stream;
  bool get isConnected => _isConnected;

  void connect(int userId) {
    if (_isConnected) return;

    try {
      final url = '${AppConstants.wsUrl}?user_id=$userId';
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _isConnected = true;
      
      _channel!.stream.listen(
        (message) {
          try {
            final data = json.decode(message);
            _controller.add(data);
          } catch (e) {
            debugPrint('Error parsing WebSocket message: $e');
          }
        },
        onDone: () {
          _isConnected = false;
          _reconnect(userId);
        },
        onError: (error) {
          _isConnected = false;
          debugPrint('WebSocket error: $error');
          _reconnect(userId);
        },
      );
    } catch (e) {
      _isConnected = false;
      _reconnect(userId);
    }
  }

  void _reconnect(int userId) {
    Future.delayed(const Duration(seconds: 5), () {
      if (!_isConnected) {
        connect(userId);
      }
    });
  }

  void disconnect() {
    _channel?.sink.close();
    _isConnected = false;
  }

  void dispose() {
    disconnect();
    _controller.close();
  }
}
