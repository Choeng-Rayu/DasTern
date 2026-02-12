import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
<<<<<<< HEAD
import 'providers/scan_provider.dart';
import 'ui/theme/app_theme.dart';
import 'ui/screens/home/home_view.dart';
=======

import 'providers/processing_provider.dart';
import 'ui/screens/home_screen.dart';
import 'ui/screens/ocr_result_screen.dart';
import 'ui/screens/ocr_preview_screen.dart';
import 'ui/screens/ai_enhanced_preview_screen.dart';
import 'ui/screens/edit_prescription_screen.dart';
import 'ui/screens/final_preview_screen.dart';
import 'ui/screens/ai_result_screen.dart';
import 'ui/screens/saved_prescriptions_screen.dart';
import 'models/medication.dart';

import 'providers/scan_provider.dart';
import 'ui/theme/app_theme.dart';
import 'ui/screens/home/home_view.dart';

>>>>>>> c04fb50ce3d62100ad607cc395b368e4045989f9

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
<<<<<<< HEAD
  const MyApp({super.key});
=======
  const MyApp({Key? key}) : super(key: key);
>>>>>>> c04fb50ce3d62100ad607cc395b368e4045989f9

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
<<<<<<< HEAD
=======

        ChangeNotifierProvider(
          create: (_) => OCRProvider(),
        ),
        ChangeNotifierProvider(
          create: (_) => AIProvider(),
        ),
      ],
      child: MaterialApp(
        title: 'Prescription OCR Scanner',
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.light,
          ),
          appBarTheme: AppBarTheme(
            elevation: 0,
            backgroundColor: Colors.blue.shade700,
            foregroundColor: Colors.white,
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
          inputDecorationTheme: InputDecorationTheme(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
          ),
        ),
        darkTheme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.dark,
          ),
          appBarTheme: AppBarTheme(
            elevation: 0,
            backgroundColor: Colors.blue.shade900,
            foregroundColor: Colors.white,
          ),
        ),
        themeMode: ThemeMode.light,
        home: const HomeScreen(),
        routes: {
          '/home': (context) => const HomeScreen(),
          '/ocr-result': (context) {
            final imagePath =
                ModalRoute.of(context)?.settings.arguments as String?;
            return OCRResultScreen(
              imagePath: imagePath ?? '',
            );
          },
          '/ocr-preview': (context) => const OCRPreviewScreen(),
          '/ai-processing': (context) => const AIEnhancedPreviewScreen(),
          '/ai-result': (context) => const AIResultScreen(),
          '/edit-prescription': (context) {
            final medications = ModalRoute.of(context)?.settings.arguments
                as List<MedicationInfo>?;
            return EditPrescriptionScreen(initialMedications: medications);
          },
          '/final-preview': (context) {
            final medications = ModalRoute.of(context)?.settings.arguments
                as List<MedicationInfo>?;
            return FinalPreviewScreen(medications: medications);
          },
          '/saved-prescriptions': (context) =>
              const SavedPrescriptionsScreen(),
        },

>>>>>>> c04fb50ce3d62100ad607cc395b368e4045989f9
        ChangeNotifierProvider(create: (_) => ScanProvider()),
      ],
      child: MaterialApp(
        title: 'Prescription OCR',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        home: const HomeView(),
<<<<<<< HEAD
=======

>>>>>>> c04fb50ce3d62100ad607cc395b368e4045989f9
      ),
    );
  }
}
