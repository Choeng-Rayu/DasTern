import 'package:flutter/material.dart';

class HospitalLogo extends StatelessWidget {
  final double radius;
  final String name;
  final TextStyle? textStyle;
  final double spacing;

  const HospitalLogo({
    Key? key,
    this.radius = 28,
    this.name = 'DasTern',
    this.textStyle,
    this.spacing = 8,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: radius * 2,
          height: radius * 2,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white,
            border: Border.all(
              color: Colors.blue.shade300,
              width: 3,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.15),
                blurRadius: 6,
                offset: Offset(0, 2),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(6.0),
            child: ClipOval(
              child: Image.asset(
                'assets/images/doctor.png',
                width: (radius - 6) * 2,
                height: (radius - 6) * 2,
                fit: BoxFit.contain,
              ),
            ),
          ),
        ),
        SizedBox(width: spacing),
        Text(
          name,
          style: textStyle ??
              const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
        ),
      ],
    );
  }
}
