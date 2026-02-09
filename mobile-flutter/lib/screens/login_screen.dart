import 'package:dastern_mobile/l10n/app_localizations.dart';
import 'package:dastern_mobile/widgets/auth_background.dart';
import 'package:dastern_mobile/widgets/bottom_round_container.dart';
import 'package:dastern_mobile/widgets/hospital_logo.dart';
import 'package:flutter/material.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

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
            ]
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
                        AppLocalizations.of(context)?.createNewAccount ??
                            'គណនីថ្មី',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color.fromARGB(221, 255, 255, 255),
                        ),
                      ),
                    ),
                  )
                ],
              ),
            ),
            ),
        ),
      ),
    );
  }
}
