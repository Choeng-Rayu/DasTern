import 'package:dastern_mobile/screens/family_interface/family_alert_screen.dart';
import 'package:flutter/material.dart';
import '../../models/family_member.dart';
import '../../widgets/header_widgets.dart';
import '../../widgets/family_bottom_nav.dart';
import '../../widgets/family_list_card.dart';

class FamilyLinkHomeScreen extends StatefulWidget {
  const FamilyLinkHomeScreen({super.key});

  @override
  State<FamilyLinkHomeScreen> createState() => _FamilyLinkHomeScreenState();
}

class _FamilyLinkHomeScreenState extends State<FamilyLinkHomeScreen> {
  int _selectedNavIndex = 2;

  // Dummy data for family members
  final List<FamilyMember> members = [
    FamilyMember(
      id: '1',
      name: 'សុខឡាង',
      gender: 'ប្រុស',
      age: 20,
      phone: '090979874',
      hasPendingPrescription: false,
      lastActivity: 'ទទូលទានថ្នាំ',
    ),
    FamilyMember(
      id: '2',
      name: 'សុម៉ា',
      gender: 'ស្រី',
      age: 18,
      phone: '090123456',
      hasPendingPrescription: true,
      lastActivity: 'មិនទាន់ទទួលថ្នាំ',
    ),
    FamilyMember(
      id: '3',
      name: 'មួយមា',
      gender: 'ស្រី',
      age: 15,
      phone: '090654321',
      hasPendingPrescription: true,
      lastActivity: 'មិនទាន់ទទួលថ្នាំ',
    ),
    FamilyMember(
      id: '4',
      name: 'សុខឡេង',
      gender: 'ប្រុស',
      age: 10,
      phone: '090111222',
      hasPendingPrescription: false,
      lastActivity: 'ទទូលទានថ្នាំ',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FB),
       body: SafeArea(
         child: SingleChildScrollView(
           child: Column(
             crossAxisAlignment: CrossAxisAlignment.start,
             children: [
               // Header
               const UserHeader(
                 userName: 'សួស្តី បងហេង!',
                 userRole: '',
                 hospitalName: 'ដាស់ធឺន',
                 height: 200,
                 logoRadius: 28,
               ),
               const SizedBox(height: 16),
 
               // Title
               const Padding(
                 padding: EdgeInsets.symmetric(horizontal: 20),
                 child: Text(
                   'មុខងារគ្រួសារ',
                   style: TextStyle(
                     fontSize: 22,
                     fontWeight: FontWeight.bold,
                   ),
                 ),
               ),
               const SizedBox(height: 12),
 
               // Search Bar
               Padding(
                 padding: const EdgeInsets.symmetric(horizontal: 20),
                 child: TextField(
                   decoration: InputDecoration(
                     hintText: 'ស្វែងរកអ្នកជំងឺ',
                     hintStyle: TextStyle(color: Colors.grey.shade400),
                     prefixIcon: Icon(Icons.search, color: Colors.grey.shade400),
                     filled: true,
                     fillColor: Colors.white,
                     border: OutlineInputBorder(
                       borderRadius: BorderRadius.circular(12),
                       borderSide: BorderSide.none,
                     ),
                     contentPadding: const EdgeInsets.symmetric(vertical: 12),
                   ),
                 ),
               ),
               const SizedBox(height: 16),
 
               // Family Member List
               Padding(
                 padding: const EdgeInsets.symmetric(horizontal: 12),
                 child: Container(
                   decoration: BoxDecoration(
                     color: Colors.white,
                     borderRadius: BorderRadius.circular(22),
                     boxShadow: [
                       BoxShadow(
                         color: Colors.black.withOpacity(0.06),
                         blurRadius: 12,
                         offset: const Offset(0, 4),
                       ),
                     ],
                   ),
                   child: Column(
                     children: members
                         .map((member) => InkWell(
                               onTap: () {
                                 Navigator.of(context).push(
                                   MaterialPageRoute(
                                     builder: (context) => FamilyAlertScreen(member: member),
                                   ),
                                 );
                               },
                               child: FamilyMemberListCard(member: member),
                             ))
                         .toList(),
                   ),
                 ),
               ),
               const SizedBox(height: 32),
             ],
           ),
         ),
       ),
      bottomNavigationBar: FamilyBottomNavBar(
        selectedIndex: _selectedNavIndex,
        homeLabel: 'ទំព័រដើម',
        patientsLabel: 'អ្នកជំងឺ',
        familyAlertLabel: 'មុខងារគ្រួសារ',
        settingsLabel: 'ការកំណត់',
        scanLabel: 'ស្កេន',
        onItemSelected: (index) {
          setState(() => _selectedNavIndex = index);
          // Handle navigation if needed
        },
      ),
    );
  }
}