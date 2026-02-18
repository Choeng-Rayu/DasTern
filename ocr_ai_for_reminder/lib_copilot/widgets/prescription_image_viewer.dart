import 'dart:io';
import 'package:flutter/material.dart';

class PrescriptionImageViewer extends StatelessWidget {
  final File imageFile;

  const PrescriptionImageViewer({
    super.key,
    required this.imageFile,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Image.file(
          imageFile,
          fit: BoxFit.cover,
          width: double.infinity,
          height: 250,
          errorBuilder: (context, error, stackTrace) {
            return Container(
              width: double.infinity,
              height: 250,
              color: Colors.grey[300],
              child: const Icon(
                Icons.broken_image,
                size: 64,
                color: Colors.grey,
              ),
            );
          },
        ),
      ),
    );
  }
}
