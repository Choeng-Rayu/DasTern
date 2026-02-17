
import 'package:dastern_mobile/models/survey.dart';
final List<Survey> surveys = [
  Survey(
    title: 'សំណួរពេលព្រឹក',
    question: 'តើអ្នកធ្វើអ្វីបំផុតនៅពេលព្រឹកនេះ?',
    options: [
      '6:00 AM- 7:00 AM ព្រឹក',
      '7:00 AM- 8:00 AM ព្រឹក',
      '8:00 AM- 9:00 AM ព្រឹក',
      '9:00 AM- 10:00 AM ព្រឹក',
    ],
  ),
  Survey(
    title: 'សំណួរពេលថ្ងៃ',
    question: 'តើអ្នកធ្វើអ្វីបំផុតនៅពេលថ្ងៃ?',
    options: [
      '12:00 PM- 1:00 PM មធ្យមថ្ងៃ',
      '1:00 PM- 2:00 PM មធ្យមថ្ងៃ',
      '2:00 PM- 3:00 PM មធ្យមថ្ងៃ',
      '4:00 PM- 5:00 PM មធ្យមថ្ងៃ',
    ],
  ),
  Survey(
    title: 'សំណួរពេលល្ងាច',
    question: 'តើអ្នកធ្វើអ្វីបំផុតនៅពេលល្ងាច?',
    options: [
      '12:00 PM- 1:00 PM ល្ងាច',
      '1:00 PM- 2:00 PM ល្ងាច',
      '2:00 PM- 3:00 PM ល្ងាច',
      '4:00 PM- 5:00 PM ល្ងាច',
    ],
  ),
];
