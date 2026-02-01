import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../utils/constants.dart';

class NotificationService {
  WebSocketChannel? _channel;
  bool _isConnected = false;

  bool get isConnected => _isConnected;

  void connect(int userId, Function(Map<String, dynamic>) onMessage) {
    if (_isConnected) return;

    final url = '${AppConstants.wsUrl}?user_id=$userId';
    debugPrint('NotificationService: Connecting to $url');
    
    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _isConnected = true;

      _channel!.stream.listen(
        (message) {
          debugPrint('NotificationService: Received message: $message');
          final data = jsonDecode(message);
          onMessage(data);
        },
        onDone: () {
          debugPrint('NotificationService: Connection closed');
          _isConnected = false;
        },
        onError: (error) {
          debugPrint('NotificationService: ERROR: $error');
          _isConnected = false;
        },
      );
    } catch (e) {
      debugPrint('NotificationService: Connection failed: $e');
      _isConnected = false;
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _isConnected = false;
  }
}
