import 'package:flutter/material.dart';
import '../widgets/doctor_header.dart';
import '../widgets/statistics_row.dart';
import '../widgets/reminder_section.dart';
import '../widgets/chart_section.dart';

class DoctorScreen extends StatelessWidget {
  const DoctorScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Sample data
    final reminders = [
      {
        'name': 'សុខឡាង',
        'description': 'ខកខានការទទួលទានថ្នាំ 2ដង(ពេលព្រឹក និងពេលថ្ងៃ)',
        'time': '1:00ព្រឹក'
      },
      {
        'name': 'សុខា',
        'description': 'ខកខានការទទួលទានថ្នាំ 2ដង(ពេលព្រឹក និងពេលថ្ងៃ)',
        'time': '1:00ព្រឹក'
      },
      {
        'name': 'ធីតា',
        'description': 'ខកខានការទទួលទានថ្នាំ 2ដង(ពេលព្រឹក និងពេលថ្ងៃ)',
        'time': '1:00ព្រឹក'
      },
      {
        'name': 'ណាណា',
        'description': 'ខកខានការទទួលទានថ្នាំ 2ដង(ពេលព្រឹក និងពេលថ្ងៃ)',
        'time': '1:00ព្រឹក'
      },
    ];

    final chartData = [
      {'day': 'ច័ន្ទ', 'received': 3, 'missed': 1},
      {'day': 'អង្គារ', 'received': 5, 'missed': 2},
      {'day': 'ពុធ', 'received': 2, 'missed': 1},
      {'day': 'ព្រហ', 'received': 4, 'missed': 2},
      {'day': 'សុក្រ', 'received': 6, 'missed': 1},
      {'day': 'សៅរ៍', 'received': 4, 'missed': 3},
      {'day': 'អាទិត្យ', 'received': 3, 'missed': 4},
    ];

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.blue.shade400,
              Colors.blue.shade50,
            ],
            stops: const [0.0, 0.3],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Section
                DoctorHeader(
                  userName: 'សូស្តី ឧត្តមហេង !',
                  onNotificationTap: () {
                    // Handle notification tap
                  },
                ),
                const SizedBox(height: 20),

                // Statistics Cards Row
                const StatisticsRow(
                  receivedCount: '20',
                  pendingCount: '04',
                ),
                const SizedBox(height: 20),

                // Reminder Section
                ReminderSection(reminders: reminders),
                const SizedBox(height: 20),

                // Chart Section
                ChartSection(
                  chartData: chartData,
                  onDayTap: () {
                    // Handle day filter
                  },
                  onMonthTap: () {
                    // Handle month filter
                  },
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
      // bottomNavigationBar: _buildBottomNavigation(),
    );
  }

  // Widget _buildBottomNavigation() {
  //   return Container(
  //     decoration: BoxDecoration(
  //       color: Colors.white,
  //       boxShadow: [
  //         BoxShadow(
  //           color: Colors.black.withOpacity(0.1),
  //           blurRadius: 10,
  //           offset: const Offset(0, -2),
  //         ),
  //       ],
  //     ),
      // child: BottomNavigationBar(
      //   type: BottomNavigationBarType.fixed,
      //   currentIndex: 1,
      //   selectedItemColor: Colors.blue.shade400,
      //   unselectedItemColor: Colors.grey,
      //   items: const [
      //     BottomNavigationBarItem(
      //       icon: Icon(Icons.home_outlined),
      //       label: 'ទំព័រដើម',
      //     ),
      //     BottomNavigationBarItem(
      //       icon: Icon(Icons.medication),
      //       label: 'គ្រឿងញៀន',
      //     ),
      //     BottomNavigationBarItem(
      //       icon: Icon(Icons.qr_code_scanner),
      //       label: '',
      //     ),
      //     BottomNavigationBarItem(
      //       icon: Icon(Icons.insert_chart_outlined),
      //       label: 'របាយការណ៍',
      //     ),
      //     BottomNavigationBarItem(
      //       icon: Icon(Icons.settings_outlined),
      //       label: 'កំណត់',
      //     ),
      //   ],
      // ),
    // );
  // }
}
