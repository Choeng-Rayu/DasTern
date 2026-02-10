import 'package:flutter/material.dart';
import 'package:dastern_mobile/screens/history_screen.dart';

/// History Page Tab - Just a wrapper for navigation
/// All UI design is in screens/history_screen.dart
class HistoryPage extends StatelessWidget {
  const HistoryPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const HistoryScreen();
  }
}
