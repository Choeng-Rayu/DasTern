import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:ocr_ai_for_reminder/providers/scan_provider.dart';
import 'package:ocr_ai_for_reminder/models/prescription.dart'; // ProcessStatus

void main() {
  group('ScanProvider', () {
    late ScanProvider provider;

    setUp(() {
      provider = ScanProvider(); // We would inject mock repo here in real test
    });

    test('Initial state is correct', () {
      expect(provider.status, ProcessStatus.initial);
      expect(provider.imageFile, null);
      expect(provider.prescription, null);
    });

    // We can't easily test async process without mocking repository,
    // but we can test synchronous state changes if we had a MockRepository.
    // For now, this confirms the basic setup works.
    
    test('setImage updates state', () async {
      final file = File('test_image.jpg');
      await provider.setImage(file);
      expect(provider.imageFile, file);
      expect(provider.status, ProcessStatus.scanned);
    });
  });
}
