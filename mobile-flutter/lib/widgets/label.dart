import 'package:flutter/material.dart';

class Label extends StatelessWidget {
  final String text;
  const Label(this.text, {Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 8.0, bottom: 4.0),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w600,
          color: Color.fromARGB(221, 255, 255, 255),
        ),
      ),
    );
  }
}
