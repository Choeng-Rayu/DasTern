import 'package:dastern_mobile/services/auth_service.dart';
import 'package:dastern_mobile/widgets/auth_background.dart';
import 'package:dastern_mobile/widgets/bottom_round_container.dart';
import 'package:dastern_mobile/widgets/custom_input_field.dart';
import 'package:dastern_mobile/widgets/header_widgets.dart';
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

  String errorMessage = "";
  bool isLoading = false;

  Future<void> handleLogin() async {
    setState(() {
      isLoading = true;
      errorMessage = "";
    });

    final phone = phoneNumberController.text.trim();
    final password = passwordController.text.trim();

    // validation
    if (phone.isEmpty || password.isEmpty) {
      setState(() {
        isLoading = false;
        errorMessage = "Please fill phone number and password.";
      });
      return;
    }

    // Initialize AuthService with baseUrl (adjust as needed)
    final authService = AuthService(baseUrl: 'http://localhost:8000');
    final token = await authService.login(phone, password);

    setState(() {
      isLoading = false;
    });

    if (token != null) {
      print("Login success token: $token");

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Login Successful")),
        );

        // Navigate to home screen (or doctor screen if available)
        Navigator.pushReplacementNamed(context, '/home');
      }
    } else {
      setState(() {
        errorMessage = "Login failed. Please check phone number or password.";
      });
    }
  }

  @override
  void dispose() {
    phoneNumberController.dispose();
    passwordController.dispose();
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
                        'Your Account',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color.fromARGB(221, 255, 255, 255),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),
                  // PHONE NUMBER
                  const Label('Phone Number'),
                  CustomInputField(
                    controller: phoneNumberController,
                    hint: 'Enter your phone number',
                  ),

                  // PASSWORD
                  const Label('Password'),
                  CustomInputField(
                    controller: passwordController,
                    obscureText: true,
                    hint: 'Enter your password',
                  ),

                  const SizedBox(height: 18),

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
                    text: isLoading ? "Loading..." : "Login",
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
