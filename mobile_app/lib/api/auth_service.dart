import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/constants.dart';
import 'api_client.dart';
import '../models/user.dart';

class AuthService {
  final ApiClient _apiClient;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  AuthService(this._apiClient);

  Future<void> login(String email, String password) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/token/',
        data: {
          'username': email,
          'password': password,
        },
      );
      
      final token = response.data['access'];
      await _storage.write(key: AppConstants.tokenKey, value: token);
    } catch (e) {
      throw e;
    }
  }

  Future<User> getUserMe() async {
    try {
      final response = await _apiClient.dio.get('/users/me/');
      return User.fromJson(response.data);
    } catch (e) {
      throw e;
    }
  }

  Future<User> register(String email, String password, String role) async {
    try {
      final response = await _apiClient.dio.post(
        '/users/',
        data: {
          'username': email, // Django uses username
          'email': email,
          'password': password,
          'role': role,
        },
      );
      return User.fromJson(response.data);
    } catch (e) {
      throw e;
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: AppConstants.tokenKey);
  }

  Future<bool> isAuthenticated() async {
    final token = await _storage.read(key: AppConstants.tokenKey);
    return token != null;
  }
}
