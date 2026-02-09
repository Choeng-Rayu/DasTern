import 'package:flutter/material.dart';
import 'package:dastern_mobile/screens/create_prescription_screen.dart';

/// Create Prescription Page Tab - Just a wrapper for navigation
/// All UI design is in screens/create_prescription_screen.dart
class CreatePrescriptionPage extends StatelessWidget {
  const CreatePrescriptionPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const CreatePrescriptionScreen();
  }
}
