import 'package:flutter/material.dart';
import 'package:dastern_mobile/screens/patient_tracking_screen.dart';

/// Patient Tracking Page Tab - Just a wrapper for navigation
/// All UI design is in screens/patient_tracking_screen.dart
class PatientTrackingPage extends StatelessWidget {
  const PatientTrackingPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const PatientTrackingScreen();
  }
}
