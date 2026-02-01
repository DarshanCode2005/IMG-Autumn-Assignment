import 'dart:io';
import 'package:flutter/foundation.dart';

class AppConstants {
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000/api/v1';
    if (Platform.isAndroid) return 'http://10.0.2.2:8000/api/v1';
    return 'http://localhost:8000/api/v1';
  }

  static String get wsUrl {
    if (kIsWeb) return 'ws://localhost:8000/ws/notifications';
    if (Platform.isAndroid) return 'ws://10.0.2.2:8000/ws/notifications';
    return 'ws://localhost:8000/ws/notifications';
  }
  
  // Storage Keys
  static const String tokenKey = 'auth_token';
}
