import 'package:flutter/material.dart';
import '../widgets/hospital_logo.dart';
import '../widgets/bottom_round_container.dart';
import '../widgets/primary_button.dart';
import '../widgets/auth_background.dart';
import '../widgets/label.dart';
import '../widgets/custom_input_field.dart';

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
            backgroundColor: Colors.black.withOpacity(0.8),
            padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 18),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.only(bottom: 12.0),
                      child: Text(
                        'បញ្ចូលគណនីថ្មី',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color.fromARGB(221, 255, 255, 255),
                        ),
                      ),
                    ),
                  ),
                  const Label('សាមញ្ញឈ្មោះ'),
                  const CustomInputField(hint: 'សូមបញ្ចូលឈ្មោះរបស់អ្នក'),
                  const Label('អាសយដ្ឋាន'),
                  const CustomInputField(hint: 'សូមបញ្ចូលអាសយដ្ឋានរបស់អ្នក'),
                  const Label('ភេទ'),
                  const CustomInputField(hint: 'សូមបញ្ចូលភេទរបស់អ្នក'),
                  const Label('ថ្ងៃ ខែ ឆ្នាំ កំណើត'),
                  const Row(
                    children: [
                      Expanded(
                        child: CustomInputField(hint: 'ថ្ងៃ', maxLength: 2),
                      ),
                      SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(hint: 'ខែ', maxLength: 2),
                      ),
                      SizedBox(width: 8),
                      Expanded(
                        child: CustomInputField(hint: 'ឆ្នាំ', maxLength: 4),
                      ),
                    ],
                  ),
                  const Label('លេខទូរស័ព្ទ/អ៊ីមែល'),
                  const CustomInputField(
                      hint: 'សូមបញ្ចូលលេខទូរស័ព្ទ/អ៊ីមែលរបស់អ្នក'),
                  const SizedBox(height: 18),
                  PrimaryButton(
                    text: 'បញ្ចូល',
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
                      child: const Text(
                        'ចូលដោយគណនីមានរួច',
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
}
