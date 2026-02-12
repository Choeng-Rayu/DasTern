import 'package:dastern_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import '../widgets/header_widgets.dart';
import '../widgets/bottom_round_container.dart';
import '../widgets/primary_button.dart';
import '../widgets/auth_background.dart';
import '../widgets/label.dart';
import '../widgets/custom_input_field.dart';
import 'tab/main_navigation.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

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
                        AppLocalizations.of(context)?.login ?? 'ចូល',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color.fromARGB(221, 255, 255, 255),
                        ),
                      ),
                    ),
                  ),
                  Label('អ៊ីមែល / Email'),
                  CustomInputField(
                    controller: _emailController,
                    hint: 'user@example.com',
                  ),
                  Label('ពាក្យសម្ងាត់ / Password'),
                  CustomInputField(
                    controller: _passwordController,
                    hint: 'Enter password',
                    obscureText: true,
                  ),
                  const SizedBox(height: 24),
                  PrimaryButton(
                    text: AppLocalizations.of(context)?.login ?? 'ចូល',
                    onPressed: () {
                      // Simple demo - just navigate to home
                      Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const MainNavigation(),
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 12),
                  Center(
                    child: TextButton(
                      onPressed: () {
                        Navigator.pop(context);
                      },
                      child: const Text(
                        'Back to Welcome',
                        style: TextStyle(fontSize: 15, color: Colors.blue),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}
