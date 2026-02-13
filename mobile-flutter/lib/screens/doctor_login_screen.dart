import 'package:dastern_mobile/l10n/app_localizations.dart';
import 'package:dastern_mobile/models/user/user.dart';
import 'package:dastern_mobile/screens/doctor_screen.dart';
import 'package:dastern_mobile/services/auth_service_login.dart';
import 'package:dastern_mobile/widgets/auth_background.dart';
import 'package:dastern_mobile/widgets/bottom_round_container.dart';
import 'package:dastern_mobile/widgets/custom_input_field.dart';
import 'package:dastern_mobile/widgets/hospital_logo.dart';
import 'package:dastern_mobile/widgets/label.dart';
import 'package:dastern_mobile/widgets/primary_button.dart';
import 'package:flutter/material.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final phoneNumberController = TextEditingController();
  final passwordController = TextEditingController();
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();

  String errorMessage = "";
  bool isLoading = false;

  Future<void> handleLogin() async {
    setState(() {
      isLoading = true;
    });

    final phone = phoneNumberController.text.trim();
    final password = passwordController.text.trim();
    final firstName = firstNameController.text.trim();
    final lastName = lastNameController.text.trim();

    // Simple validation - just check fields are not empty
    if (phone.isEmpty ||
        password.isEmpty ||
        firstName.isEmpty ||
        lastName.isEmpty) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please fill all fields")),
      );
      return;
    }

    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      isLoading = false;
    });

    // Navigate to doctor screen
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => const DoctorScreen(),
      ),
    );
  }

  @override
  void dispose() {
    phoneNumberController.dispose();
    passwordController.dispose();
    firstNameController.dispose();
    lastNameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: AuthBackground(
        logo: const HospitalLogo(
          radius: 24,
          name: 'DasTern',
          textStyle: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
            shadows: [
              Shadow(
                blurRadius: 4,
                color: Colors.black26,
                offset: Offset(1, 1),
              ),
            ],
          ),
        ),
        child: Align(
          alignment: Alignment.bottomCenter,
          child: BottomRoundContainer(
            backgroundColor: Colors.black.withOpacity(0.5),
            padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 18),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: Text(
                        AppLocalizations.of(context)?.yourAccount ??
                            'គណនីរបស់​អ្នក',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color.fromARGB(221, 255, 255, 255),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // FIRST NAME
                  Label('ឈ្មោះ'),
                  CustomInputField(
                    controller: firstNameController,
                    hint: 'សូមបំពេញឈ្មោះដំបូង',
                  ),

                  const SizedBox(height: 12),

                  // LAST NAME
                  Label('នាម'),
                  CustomInputField(
                    controller: lastNameController,
                    hint: 'សូមបំពេញឈ្មោះកំរាលត្រកូល',
                  ),

                  const SizedBox(height: 16),

                  // PHONE NUMBER
                  Label(
                    AppLocalizations.of(context)?.phoneNumber ?? 'លេខទូរស័ព្ទ',
                  ),
                  CustomInputField(
                    controller: phoneNumberController,
                    hint: AppLocalizations.of(context)?.fillPhoneNumber ??
                        'សូមបំពេញលេខទូរស័ព្ទរបស់អ្នក',
                  ),

                  // PASSWORD
                  Label(
                    AppLocalizations.of(context)?.password ?? 'លេខកូខសម្ងាត់',
                  ),
                  CustomInputField(
                    controller: passwordController,
                    obscureText: true,
                    hint: AppLocalizations.of(context)?.fillPassword ??
                        'សូមបំពេញលេខកូខសម្ងាត់របស់អ្នក',
                  ),

                  // ERROR MESSAGE
                  if (errorMessage.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Text(
                        errorMessage,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),

                  // LOGIN BUTTON
                  PrimaryButton(
                    text: isLoading
                        ? "Loading..."
                        : (AppLocalizations.of(context)?.continueText ??
                            "Login"),
                    onPressed: isLoading ? null : handleLogin,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
