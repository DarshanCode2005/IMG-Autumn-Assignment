import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../utils/constants.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final StreamController<Map<String, dynamic>> _controller = StreamController.broadcast();
  bool _isConnected = false;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 3;
  Timer? _reconnectTimer;

  Stream<Map<String, dynamic>> get stream => _controller.stream;
  bool get isConnected => _isConnected;

  void connect(int userId) {
    if (_isConnected) return;

    try {
      final url = '${AppConstants.wsUrl}?user_id=$userId';
      debugPrint('WebSocket: Attempting to connect to $url');
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _isConnected = true;
      _reconnectAttempts = 0;
      
      _channel!.stream.listen(
        (message) {
          try {
            final data = json.decode(message);
            _controller.add(data);
          } catch (e) {
            debugPrint('WebSocket: Error parsing message: $e');
          }
        },
        onDone: () {
          _isConnected = false;
          debugPrint('WebSocket: Connection closed');
          _scheduleReconnect(userId);
        },
        onError: (error) {
          _isConnected = false;
          debugPrint('WebSocket: Connection error: $error');
          _scheduleReconnect(userId);
        },
      );
    } catch (e) {
      _isConnected = false;
      debugPrint('WebSocket: Failed to connect: $e');
      _scheduleReconnect(userId);
    }
  }

  void _scheduleReconnect(int userId) {
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      debugPrint('WebSocket: Max reconnection attempts reached. Giving up.');
      return;
    }
    
    _reconnectTimer?.cancel();
    final delay = Duration(seconds: 5 * (_reconnectAttempts + 1)); // Exponential backoff
    debugPrint('WebSocket: Reconnecting in ${delay.inSeconds}s (attempt ${_reconnectAttempts + 1}/$_maxReconnectAttempts)');
    
    _reconnectTimer = Timer(delay, () {
      _reconnectAttempts++;
      if (!_isConnected) {
        connect(userId);
      }
    });
  }

  void disconnect() {
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _isConnected = false;
    _reconnectAttempts = _maxReconnectAttempts; // Prevent auto-reconnect
  }

  void dispose() {
    disconnect();
    _controller.close();
  }
}
