import 'package:flutter/material.dart';

import '../screens/scan_screen.dart';
import '../screens/medicine_schedule_screen.dart';
import '../screens/settings_screen.dart';

class AppRouter {
  static const String initialRoute = '/scan';

  static Route<dynamic>? onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case '/scan':
        return MaterialPageRoute(builder: (_) => const ScanScreen());
      case '/medicine_schedule':
        return MaterialPageRoute(builder: (_) => const MedicineScheduleScreen());
      case '/settings':
        return MaterialPageRoute(builder: (_) => const SettingsScreen());
      default:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(child: Text('Route not found')),
          ),
        );
    }
  }
}
