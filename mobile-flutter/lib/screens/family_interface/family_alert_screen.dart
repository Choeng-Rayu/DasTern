import 'package:dastern_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import '../../models/current_prescript.dart';
import '../../widgets/family_header.dart';
import '../../widgets/family_alert_card.dart';
import '../../widgets/family_patient_details.dart';
import '../../widgets/family_prescription_list.dart';
import '../../widgets/family_bottom_nav.dart';

class FamilyAlertScreen extends StatefulWidget {
  const FamilyAlertScreen({super.key});

  @override
  State<FamilyAlertScreen> createState() => _FamilyAlertScreenState();
}

class _FamilyAlertScreenState extends State<FamilyAlertScreen> {
  int _selectedNavIndex = 3;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isKhmer = Localizations.localeOf(context).languageCode == 'km';

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FB),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with doctor icon near DasTern title
            FamilyHeaderWidget(
              appName: isKhmer ? 'ដាស់ធឺន' : 'DasTern',
              greeting: isKhmer ? 'សួស្តី មេងហេង !' : 'Hello Mengheng!',
              avatarImagePath: 'assets/images/doctor.png', // Doctor icon near title
              backgroundImagePath: 'assets/images/header_background.png',
              onNotificationTap: _onNotificationTap,
            ),
            const SizedBox(height: 16),

            // Title
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                l10n.familyAlert,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Search Bar
            _buildSearchBar(l10n),
            const SizedBox(height: 16),

            // Alert Card
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: FamilyAlertCard(
                name: isKhmer ? 'សុខឡាង' : 'Soklang',
                description: isKhmer
                    ? 'នៅតែរង់ចាំទទួលថ្នាំ ពេលព្រឹក'
                    : 'Still waiting for morning medication',
                time: isKhmer ? '១ម៉ោងមុន' : '1 hour ago',
                date: isKhmer ? '៣១-១២-២០២៥' : '31-12-2025',
                profileImagePath: 'assets/images/profile.png',
                onTap: _onAlertCardTap,
              ),
            ),
            const SizedBox(height: 16),

            // Patient Detail Card
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: FamilyPatientDetailCard(
                name: isKhmer ? 'សុខឡាង' : 'Soklang',
                statusLabel: l10n.pendingPrescription,
                isPending: true,
                genderLabel: l10n.gender,
                genderValue: isKhmer ? 'ប្រុស' : 'Male',
                generationLabel: isKhmer ? 'អាយុ' : 'Gen',
                generationValue: isKhmer ? 'ឆ្នាំ១១សា៤' : 'Alpha',
                ageLabel: isKhmer ? 'អាយុ' : 'Age',
                ageValue: isKhmer ? '២០ ឆ្នាំ' : '20 years',
                phoneLabel: isKhmer ? 'លេខទូរស័ព្ទ' : 'Phone',
                phoneValue: '090979874',
                morningLabel: isKhmer ? 'ពេលព្រឹក' : 'Morning',
                eveningLabel: isKhmer ? 'ពេលល្ងាច' : 'Evening',
                buttonLabel: l10n.viewPrescription,
                profileImagePath: 'assets/images/profile.png',
                onButtonPressed: _onViewPrescription,
              ),
            ),
            const SizedBox(height: 16),

            // Prescription List with medicine images
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: FamilyPrescriptionList(
                title: l10n.prescriptionDate,
                date: isKhmer ? '២០-កុម្ភះ-២០២៥' : '20-Feb-2025',
                medicineLabel: l10n.medicine,
                quantityLabel: l10n.quantity,
                usageLabel: l10n.usage,
                items: _getPrescriptionItems(isKhmer),
              ),
            ),
            const SizedBox(height: 100),
          ],
        ),
      ),
      bottomNavigationBar: FamilyBottomNavBar(
        selectedIndex: _selectedNavIndex,
        homeLabel: l10n.home,
        patientsLabel: l10n.patients,
        familyAlertLabel: l10n.familyAlert,
        settingsLabel: l10n.settings,
        scanLabel: isKhmer ? 'ស្កេន' : 'Scan',
        onItemSelected: _onNavItemSelected,
      ),
    );
  }

  Widget _buildSearchBar(AppLocalizations l10n) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: TextField(
        decoration: InputDecoration(
          hintText: l10n.searchMember,
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
    );
  }

  List<PrescriptionItem> _getPrescriptionItems(bool isKhmer) {
    return [
      PrescriptionItem(
        name: isKhmer ? 'ប៉ារ៉ាសេតាមុល' : 'Paracetamol',
        quantity: isKhmer ? '១ គ្រាប់' : '1 tablet',
        usage: isKhmer ? 'ព្រឹក និង ល្ងាច' : 'Morning & Evening',
        color: Colors.grey,
        imagePath: 'assets/images/paracetamol_icon.png',
      ),
      PrescriptionItem(
        name: isKhmer ? 'អុីបុយប្រូហ្វេន' : 'Ibuprofen',
        quantity: isKhmer ? '១ គ្រាប់' : '1 tablet',
        usage: isKhmer ? 'ព្រឹក និង ល្ងាច' : 'Morning & Evening',
        color: Colors.orange,
        imagePath: 'assets/images/ibubrofen_icon.png',
      ),
      PrescriptionItem(
        name: isKhmer ? 'ឡូរ៉ាតាដីន' : 'Loratadine',
        quantity: isKhmer ? '១ គ្រាប់' : '1 tablet',
        usage: isKhmer ? 'ព្រឹក និង ល្ងាច' : 'Morning & Evening',
        color: Colors.purple,
        imagePath: 'assets/images/loratadine_icon.png',
      ),
    ];
  }

  void _onNotificationTap() {
    // Handle notification tap
  }

  void _onAlertCardTap() {
    // Handle alert card tap
  }

  void _onViewPrescription() {
    // Handle view prescription
  }

  void _onNavItemSelected(int index) {
    setState(() => _selectedNavIndex = index);
    // Handle navigation
  }
}