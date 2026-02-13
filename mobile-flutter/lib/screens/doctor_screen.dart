import 'package:flutter/material.dart';
import 'package:dastern_mobile/widgets/background_homepage.dart';
import 'package:dastern_mobile/widgets/header_widgets.dart';
import 'package:dastern_mobile/widgets/medication_shift.dart';
import 'package:dastern_mobile/models/day_period.dart' as day_period;

class DoctorScreen extends StatefulWidget {
  const DoctorScreen({super.key});

  @override
  State<DoctorScreen> createState() => _DoctorScreenState();
}

class _DoctorScreenState extends State<DoctorScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      body: Column(
        children: [
          // Header section with UserHeader widget
          UserHeader(
            userName: 'Welcome Doctor',
            userRole: 'Healthcare Provider',
            height: 250,
          ),

          // Scrollable content
          Expanded(
            child: BackgroundHomepage(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 24),

                    // Section Title
                    const Text(
                      'Patient Medication Schedule',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 16),

                    // 🔥 Medication Schedule (Horizontal Scroll)
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
                            const SizedBox(width: 12),
                            SizedBox(
                              width: 280,
                              child: MedicationShift(
                                period: day_period.DayPeriod.afternoon,
                                backgroundImage: 'assets/images/afternoon.png',
                                times: ['12:00 PM', '1:00 PM'],
                              ),
                            ),
                            const SizedBox(width: 12),
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

                    const SizedBox(height: 32),

                    // Additional Info Section
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.blue.withOpacity(0.3),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Patient Information',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                          const SizedBox(height: 12),
                          const Text(
                            '• Monitor patient medication adherence',
                            style: TextStyle(fontSize: 14, color: Colors.black54),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            '• Track medication effectiveness',
                            style: TextStyle(fontSize: 14, color: Colors.black54),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            '• Receive alerts for missed doses',
                            style: TextStyle(fontSize: 14, color: Colors.black54),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 24),
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
