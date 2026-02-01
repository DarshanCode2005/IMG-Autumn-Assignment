import 'package:flutter/material.dart';
import '../api/notification_service.dart';

class NotificationProvider extends ChangeNotifier {
  final NotificationService _notificationService = NotificationService();
  final List<Map<String, dynamic>> _notifications = [];
  
  // Callback to trigger reloads in other providers
  Function(Map<String, dynamic>)? onProcessedCallback;

  List<Map<String, dynamic>> get notifications => _notifications;
  bool get isConnected => _notificationService.isConnected;

  void connect(int userId) {
    _notificationService.connect(userId, (data) {
      _notifications.add(data);
      
      // If a photo was processed, we might want to trigger a callback
      if (data['type'] == 'photo_processed' && data['status'] == 'completed') {
        onProcessedCallback?.call(data);
      }
      
      notifyListeners();
    });
  }

  void setOnProcessedCallback(Function(Map<String, dynamic>) callback) {
    onProcessedCallback = callback;
  }

  void disconnect() {
    _notificationService.disconnect();
    notifyListeners();
  }

  @override
  void dispose() {
    _notificationService.disconnect();
    super.dispose();
  }
}
