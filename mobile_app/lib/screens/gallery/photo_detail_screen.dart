import 'package:flutter/material.dart';
// Conditional import for cross-platform download support
import 'dart:html' as html if (dart.library.io) 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:cached_network_image/cached_network_image.dart';
import 'package:provider/provider.dart';
import '../../models/photo.dart';
import '../../providers/photo_provider.dart';
import '../../providers/comment_provider.dart';
import '../../models/comment.dart';

class PhotoDetailScreen extends StatefulWidget {
  final Photo photo;

  const PhotoDetailScreen({super.key, required this.photo});

  @override
  State<PhotoDetailScreen> createState() => _PhotoDetailScreenState();
}

class _PhotoDetailScreenState extends State<PhotoDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CommentProvider>().loadComments(widget.photo.id);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        iconTheme: const IconThemeData(color: Colors.white),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: () {
              final url = widget.photo.fullOriginalUrl;
              debugPrint('Downloading: $url');
              
              if (kIsWeb) {
                // Web-specific download logic
                final anchor = html.AnchorElement(href: url)
                  ..target = 'blank'
                  ..download = 'photo_${widget.photo.id}.jpg';
                html.document.body?.append(anchor);
                anchor.click();
                anchor.remove();
                
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Download started')),
                );
              } else {
                // Mobile download logic (placeholder)
                // In a real app, use plugins like flutter_downloader or url_launcher
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Tap to open: $url')),
                );
              }
            },
          ),
        ],
      ),
      extendBodyBehindAppBar: true,
      body: Stack(
        fit: StackFit.expand,
        children: [
          InteractiveViewer(
            child: Center(
              child: CachedNetworkImage(
                imageUrl: widget.photo.fullWatermarkedUrl,
                placeholder: (context, url) =>
                    const Center(child: CircularProgressIndicator()),
                errorWidget: (context, url, error) =>
                    const Center(child: Icon(Icons.error, color: Colors.white)),
              ),
            ),
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              color: Colors.black54,
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Consumer<PhotoProvider>(
                    builder: (context, provider, child) {
                      final currentPhoto = provider.photos.firstWhere(
                        (p) => p.id == widget.photo.id,
                        orElse: () => widget.photo,
                      );
                      
                      return Row(
                        children: [
                          IconButton(
                            icon: Icon(
                              currentPhoto.isLiked ? Icons.favorite : Icons.favorite_border,
                              color: currentPhoto.isLiked ? Colors.red : Colors.white,
                              size: 30,
                            ),
                            onPressed: () {
                              context.read<PhotoProvider>().toggleLike(widget.photo.id);
                            },
                          ),
                          Text(
                            '${currentPhoto.likesCount} likes',
                            style: const TextStyle(color: Colors.white),
                          ),
                          const SizedBox(width: 20),
                          InkWell(
                            onTap: () => _showComments(context),
                            child: Row(
                              children: [
                                const Icon(Icons.comment, color: Colors.white),
                                const SizedBox(width: 8),
                                Text(
                                  '${currentPhoto.commentsCount} comments',
                                  style: const TextStyle(color: Colors.white),
                                ),
                              ],
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                  IconButton(
                    icon: const Icon(Icons.info_outline, color: Colors.white),
                    onPressed: () {
                      _showPhotoInfo(context, widget.photo);
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showComments(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => _CommentsSheet(photoId: widget.photo.id),
    );
  }

  void _showPhotoInfo(BuildContext context, Photo photo) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(16),
          child: ListView(
            shrinkWrap: true,
            children: [
              Text('Photo Details', style: Theme.of(context).textTheme.headlineSmall),
              const Divider(),
              if (photo.aiTags != null && photo.aiTags!.isNotEmpty) ...[
                const Text('AI Tags:', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: photo.aiTags!.map((tag) => Chip(
                    label: Text(tag),
                    backgroundColor: Colors.blue[50],
                  )).toList(),
                ),
                const SizedBox(height: 16),
              ],
              const Text('Manual Tags:', style: TextStyle(fontWeight: FontWeight.bold)),
              if (photo.manualTags != null && photo.manualTags!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: photo.manualTags!.map((tag) => Chip(
                    label: Text(tag),
                    backgroundColor: Colors.green[50],
                  )).toList(),
                ),
              ],
              TextButton.icon(
                icon: const Icon(Icons.add),
                label: const Text('Add Tag'),
                onPressed: () => _showAddTagDialog(context, photo),
              ),
              const SizedBox(height: 16),
              const Text('EXIF Data:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              if (photo.exifData == null || photo.exifData!.isEmpty)
                const Text('No EXIF metadata available')
              else
                ...photo.exifData!.entries.map((e) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        children: [
                          Text('${e.key}: ', style: const TextStyle(fontWeight: FontWeight.w500)),
                          Expanded(child: Text(e.value.toString())),
                        ],
                      ),
                    )),
            ],
          ),
        );
      },
    );
  }

  void _showAddTagDialog(BuildContext context, Photo photo) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Add Tag'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: 'Enter tag name'),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              if (controller.text.trim().isNotEmpty) {
                final newTag = controller.text.trim();
                final currentTags = List<String>.from(photo.manualTags ?? []);
                if (!currentTags.contains(newTag)) {
                  currentTags.add(newTag);
                  try {
                    await context.read<PhotoProvider>().updateTags(photo.id, currentTags);
                    if (context.mounted) Navigator.pop(dialogContext);
                    // Force refresh by rebuilding the bottom sheet content
                    if (context.mounted) {
                      Navigator.pop(context); // Close info sheet
                      // Re-open info sheet with updated photo data
                      final updatedPhoto = context.read<PhotoProvider>().photos.firstWhere((p) => p.id == photo.id);
                      _showPhotoInfo(context, updatedPhoto);
                    }
                  } catch (e) {
                    if (context.mounted) {
                       ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
                    }
                  }
                }
              }
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}

class _CommentsSheet extends StatefulWidget {
  final int photoId;
  const _CommentsSheet({required this.photoId});

  @override
  State<_CommentsSheet> createState() => _CommentsSheetState();
}

class _CommentsSheetState extends State<_CommentsSheet> {
  final _commentController = TextEditingController();
  int? _replyToId;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  void _submitComment() async {
    if (_commentController.text.trim().isEmpty) return;

    try {
      await context.read<CommentProvider>().addComment(
        widget.photoId,
        _commentController.text.trim(),
        parentId: _replyToId,
      );
      _commentController.clear();
      setState(() {
        _replyToId = null;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to add comment: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
        top: 20,
      ),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.7,
        child: Column(
          children: [
            const Text(
              'Comments',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            Expanded(
              child: Consumer<CommentProvider>(
                builder: (context, provider, child) {
                  final comments = provider.getCommentsForPhoto(widget.photoId);
                  
                  if (provider.isLoading && comments.isEmpty) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  if (comments.isEmpty) {
                    return const Center(child: Text('No comments yet. Be the first to comment!'));
                  }

                  return ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: comments.length,
                    itemBuilder: (context, index) {
                      return _CommentItem(
                        comment: comments[index],
                        onReply: (id) {
                          setState(() {
                            _replyToId = id;
                          });
                        },
                      );
                    },
                  );
                },
              ),
            ),
            if (_replyToId != null)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                color: Colors.grey[200],
                child: Row(
                  children: [
                    const Text('Replying to comment...'),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close, size: 16),
                      onPressed: () => setState(() => _replyToId = null),
                    ),
                  ],
                ),
              ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _commentController,
                      decoration: const InputDecoration(
                        hintText: 'Add a comment...',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: _submitComment,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CommentItem extends StatelessWidget {
  final Comment comment;
  final Function(int) onReply;
  final int depth;

  const _CommentItem({
    required this.comment,
    required this.onReply,
    this.depth = 0,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.only(left: depth * 24.0, bottom: 8.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    comment.authorDisplayName,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    comment.createdAt.split('T')[0],
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(comment.content),
              TextButton(
                onPressed: () => onReply(comment.id),
                child: const Text('Reply', style: TextStyle(fontSize: 12)),
              ),
            ],
          ),
        ),
        if (comment.replies != null)
          ...comment.replies!.map((reply) => _CommentItem(
                comment: reply,
                onReply: onReply,
                depth: depth + 1,
              )),
      ],
    );
  }
}
