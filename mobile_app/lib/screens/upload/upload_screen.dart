import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../providers/photo_provider.dart';
import '../../widgets/platform_image_preview.dart';

class UploadScreen extends StatefulWidget {
  final int eventId;

  const UploadScreen({super.key, required this.eventId});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final ImagePicker _picker = ImagePicker();
  final List<XFile> _selectedImages = [];
  bool _isUploading = false;

  Future<void> _pickImages() async {
    final List<XFile> images = await _picker.pickMultiImage();
    if (images.isNotEmpty) {
      setState(() {
        _selectedImages.addAll(images);
      });
    }
  }

  Future<void> _uploadImages() async {
    if (_selectedImages.isEmpty) return;

    setState(() => _isUploading = true);
    try {
      // Pass the XFile objects directly to the provider
      await context.read<PhotoProvider>().uploadPhotos(_selectedImages, widget.eventId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Upload successful')),
        );
        context.pop(); // Go back to gallery
        // Trigger refresh of gallery
        context.read<PhotoProvider>().loadPhotos(widget.eventId);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Upload failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isUploading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Upload Photos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: (_selectedImages.isEmpty || _isUploading) ? null : _uploadImages,
          ),
        ],
      ),
      body: _isUploading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Expanded(
                  child: GridView.builder(
                    padding: const EdgeInsets.all(8),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 3,
                      crossAxisSpacing: 8,
                      mainAxisSpacing: 8,
                    ),
                    itemCount: _selectedImages.length + 1,
                    itemBuilder: (context, index) {
                      if (index == 0) {
                        return InkWell(
                          onTap: _pickImages,
                          child: Container(
                            color: Colors.grey[200],
                            child: const Icon(Icons.add_a_photo, size: 40),
                          ),
                        );
                      }
                      final image = _selectedImages[index - 1];
                      return Stack(
                        fit: StackFit.expand,
                        children: [
                          PlatformImagePreview(file: image),
                          Positioned(
                            top: 4,
                            right: 4,
                            child: InkWell(
                              onTap: () {
                                setState(() {
                                  _selectedImages.removeAt(index - 1);
                                });
                              },
                              child: const CircleAvatar(
                                radius: 12,
                                backgroundColor: Colors.red,
                                child: Icon(Icons.close, size: 16, color: Colors.white),
                              ),
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                ),
              ],
            ),
    );
  }
}
