import 'package:flutter/material.dart';
import '../api/event_service.dart';
import '../api/api_client.dart';
import '../models/event.dart';

class EventProvider extends ChangeNotifier {
  final EventService _eventService;
  List<Event> _events = [];
  bool _isLoading = false;
  String? _error;

  EventProvider() : _eventService = EventService(ApiClient());

  List<Event> get events => _events;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Event? getEventById(int id) {
    try {
      return _events.firstWhere((e) => e.id == id);
    } catch (_) {
      return null;
    }
  }

  Future<void> loadEvents() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      _events = await _eventService.getEvents();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> addEvent(String name, String description, DateTime date, String location) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final eventData = {
        'name': name,
        'description': description,
        'date': date.toIso8601String().split('T')[0],
        'location': location,
      };
      await _eventService.createEvent(eventData);
      await loadEvents(); // Refresh list
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateEvent(int id, String name, String description, DateTime date, String location) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final eventData = {
        'name': name.trim(),
        'description': description.trim(),
        'date': date.toIso8601String().split('T')[0],
        'location': location.trim(),
      };
      await _eventService.updateEvent(id, eventData);
      await loadEvents(); // Refresh list
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deleteEvent(int id) async {
    _isLoading = true;
    notifyListeners();
    try {
      await _eventService.deleteEvent(id);
      _events.removeWhere((e) => e.id == id);
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
