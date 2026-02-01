import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../providers/photo_provider.dart';
import '../../widgets/photo_grid_item.dart';
import '../../providers/event_provider.dart';
import '../../providers/websocket_provider.dart';

class GalleryScreen extends StatefulWidget {
  final int eventId;

  const GalleryScreen({super.key, required this.eventId});

  @override
  State<GalleryScreen> createState() => _GalleryScreenState();
}

class _GalleryScreenState extends State<GalleryScreen> {
  StreamSubscription? _wsSubscription;

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
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final event = context.watch<EventProvider>().getEventById(widget.eventId);
    final photoProvider = context.watch<PhotoProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Text(event?.name ?? 'Event Gallery'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search by tags...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
                contentPadding: const EdgeInsets.symmetric(vertical: 0),
                filled: true,
                fillColor: Colors.white,
              ),
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
