import 'package:flutter/material.dart';
import 'package:dastern_mobile/screens/home_screen.dart';

/// Home Page Tab - Just a wrapper for navigation
/// All UI design is in screens/home_screen.dart
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return const HomeScreen();
  }
}
