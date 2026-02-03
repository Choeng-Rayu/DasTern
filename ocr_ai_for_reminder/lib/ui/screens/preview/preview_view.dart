import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/medicine.dart';
// import '../../../models/prescription.dart'; // Unused
import '../../../providers/scan_provider.dart';
import '../../widgets/custom_button.dart';

class PreviewView extends StatelessWidget {
  const PreviewView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Review Prescription'),
      ),
      body: Consumer<ScanProvider>(
        builder: (context, provider, _) {
          final prescription = provider.prescription;
          if (prescription == null) {
            return const Center(child: Text('No data found'));
          }

          return Column(
            children: [
              Expanded(
                child: ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: prescription.medications.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final med = prescription.medications[index];
                    return _MedicineCard(
                      medicine: med,
                      onEdit: (updatedMed) {
                         provider.updateMedicalDetails(index, updatedMed);
                      },
                    );
                  },
                ),
              ),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, -5),
                    ),
                  ],
                ),
                child: CustomButton(
                  text: 'Confirm Prescription',
                  icon: Icons.check,
                  onPressed: () {
                    provider.confirmPrescription();
                    Navigator.popUntil(context, (route) => route.isFirst);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Prescription saved!')),
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _MedicineCard extends StatelessWidget {
  final Medicine medicine;
  final Function(Medicine) onEdit;

  const _MedicineCard({
    required this.medicine,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    medicine.name,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit, size: 20),
                  onPressed: () => _showEditDialog(context),
                ),
              ],
            ),
            const SizedBox(height: 8),
            _buildInfoRow(context, Icons.medication, '${medicine.dosage}'),
            const SizedBox(height: 4),
            _buildInfoRow(context, Icons.schedule, medicine.frequency), 
            const SizedBox(height: 12),
            _buildScheduleBadges(context),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(BuildContext context, IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey),
        const SizedBox(width: 8),
        Text(text, style: Theme.of(context).textTheme.bodyMedium),
      ],
    );
  }

  Widget _buildScheduleBadges(BuildContext context) {
    return Wrap(
      spacing: 8,
      children: [
        if (medicine.isMorning) _Badge(label: 'Morning'),
        if (medicine.isAfternoon) _Badge(label: 'Noon'),
        if (medicine.isEvening) _Badge(label: 'Evening'),
        if (medicine.isNight) _Badge(label: 'Night'),
      ],
    );
  }

  void _showEditDialog(BuildContext context) {
    final nameCtrl = TextEditingController(text: medicine.name);
    final doseCtrl = TextEditingController(text: medicine.dosage);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Medicine'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Medicine Name'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: doseCtrl,
              decoration: const InputDecoration(labelText: 'Dosage (e.g., 500mg)'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
               onEdit(medicine.copyWith(
                 name: nameCtrl.text,
                 dosage: doseCtrl.text,
               ));
               Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  final String label;

  const _Badge({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Theme.of(context).primaryColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).primaryColor.withValues(alpha: 0.2),
        ),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          color: Theme.of(context).primaryColor,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
