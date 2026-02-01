import 'package:dio/dio.dart';
import 'api_client.dart';
import '../models/event.dart';

class EventService {
  final ApiClient _apiClient;

  EventService(this._apiClient);

  Future<List<Event>> getEvents() async {
    try {
      final response = await _apiClient.dio.get('/events/');
      
      // DRF pagination returns {count, next, previous, results}
      if (response.data is Map && response.data.containsKey('results')) {
        final List<dynamic> data = response.data['results'];
        return data.map((json) => Event.fromJson(json)).toList();
      }
      
      // Fallback if pagination is disabled
      final List<dynamic> data = response.data;
      return data.map((json) => Event.fromJson(json)).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<Event> getEvent(int id) async {
    try {
      final response = await _apiClient.dio.get('/events/$id');
      return Event.fromJson(response.data);
    } catch (e) {
      throw e;
    }
  }

  Future<Event> createEvent(Map<String, dynamic> eventData) async {
    try {
      final response = await _apiClient.dio.post('/events/', data: eventData);
      return Event.fromJson(response.data);
    } catch (e) {
      throw e;
    }
  }

  Future<Event> updateEvent(int id, Map<String, dynamic> eventData) async {
    try {
      final response = await _apiClient.dio.put('/events/$id', data: eventData);
      return Event.fromJson(response.data);
    } catch (e) {
      throw e;
    }
  }

  Future<void> deleteEvent(int id) async {
    try {
      await _apiClient.dio.delete('/events/$id');
    } catch (e) {
      throw e;
    }
  }
}
