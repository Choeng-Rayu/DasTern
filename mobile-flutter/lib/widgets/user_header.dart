import 'package:flutter/material.dart';
import 'package:dastern_mobile/widgets/hospital_logo.dart';

class UserHeader extends StatelessWidget {
  final String userName;
  final String userRole;
  final double height;

  const UserHeader({
    Key? key,
    required this.userName,
    required this.userRole,
    this.height = 250,
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
      // child: Container(
      //   padding: const EdgeInsets.all(16.0),
      //   decoration: BoxDecoration(
      //     // Dark overlay to make text readable
      //     // color: Colors.black.withOpacity(0.3),
      //   ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // Hospital Logo at the top
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: HospitalLogo(
              radius: 30,
              name: 'DasTern',
              textStyle: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
          const Spacer(),
          // Decorative diagonal line (matching Figma)
          Padding(
            padding: const EdgeInsets.only(left: 16.0, right: 80.0),
            child: Stack(
              children: [
                // Main white line
                Container(
                  height: 3,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.9),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.white.withOpacity(0.5),
                        blurRadius: 8,
                        // spreadRadius: 1,
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
}
