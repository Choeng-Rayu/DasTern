import 'package:flutter/material.dart';

class ScanScreen extends StatelessWidget {
  const ScanScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan (OCR)')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.camera_alt, size: 72),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // TODO: launch camera / pick image and run OCR
              },
              child: const Text('Start Scan'),
            ),
          ],
        ),
      ),
    );
  }
}