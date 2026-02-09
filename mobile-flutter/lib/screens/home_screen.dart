import 'package:flutter/material.dart';
import 'package:dastern_mobile/widgets/background_homepage.dart';
import 'package:dastern_mobile/widgets/header_widgets.dart';
import 'package:dastern_mobile/widgets/medication_shift.dart';
import 'package:dastern_mobile/models/day_period.dart' as day_period;

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      extendBodyBehindAppBar: true,
      body: Column(
        children: [
          // Header section
          UserHeader(
            userName: 'Hello soklang',
            userRole: 'Patient',
            height: 250,
          ),

          // Scrollable content
          Expanded(
            child: BackgroundHomepage(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(height: 24),

                    // 🔥 Medication Schedule (Horizontal Roll)
                    SizedBox(
                      height: 140,
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: [
                            SizedBox(
                              width: 280,
                              child: MedicationShift(
                                period: day_period.DayPeriod.morning,
                                backgroundImage: 'assets/images/morning.png',
                                times: ['8:00 AM', '9:00 AM'],
                              ),
                            ),
                            SizedBox(width: 12),
                            SizedBox(
                              width: 280,
                              child: MedicationShift(
                                period: day_period.DayPeriod.afternoon,
                                backgroundImage: 'assets/images/afternoon.png',
                                times: ['12:00 PM', '1:00 PM'],
                              ),
                            ),
                            SizedBox(width: 12),
                            SizedBox(
                              width: 280,
                              child: MedicationShift(
                                period: day_period.DayPeriod.night,
                                backgroundImage: 'assets/images/night.png',
                                times: ['6:00 PM', '7:00 PM'],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
