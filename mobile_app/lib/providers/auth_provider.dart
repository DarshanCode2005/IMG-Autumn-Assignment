import 'package:flutter/material.dart';
import '../api/auth_service.dart';
import '../api/api_client.dart';
import '../models/user.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService;
  bool _isLoading = false;
  bool _isAuthenticated = false;
  User? _user;

  AuthProvider() : _authService = AuthService(ApiClient()) {
    checkAuthStatus();
  }

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  User? get user => _user;
  bool get isAdminOrCoordinator => 
    _user?.role.toLowerCase() == 'admin' || _user?.role.toLowerCase() == 'coordinator';

  Future<void> checkAuthStatus() async {
    _isAuthenticated = await _authService.isAuthenticated();
    if (_isAuthenticated) {
      try {
        _user = await _authService.getUserMe();
      } catch (e) {
        _isAuthenticated = false;
        await _authService.logout();
      }
    } else {
      _user = null;
    }
    notifyListeners();
  }

  Future<void> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      await _authService.login(email, password);
      _user = await _authService.getUserMe();
      _isAuthenticated = true;
    } catch (e) {
      _isAuthenticated = false;
      _user = null;
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> register(String email, String password, String role) async {
    _isLoading = true;
    notifyListeners();
    try {
      await _authService.register(email, password, role);
    } catch (e) {
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateProfile(Map<String, dynamic> profileData) async {
    _isLoading = true;
    notifyListeners();
    try {
      _user = await _authService.updateProfile(profileData);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> uploadProfilePic(dynamic file) async {
    _isLoading = true;
    notifyListeners();
    try {
      _user = await _authService.uploadProfilePic(file);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _isAuthenticated = false;
    _user = null;
    notifyListeners();
  }
}
