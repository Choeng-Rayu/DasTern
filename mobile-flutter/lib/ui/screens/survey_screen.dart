import 'package:dastern_mobile/models/survey.dart';
import 'package:flutter/material.dart';
// import '../../domain/model/survey.dart';

class SurveyFlowScreen extends StatefulWidget {
  final List<Survey> surveys;
  final void Function(List<int> answers)? onComplete;

  const SurveyFlowScreen({Key? key, required this.surveys, this.onComplete})
    : super(key: key);

  @override
  State<SurveyFlowScreen> createState() => _SurveyFlowScreenState();
}

class _SurveyFlowScreenState extends State<SurveyFlowScreen> {
  int currentIndex = 0;
  List<int?> selectedAnswers = [];

  @override
  void initState() {
    super.initState();
    selectedAnswers = List<int?>.filled(widget.surveys.length, null);
  }

  void _onOptionSelected(int index) {
    setState(() {
      selectedAnswers[currentIndex] = index;
    });
  }

  void _onNext() {
    if (currentIndex < widget.surveys.length - 1) {
      setState(() {
        currentIndex++;
      });
    } else {
      // Complete
      if (widget.onComplete != null) {
        widget.onComplete!(selectedAnswers.cast<int>());
      } else {
        Navigator.of(context).pop();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final survey = widget.surveys[currentIndex];
    final progress = (currentIndex + 1) / widget.surveys.length;
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.black),
          onPressed: () {
            if (currentIndex > 0) {
              setState(() => currentIndex--);
            } else {
              Navigator.of(context).maybePop();
            }
          },
        ),
        title: const Text(
          'សំណួរ',
          style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Icon(Icons.wb_sunny, color: Colors.amber.shade700),
          ),
        ],
        toolbarHeight: 56,
      ),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
              child: LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.grey.shade300,
                color: Colors.blue,
                minHeight: 6,
              ),
            ),
            Expanded(
              child: Center(
                child: Container(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 24,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(28),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.07),
                        blurRadius: 16,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        survey.question,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(height: 18),
                      ...List.generate(survey.options.length, (i) {
                        return Column(
                          children: [
                            RadioListTile<int>(
                              value: i,
                              groupValue: selectedAnswers[currentIndex],
                              onChanged: (val) {
                                if (val != null) _onOptionSelected(val);
                              },
                              title: Text(
                                survey.options[i],
                                style: const TextStyle(fontSize: 16),
                              ),
                              contentPadding: EdgeInsets.zero,
                            ),
                            if (i != survey.options.length - 1)
                              const Divider(
                                height: 0,
                                thickness: 1,
                                color: Color(0xFFF0F0F0),
                              ),
                          ],
                        );
                      }),
                      const SizedBox(height: 24),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: selectedAnswers[currentIndex] != null
                              ? _onNext
                              : null,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: const Text(
                            'បន្ត',
                            style: TextStyle(fontSize: 16, color: Colors.white),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
