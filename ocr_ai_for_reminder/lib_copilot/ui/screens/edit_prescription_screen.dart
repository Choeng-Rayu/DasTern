import 'package:flutter/material.dart';
import '../../models/medication.dart';

class EditPrescriptionScreen extends StatefulWidget {
  final List<MedicationInfo>? initialMedications;

  const EditPrescriptionScreen({
    super.key,
    this.initialMedications,
  });

  @override
  State<EditPrescriptionScreen> createState() => _EditPrescriptionScreenState();
}

class _EditPrescriptionScreenState extends State<EditPrescriptionScreen> {
  late List<Map<String, dynamic>> medications;
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    medications = widget.initialMedications
            ?.map((m) => {
                  'name': m.name,
                  'dosage': m.dosage,
                  'times': List<String>.from(m.times),
                  'times24h': List<String>.from(m.times24h),
                  'repeat': m.repeat,
                  'durationDays': m.durationDays,
                  'notes': m.notes,
                })
            .toList() ??
        [];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Prescription'),
        backgroundColor: Colors.purple.shade700,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: 'Add Medication',
            onPressed: _addMedication,
          ),
        ],
      ),
      body: medications.isEmpty
          ? _buildEmptyState()
          : Form(
              key: _formKey,
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: medications.length,
                itemBuilder: (context, index) {
                  return _buildMedicationEditor(index);
                },
              ),
            ),
      bottomNavigationBar:
          medications.isNotEmpty ? _buildBottomActions() : null,
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.medication_outlined,
              size: 64, color: Colors.grey.shade300),
          const SizedBox(height: 16),
          const Text(
            'No Medications',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text('Add medications to your prescription'),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            icon: const Icon(Icons.add),
            label: const Text('Add First Medication'),
            onPressed: _addMedication,
          ),
        ],
      ),
    );
  }

  Widget _buildMedicationEditor(int index) {
    final medication = medications[index];

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ExpansionTile(
        initiallyExpanded: medications.length == 1,
        leading: CircleAvatar(
          backgroundColor: Colors.purple.shade100,
          child: Text('${index + 1}'),
        ),
        title: Text(
          medication['name']?.isEmpty ?? true
              ? 'New Medication'
              : medication['name'],
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: medication['dosage']?.isNotEmpty ?? false
            ? Text(medication['dosage'])
            : null,
        trailing: medications.length > 1
            ? IconButton(
                icon: const Icon(Icons.delete_outline, color: Colors.red),
                onPressed: () => _removeMedication(index),
              )
            : null,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                TextFormField(
                  decoration:
                      const InputDecoration(labelText: 'Medication Name *'),
                  initialValue: medication['name'],
                  onChanged: (value) {
                    setState(() {
                      medications[index]['name'] = value;
                    });
                  },
                  validator: (value) =>
                      value?.isEmpty ?? true ? 'Name is required' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  decoration: const InputDecoration(
                    labelText: 'Dosage *',
                    hintText: 'e.g., 500mg, 2 tablets',
                  ),
                  initialValue: medication['dosage'],
                  onChanged: (value) {
                    setState(() {
                      medications[index]['dosage'] = value;
                    });
                  },
                  validator: (value) =>
                      value?.isEmpty ?? true ? 'Dosage is required' : null,
                ),
                const SizedBox(height: 16),
                _buildTimesEditor(index),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        decoration:
                            const InputDecoration(labelText: 'Frequency'),
                        initialValue: medication['repeat'],
                        onChanged: (value) {
                          setState(() {
                            medications[index]['repeat'] = value;
                          });
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: TextFormField(
                        decoration:
                            const InputDecoration(labelText: 'Duration (days)'),
                        initialValue:
                            medication['durationDays']?.toString() ?? '',
                        keyboardType: TextInputType.number,
                        onChanged: (value) {
                          setState(() {
                            medications[index]['durationDays'] =
                                int.tryParse(value);
                          });
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                TextFormField(
                  decoration: const InputDecoration(labelText: 'Notes'),
                  initialValue: medication['notes'],
                  maxLines: 3,
                  onChanged: (value) {
                    setState(() {
                      medications[index]['notes'] = value;
                    });
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimesEditor(int index) {
    final times = List<String>.from(medications[index]['times'] ?? []);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Times of Day'),
            TextButton.icon(
              icon: const Icon(Icons.add, size: 18),
              label: const Text('Add'),
              onPressed: () => _addTime(index),
            ),
          ],
        ),
        Wrap(
          spacing: 8,
          children: [
            ...times.map((time) => Chip(
                  label: Text(time),
                  deleteIcon: const Icon(Icons.close, size: 18),
                  onDeleted: () => _removeTime(index, time),
                )),
          ],
        ),
      ],
    );
  }

  Widget _buildBottomActions() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton.icon(
              icon: const Icon(Icons.cancel),
              label: const Text('Cancel'),
              onPressed: () => Navigator.pop(context),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            flex: 2,
            child: ElevatedButton.icon(
              icon: const Icon(Icons.check),
              label: const Text('Save'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.purple.shade700,
              ),
              onPressed: _savePrescription,
            ),
          ),
        ],
      ),
    );
  }

  void _addMedication() {
    setState(() {
      medications.add({
        'name': '',
        'dosage': '',
        'times': [],
        'times24h': [],
        'repeat': 'daily',
        'durationDays': null,
        'notes': '',
      });
    });
  }

  void _removeMedication(int index) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Remove Medication'),
        content: Text('Remove ${medications[index]['name']}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              setState(() {
                medications.removeAt(index);
              });
              Navigator.pop(ctx);
            },
            child: const Text('Remove', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _addTime(int index) {
    final timeOptions = ['morning', 'noon', 'evening', 'night'];
    final times = List<String>.from(medications[index]['times'] ?? []);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Time'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: timeOptions
              .where((t) => !times.contains(t))
              .map((time) => ListTile(
                    title: Text(time),
                    onTap: () {
                      setState(() {
                        medications[index]['times'] = [...times, time];
                        medications[index]['times24h'] = [
                          ...(medications[index]['times24h'] ?? []),
                          _convertTo24h(time)
                        ];
                      });
                      Navigator.pop(ctx);
                    },
                  ))
              .toList(),
        ),
      ),
    );
  }

  String _convertTo24h(String time) {
    final map = {
      'morning': '08:00',
      'noon': '12:00',
      'evening': '18:00',
      'night': '21:00',
    };
    return map[time] ?? time;
  }

  void _removeTime(int index, String time) {
    setState(() {
      final times = List<String>.from(medications[index]['times'] ?? []);
      final times24h = List<String>.from(medications[index]['times24h'] ?? []);
      final timeIndex = times.indexOf(time);
      times.remove(time);
      if (timeIndex >= 0 && timeIndex < times24h.length) {
        times24h.removeAt(timeIndex);
      }
      medications[index]['times'] = times;
      medications[index]['times24h'] = times24h;
    });
  }

  void _savePrescription() {
    if (_formKey.currentState?.validate() ?? false) {
      final medList = medications
          .map((m) => MedicationInfo(
                name: m['name'] ?? '',
                dosage: m['dosage'] ?? '',
                times: List<String>.from(m['times'] ?? []),
                times24h: List<String>.from(m['times24h'] ?? []),
                repeat: m['repeat'] ?? 'daily',
                durationDays: m['durationDays'],
                notes: m['notes'] ?? '',
              ))
          .toList();

      Navigator.pushNamed(
        context,
        '/final-preview',
        arguments: medList,
      );
    }
  }
}
