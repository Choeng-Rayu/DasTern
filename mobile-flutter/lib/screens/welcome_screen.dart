import 'package:dastern_mobile/l10n/app_localizations.dart';
import 'package:dastern_mobile/screens/doctor_screen.dart';
import 'package:dastern_mobile/screens/login_screen.dart';
import 'package:dastern_mobile/screens/sign_up_screen.dart';
import 'package:dastern_mobile/widgets/bottom_round_container.dart';
import 'package:flutter/material.dart';
import '../widgets/hospital_logo.dart';
import '../widgets/primary_button.dart';
import '../widgets/background_welcome.dart';

class WelcomeScreen extends StatelessWidget {
  final void Function(Locale)? onLocaleChange;
  const WelcomeScreen({Key? key, this.onLocaleChange}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: BackgroundWelcome(
        child: Stack(
          children: [
            // Top row with logo and language switcher
            SafeArea(
              child: Padding(
                padding:
                    const EdgeInsets.only(top: 16.0, left: 16.0, right: 12.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    HospitalLogo(
                      radius: 28,
                      name: AppLocalizations.of(context)?.appTitle ?? 'DasTern',
                      textStyle: const TextStyle(
                        fontSize: 22,
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
                    DropdownButton<Locale>(
                      underline: const SizedBox(),
                      style: const TextStyle(
                          color: Color.fromARGB(255, 45, 45, 45)),
                      icon: const Icon(Icons.language,
                          color: Color.fromARGB(255, 0, 0, 0)),
                      value: Localizations.localeOf(context),
                      items: const [
                        DropdownMenuItem(
                            value: Locale('en'), child: Text('English')),
                        DropdownMenuItem(
                            value: Locale('km'), child: Text('ភាសាខ្មែរ')),
                      ],
                      onChanged: (locale) {
                        if (locale != null && onLocaleChange != null) {
                          onLocaleChange!(locale);
                        }
                      },
                    ),
                  ],
                ),
              ),
            ),
            // Centered doctor image and welcome message
            Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const SizedBox(height: 30),
                    Container(
                      width: 290,
                      height: 370,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(40),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.08),
                            blurRadius: 16,
                            offset: Offset(0, 6),
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(40),
                        child: Image.asset(
                          'assets/images/welcome_doctor_image.png',
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Text(
                      AppLocalizations.of(context)?.welcomeMessage ?? '',
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 8,
                            color: Colors.black38,
                            offset: Offset(1, 2),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            // Bottom full-width rounded container
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: BottomRoundContainer(
                padding:
                    const EdgeInsets.symmetric(vertical: 28, horizontal: 18),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const SizedBox(height: 30),
                    PrimaryButton(
                      text: AppLocalizations.of(context)?.createAccount ??
                          'Create an Account',
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const SignupScreen(),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 20),
                    PrimaryButton(
                      text: AppLocalizations.of(context)?.login ?? 'Login',
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const LoginScreen(),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 20),
                    TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: ( context) => const LoginScreen(),
                          ),
                        );
                      },
                      child: Text(
                        AppLocalizations.of(context)?.loginAsDoctor ??
                            'login as a Doctor',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.blueAccent,
                          // decoration: TextDecoration.underline,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
