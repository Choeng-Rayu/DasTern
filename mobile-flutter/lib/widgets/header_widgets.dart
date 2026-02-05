import 'package:flutter/material.dart';

/// Hospital Logo Widget - Used in headers and various screens
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
          // width: radius * 9,
          // height: radius * 2,
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
            padding: const EdgeInsets.all(7.0),
            child: ClipOval(
              child: Image.asset(
                'assets/images/doctor.png',
                fit: BoxFit.contain,
                alignment: Alignment(0, 0.2),
              ),
            ),
          ),
        ),
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

/// User Header Widget - Combines hospital logo with user information
class UserHeader extends StatelessWidget {
  final String userName;
  final String userRole;
  final double height;
  final double logoRadius;
  final String hospitalName;

  const UserHeader({
    Key? key,
    required this.userName,
    required this.userRole,
    this.height = 250,
    this.logoRadius = 30,
    this.hospitalName = 'DasTern',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      width: double.infinity,
      decoration: const BoxDecoration(
        borderRadius: BorderRadius.all(Radius.circular(35)),
        image: DecorationImage(
          image: AssetImage('assets/images/background-welcome.jpg'),
          fit: BoxFit.cover,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // Hospital Logo at the top (integrated)
          Padding(
            padding:
                const EdgeInsets.fromLTRB(0.01, 50, 30, 19), // 👈 move DOWN
            child: _buildHospitalLogo(),
          ),
          const Spacer(),
          // Decorative diagonal line (matching Figma)
          Padding(
            padding: const EdgeInsets.only(left: 16.0, right: 80.0),
            child: Stack(
              children: [
                // Main white line
                Container(
                  height: 1,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.9),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.white.withOpacity(0.5),
                        blurRadius: 8,
                      ),
                    ],
                  ),
                ),
                // Extended line going to the right
                Positioned(
                  right: -60,
                  top: 10,
                  child: Container(
                    width: 1,
                    height: 3,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.white.withOpacity(0.9),
                          Colors.white.withOpacity(0.0),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // User Information at the bottom
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  userName,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  userRole,
                  style: const TextStyle(
                    fontSize: 18,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build hospital logo widget integrated into the header
  Widget _buildHospitalLogo() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: logoRadius * 4,
          height: logoRadius * 2,
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
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(6.0),
            child: ClipOval(
              child: Image.asset(
                'assets/images/doctor.png',
                fit: BoxFit.contain,
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          hospitalName,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }
}
