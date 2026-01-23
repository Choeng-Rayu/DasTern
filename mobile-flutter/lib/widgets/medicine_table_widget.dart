import 'package:flutter/material.dart';
import '../models/medicine.dart';

class MedicineTableWidget extends StatelessWidget {
  final List<Medicine> items;
  const MedicineTableWidget({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    return DataTable(
      columns: const [
        DataColumn(label: Text('Name')),
        DataColumn(label: Text('Time')),
      ],
      rows: items
          .map((m) => DataRow(cells: [DataCell(Text(m.name)), DataCell(Text(m.timeOfDay))]))
          .toList(),
    );
  }
}