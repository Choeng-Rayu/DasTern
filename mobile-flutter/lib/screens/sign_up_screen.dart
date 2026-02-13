import 'package:dastern_mobile/l10n/app_localizations.dart';
import 'package:dastern_mobile/screens/sign_up_detail_screen.dart';
import 'package:flutter/material.dart';
import '../widgets/header_widgets.dart';
import '../widgets/bottom_round_container.dart';
import '../widgets/primary_button.dart';
import '../widgets/auth_background.dart';
import '../widgets/label.dart';
import '../widgets/custom_input_field.dart';
import 'tab/main_navigation.dart';

class SignupScreen extends StatelessWidget {
  const SignupScreen({Key? key}) : super(key: key);

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
                        AppLocalizations.of(context)?.createNewAccount ??
                            'បង្កើតគណនីថ្មី',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color.fromARGB(221, 255, 255, 255),
                        ),
                      ),
                    ),
                  ),
                  Label(AppLocalizations.of(context)?.lastName ?? 'នាមត្រកូល'),
                  CustomInputField(
                      hint: AppLocalizations.of(context)?.fillLastName ??
                          'សូមបំពេញនាមត្រកូលរបស់អ្នក'),
                  Label(AppLocalizations.of(context)?.firstName ?? 'នាមខ្លួន'),
                  CustomInputField(
                      hint: AppLocalizations.of(context)?.fillFirstName ??
                          'សូមបំពេញនាមខ្លួនរបស់អ្នក'),
                  Label(AppLocalizations.of(context)?.gender ?? 'ភេទ'),
                  CustomInputField(
                      hint: AppLocalizations.of(context)?.fillGender ??
                          'សូមបំពេញភេទរបស់អ្នក'),
                  Label(AppLocalizations.of(context)?.dateOfBirth ??
                      'ថ្ងៃ ខែ ឆ្នាំ កំណើត'),
                  Row(
                    children: [
                      Expanded(
                        child: CustomInputField(
                            hint: AppLocalizations.of(context)?.day ?? 'ថ្ងៃទី',
                            maxLength: 2),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(
                            hint: AppLocalizations.of(context)?.month ?? 'ខែ',
                            maxLength: 2),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(
                            hint: AppLocalizations.of(context)?.year ?? 'ឆ្នាំ',
                            maxLength: 4),
                      ),
                    ],
                  ),
                  Label(AppLocalizations.of(context)?.idCardNumber ??
                      'លេខអត្តសញ្ញាណប័ណ្ណ'),
                  CustomInputField(
                      hint: AppLocalizations.of(context)?.fillIdCardNumber ??
                          'សូមបំពេញលេខអត្តសញ្ញាណប័ណ្ណរបស់អ្នក'),
                  const SizedBox(height: 18),
                  PrimaryButton(
                    text: AppLocalizations.of(context)?.continueText ?? 'បន្ត',
                    onPressed: () {
                      // Navigator.push(
                      //   context,
                      //   MaterialPageRoute(
                      //     builder:(context) => const SignupDetailScreen(),
                      //   ),
                      // );
                    },
                  ),
                  const SizedBox(height: 12),
                  Center(
                    child: TextButton(
                      onPressed: () {},
                      child: Text(
                        AppLocalizations.of(context)?.alreadyCreatedAccount ??
                            'បានបង្កើតគណនីពីមុន',
                        style:
                            const TextStyle(fontSize: 15, color: Colors.blue),
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
}
