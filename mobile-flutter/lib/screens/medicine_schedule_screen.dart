import 'package:flutter/material.dart';

import '../models/medicine.dart';

class MedicineScheduleScreen extends StatelessWidget {
  const MedicineScheduleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Medicine> demo = [
      Medicine(name: 'Paracetamol', timeOfDay: 'Morning'),
      Medicine(name: 'Vitamin C', timeOfDay: 'Afternoon'),
      Medicine(name: 'Melatonin', timeOfDay: 'Night'),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Medicine Schedule')),
      body: ListView.builder(
        itemCount: demo.length,
        itemBuilder: (context, index) {
          final m = demo[index];
          return ListTile(
            title: Text(m.name),
            subtitle: Text(m.timeOfDay),
            leading: const Icon(Icons.medication),
          );
        },
      ),
    );
  }
}
