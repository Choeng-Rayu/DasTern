import 'package:flutter/material.dart';

class FamilyBottomNavBar extends StatelessWidget {
  final int selectedIndex;
  final String homeLabel;
  final String patientsLabel;
  final String familyAlertLabel;
  final String settingsLabel;
  final String? scanLabel;
  final ValueChanged<int> onItemSelected;

  const FamilyBottomNavBar({
    Key? key,
    required this.selectedIndex,
    required this.homeLabel,
    required this.patientsLabel,
    required this.familyAlertLabel,
    required this.settingsLabel,
    this.scanLabel,
    required this.onItemSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(0, Icons.home_outlined, Icons.home, homeLabel),
              _buildNavItem(1, Icons.calendar_today_outlined, Icons.calendar_today, patientsLabel),
              _buildCenterNavItem(),
              _buildNavItem(3, Icons.family_restroom_outlined, Icons.family_restroom, familyAlertLabel),
              _buildNavItem(4, Icons.settings_outlined, Icons.settings, settingsLabel),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, IconData activeIcon, String label) {
    final isSelected = selectedIndex == index;
    return GestureDetector(
      onTap: () => onItemSelected(index),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isSelected ? activeIcon : icon,
            color: isSelected ? const Color(0xFF4A90D9) : Colors.grey,
            size: 24,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: isSelected ? const Color(0xFF4A90D9) : Colors.grey,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCenterNavItem() {
    // Center scan button is NEVER filled - always outline style
    // It only gets filled when user is actively using the scan feature
    return GestureDetector(
      onTap: () => onItemSelected(2),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.grey.shade300, width: 1.5),
            ),
            child: Icon(
              Icons.qr_code_scanner,
              color: Colors.grey.shade500,
              size: 26,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            scanLabel ?? '',
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey.shade500,
              fontWeight: FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
}