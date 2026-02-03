import 'package:flutter/material.dart';
import '../../widgets/custom_button.dart';
import '../scan/scan_view.dart';

class HomeView extends StatelessWidget {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Prescription Reminder'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.medication_liquid,
                size: 80,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(height: 32),
              Text(
                'Add Your Prescription',
                style: Theme.of(context).textTheme.headlineMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Text(
                'Scan your prescription or add medicines manually to get started.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              SizedBox(
                width: double.infinity,
                child: CustomButton(
                  text: 'Scan Prescription',
                  icon: Icons.camera_alt,
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ScanView()),
                    );
                  },
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: CustomButton(
                  text: 'Create Manually',
                  icon: Icons.edit_note,
                  isOutlined: true,
                  onPressed: () {
                    // Logic for manual creation would go here
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Manual creation not implemented yet')),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
