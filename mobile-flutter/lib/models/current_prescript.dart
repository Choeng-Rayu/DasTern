import 'package:flutter/material.dart';

class PrescriptionItem {
  final String name;
  final String quantity;
  final String usage;
  final Color color;
  final String? imagePath;  // Make sure this exists

  PrescriptionItem({
    required this.name,
    required this.quantity,
    required this.usage,
    required this.color,
    this.imagePath,
  });
}