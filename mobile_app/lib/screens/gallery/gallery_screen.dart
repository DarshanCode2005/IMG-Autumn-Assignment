import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../providers/photo_provider.dart';
import '../../widgets/photo_grid_item.dart';
import '../../providers/event_provider.dart';
import '../../providers/websocket_provider.dart';
import '../../providers/auth_provider.dart';

class GalleryScreen extends StatefulWidget {
  final int eventId;

  const GalleryScreen({super.key, required this.eventId});

  @override
  State<GalleryScreen> createState() => _GalleryScreenState();
}

class _GalleryScreenState extends State<GalleryScreen> {
  StreamSubscription? _wsSubscription;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final photoProvider = context.read<PhotoProvider>();
      photoProvider.loadPhotos(widget.eventId);
      
      // Connect to WebSocket and listen for updates
      final wsProvider = context.read<WebSocketProvider>();
      wsProvider.connect(1); // Default to user 1 for now
      _wsSubscription = wsProvider.stream.listen((data) {
        photoProvider.handleMessage(data);
      });
    });
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  void _showDeleteDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Event'),
        content: const Text('Are you sure you want to delete this event? This will also delete all photos in this event.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(ctx);
              try {
                await context.read<EventProvider>().deleteEvent(widget.eventId);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Event deleted')),
                  );
                  context.go('/');
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e')),
                  );
                }
              }
            },
            child: const Text('Delete', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final event = context.watch<EventProvider>().getEventById(widget.eventId);
    final photoProvider = context.watch<PhotoProvider>();
    final isAdminOrCoordinator = context.watch<AuthProvider>().isAdminOrCoordinator;

    return Scaffold(
      appBar: AppBar(
        title: Text(event?.name ?? 'Event Gallery'),
        actions: [
          if (isAdminOrCoordinator)
            PopupMenuButton<String>(
              onSelected: (value) {
                if (value == 'edit') {
                  context.push('/create-event', extra: event);
                } else if (value == 'delete') {
                  _showDeleteDialog(context);
                }
              },
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'edit',
                  child: Row(
                    children: [
                      Icon(Icons.edit),
                      SizedBox(width: 8),
                      Text('Edit Event'),
                    ],
                  ),
                ),
                const PopupMenuItem(
                  value: 'delete',
                  child: Row(
                    children: [
                      Icon(Icons.delete, color: Colors.red),
                      SizedBox(width: 8),
                      Text('Delete Event', style: TextStyle(color: Colors.red)),
                    ],
                  ),
                ),
              ],
            ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search by tags...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          photoProvider.loadPhotos(widget.eventId);
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
                contentPadding: const EdgeInsets.symmetric(vertical: 0),
                filled: true,
                fillColor: Colors.white,
              ),
              onChanged: (value) {
                setState(() {}); // Rebuild to show/hide clear button
              },
              onSubmitted: (value) {
                photoProvider.loadPhotos(widget.eventId, tags: value);
              },
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          if (event != null)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.calendar_today, size: 18),
                      const SizedBox(width: 8),
                      Text(event.date, style: Theme.of(context).textTheme.bodyLarge),
                      if (event.location != null) ...[
                        const SizedBox(width: 24),
                        const Icon(Icons.location_on, size: 18),
                        const SizedBox(width: 8),
                        Text(event.location!, style: Theme.of(context).textTheme.bodyLarge),
                      ],
                    ],
                  ),
                  if (event.description != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      event.description!,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                  const Divider(height: 32),
                ],
              ),
            ),
          Expanded(
            child: Consumer<PhotoProvider>(
              builder: (context, provider, child) {
                if (provider.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (provider.error != null) {
                  return Center(child: Text('Error: ${provider.error}'));
                }

                if (provider.photos.isEmpty) {
                  return const Center(child: Text('No photos found in this event'));
                }

                return RefreshIndicator(
                  onRefresh: () => provider.loadPhotos(widget.eventId),
                  child: GridView.builder(
                    padding: const EdgeInsets.all(4),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 3,
                      crossAxisSpacing: 4,
                      mainAxisSpacing: 4,
                    ),
                    itemCount: provider.photos.length,
                    itemBuilder: (context, index) {
                      final photo = provider.photos[index];
                      return PhotoGridItem(
                        photo: photo,
                        onTap: () {
                          context.push('/gallery/${widget.eventId}/photo', extra: photo);
                        },
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),

      floatingActionButton: FloatingActionButton(
        onPressed: () {
          context.push('/gallery/${widget.eventId}/upload');
        },
        child: const Icon(Icons.add_a_photo),
      ),
    );
  }
}
