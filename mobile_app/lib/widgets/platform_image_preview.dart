import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class PlatformImagePreview extends StatelessWidget {
  final XFile file;
  final BoxFit fit;
  final double? width;
  final double? height;

  const PlatformImagePreview({
    super.key,
    required this.file,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    if (kIsWeb) {
      // On Web, we must use Image.network or Image.memory.
      // cross_file (XFile) provides a convenient way to get a URL or bytes.
      return FutureBuilder<Uint8List>(
        future: file.readAsBytes(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done && snapshot.hasData) {
            return Image.memory(
              snapshot.data!,
              fit: fit,
              width: width,
              height: height,
            );
          }
          return const Center(child: CircularProgressIndicator());
        },
      );
    } else {
      // On Mobile/Desktop, we can use Image.file.
      return Image.file(
        File(file.path),
        fit: fit,
        width: width,
        height: height,
      );
    }
  }
}
