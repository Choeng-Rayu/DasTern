import 'package:flutter/material.dart';
import '../../data/prescription_storage.dart';
import '../../models/medication.dart';

class SavedPrescriptionsScreen extends StatefulWidget {
  const SavedPrescriptionsScreen({super.key});

  @override
  State<SavedPrescriptionsScreen> createState() =>
      _SavedPrescriptionsScreenState();
}

class _SavedPrescriptionsScreenState extends State<SavedPrescriptionsScreen> {
  final PrescriptionStorage _storage = PrescriptionStorage();
  List<PrescriptionData> _prescriptions = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadPrescriptions();
  }

  Future<void> _loadPrescriptions() async {
    setState(() => _isLoading = true);
    try {
      final prescriptions = await _storage.loadPrescriptions();
      setState(() {
        _prescriptions = prescriptions.reversed.toList(); // Most recent first
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading prescriptions: $e')),
        );
      }
    }
  }

  Future<void> _deletePrescription(String id) async {
    try {
      await _storage.deletePrescription(id);
      await _loadPrescriptions();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Prescription deleted')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Saved Prescriptions'),
        actions: [
          if (_prescriptions.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_sweep),
              onPressed: _confirmClearAll,
              tooltip: 'Clear all',
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _prescriptions.isEmpty
              ? _buildEmptyState()
              : RefreshIndicator(
                  onRefresh: _loadPrescriptions,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _prescriptions.length,
                    itemBuilder: (context, index) {
                      final prescription = _prescriptions[index];
                      return _buildPrescriptionCard(prescription);
                    },
                  ),
                ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.folder_open,
            size: 80,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No Saved Prescriptions',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Prescriptions you save will appear here',
            style: TextStyle(color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildPrescriptionCard(PrescriptionData prescription) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _showPrescriptionDetails(prescription),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.medical_services,
                        color: Colors.blue),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          prescription.patientName ?? 'Prescription',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          _formatDate(prescription.createdAt),
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete, color: Colors.red),
                    onPressed: () => _confirmDelete(prescription),
                  ),
                ],
              ),
              if (prescription.diagnosis != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.orange.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'Diagnosis: ${prescription.diagnosis}',
                    style: TextStyle(
                      color: Colors.orange[900],
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              Text(
                '${prescription.medications.length} Medication(s)',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Colors.grey[700],
                ),
              ),
              const SizedBox(height: 8),
              ...prescription.medications.take(3).map((med) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      children: [
                        const Icon(Icons.circle,
                            size: 6, color: Colors.green),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            '${med.name} - ${med.dosage}',
                            style: const TextStyle(fontSize: 14),
                          ),
                        ),
                      ],
                    ),
                  )),
              if (prescription.medications.length > 3)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    '+ ${prescription.medications.length - 3} more',
                    style: TextStyle(
                      color: Colors.blue[700],
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _showPrescriptionDetails(PrescriptionData prescription) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) => Column(
          children: [
            Container(
              margin: const EdgeInsets.only(top: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Expanded(
              child: ListView(
                controller: scrollController,
                padding: const EdgeInsets.all(24),
                children: [
                  Text(
                    prescription.patientName ?? 'Prescription Details',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _formatDate(prescription.createdAt),
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  if (prescription.diagnosis != null) ...[
                    const SizedBox(height: 16),
                    Text(
                      'Diagnosis',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.grey[700],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(prescription.diagnosis!),
                  ],
                  const SizedBox(height: 24),
                  Text(
                    'Medications (${prescription.medications.length})',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  ...prescription.medications
                      .map((med) => _buildMedicationDetail(med)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMedicationDetail(MedicationInfo med) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade50, Colors.purple.shade50],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            med.name,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          _buildInfoRow(Icons.medication, 'Dosage', med.dosage),
          _buildInfoRow(
              Icons.schedule, 'Times', med.times24h.join(', ') + ' (' + med.times.join(', ') + ')'),
          _buildInfoRow(Icons.repeat, 'Repeat', med.repeat),
          if (med.durationDays != null)
            _buildInfoRow(
                Icons.calendar_today, 'Duration', '${med.durationDays} days'),
          if (med.notes.isNotEmpty)
            _buildInfoRow(Icons.note, 'Notes', med.notes),
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 16, color: Colors.blue[700]),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }

  void _confirmDelete(PrescriptionData prescription) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Prescription?'),
        content: Text(
          'Are you sure you want to delete this prescription for ${prescription.patientName ?? "this patient"}?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _deletePrescription(prescription.id);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  void _confirmClearAll() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear All Prescriptions?'),
        content: const Text(
          'This will permanently delete all saved prescriptions. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await _storage.clearAll();
              await _loadPrescriptions();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('All prescriptions cleared')),
                );
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Clear All'),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return 'Today at ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays == 1) {
      return 'Yesterday';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}
