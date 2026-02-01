import 'package:dio/dio.dart';
import 'api_client.dart';
import '../models/event.dart';

class EventService {
  final ApiClient _apiClient;

  EventService(this._apiClient);

  Future<List<Event>> getEvents() async {
    try {
      final response = await _apiClient.dio.get('/events/');
      final List<dynamic> data = response.data;
      return data.map((json) => Event.fromJson(json)).toList();
    } catch (e) {
      throw e;
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
