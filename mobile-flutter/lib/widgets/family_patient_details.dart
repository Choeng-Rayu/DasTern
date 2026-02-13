import 'package:flutter/material.dart';

class FamilyPatientDetailCard extends StatelessWidget {
  final String name;
  final String statusLabel;
  final bool isPending;
  final String genderLabel;
  final String genderValue;
  final String generationLabel;
  final String generationValue;
  final String ageLabel;
  final String ageValue;
  final String phoneLabel;
  final String phoneValue;
  final String morningLabel;
  final String eveningLabel;
  final String buttonLabel;
  final String? profileImagePath;
  final VoidCallback? onButtonPressed;

  const FamilyPatientDetailCard({
    Key? key,
    required this.name,
    required this.statusLabel,
    this.isPending = true,
    required this.genderLabel,
    required this.genderValue,
    required this.generationLabel,
    required this.generationValue,
    required this.ageLabel,
    required this.ageValue,
    required this.phoneLabel,
    required this.phoneValue,
    required this.morningLabel,
    required this.eveningLabel,
    required this.buttonLabel,
    this.profileImagePath,
    this.onButtonPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 16),
          _buildInfoRow(genderLabel, genderValue, generationLabel, generationValue),
          const SizedBox(height: 8),
          _buildInfoRow(ageLabel, ageValue, '', ''),
          const SizedBox(height: 8),
          _buildInfoRow(phoneLabel, phoneValue, '', ''),
          const SizedBox(height: 16),
          _buildTimeIndicators(),
          const SizedBox(height: 16),
          _buildActionButton(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: Colors.blue.shade100,
            shape: BoxShape.circle,
          ),
          child: ClipOval(
            child: profileImagePath != null
                ? Image.asset(
                    profileImagePath!,
                    width: 56,
                    height: 56,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => const Icon(
                      Icons.person,
                      color: Colors.blue,
                      size: 32,
                    ),
                  )
                : const Icon(Icons.person, color: Colors.blue, size: 32),
          ),
        ),
        const SizedBox(width: 12),
        Text(
          name,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const Spacer(),
        _buildStatusBadge(),
      ],
    );
  }

  Widget _buildStatusBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isPending ? Colors.orange.shade50 : Colors.green.shade50,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isPending ? Colors.orange.shade200 : Colors.green.shade200,
        ),
      ),
      child: Text(
        statusLabel,
        style: TextStyle(
          color: isPending ? Colors.orange.shade700 : Colors.green.shade700,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label1, String value1, String label2, String value2) {
    return Row(
      children: [
        Text(
          '$label1: ',
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey.shade600,
          ),
        ),
        Text(
          value1,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
        if (label2.isNotEmpty) ...[
          const SizedBox(width: 24),
          Text(
            '$label2: ',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade600,
            ),
          ),
          Text(
            value2,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildTimeIndicators() {
    return Row(
      children: [
        _buildTimeIndicator(Colors.red, morningLabel),
        const SizedBox(width: 24),
        _buildTimeIndicator(Colors.grey.shade400, eveningLabel),
      ],
    );
  }

  Widget _buildTimeIndicator(Color color, String label) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(fontSize: 13),
        ),
      ],
    );
  }

  Widget _buildActionButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: onButtonPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.orange,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
        ),
        child: Text(
          buttonLabel,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}