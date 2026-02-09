import 'package:flutter/material.dart';
// import 'package:ui_for_capstone/data/survey_data.dart';
// import 'package:ui_for_capstone/ui/screen/survey_flow_screen.dart';
import '../widgets/header_widgets.dart';
import '../widgets/bottom_round_container.dart';
import '../widgets/primary_button.dart';
import '../widgets/auth_background.dart';
import '../widgets/label.dart';
import '../widgets/custom_input_field.dart';

class SignupDetailScreen extends StatelessWidget {
  const SignupDetailScreen({Key? key}) : super(key: key);

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
            backgroundColor: const Color(0xFF1E1E1E),
            padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 18),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.arrow_back_ios, color: Colors.white, size: 20),
                      SizedBox(width: 8),
                      Text(
                        'បញ្ចូលពត៌មាន',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Label('លេខសំគាល់'),
                  const CustomInputField(hint: 'សូមបញ្ចូលលេខសំគាល់របស់អ្នក'),
                  const Label('លេខសំគាល់សំខាន់'),
                  const CustomInputField(
                      hint: 'សូមបញ្ចូលលេខសំគាល់សំខាន់របស់អ្នក'),
                  const Label('អាសយដ្ឋានបច្ចុប្បន្ន'),
                  const CustomInputField(
                    hint: 'សូមបញ្ចូលអាសយដ្ឋានបច្ចុប្បន្នរបស់អ្នក',
                  ),
                  const Label('លេខកូដចាស់'),
                  const Row(
                    children: [
                      Expanded(
                        child: CustomInputField(hint: '១', maxLength: 1),
                      ),
                      SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(hint: '២', maxLength: 1),
                      ),
                      SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(hint: '៣', maxLength: 1),
                      ),
                      SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(hint: '៤', maxLength: 1),
                      ),
                    ],
                  ),
                  const Label('លេខកូដថ្មី'),
                  const Row(
                    children: [
                      Expanded(
                        child: CustomInputField(hint: '១', maxLength: 1),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(hint: '២', maxLength: 1),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(hint: '៣', maxLength: 1),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(hint: '៤', maxLength: 1),
                      ),
                    ],
                  ),
                  const CustomInputField(
                    hint: 'សូមបញ្ចូលពត៌មាន និងអត្ថបទបន្ថែមប្រសិនបើមាន',
                  ),
                  const Label('អាសយដ្ឋាន'),
                  const CustomInputField(hint: 'អាសយដ្ឋាន'),
                  const SizedBox(height: 18),
                  PrimaryButton(
                    text: 'បញ្ចូល',
                    onPressed: () {
                      // Navigator.push(
                      //   context,
                      //   MaterialPageRoute(
                      //     builder: (context) =>
                      //         SurveyFlowScreen(surveys: surveys),
                      //   ),
                      // );
                    },
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
