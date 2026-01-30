import 'package:flutter/material.dart';
import 'package:dastern_mobile/screens/settings_screen.dart';

/// Settings Page Tab - Just a wrapper for navigation
/// All UI design is in screens/settings_screen.dart
class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const SettingsScreen();
  }
}
