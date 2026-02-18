import 'package:flutter/material.dart';
import '../models/family_member.dart';

class FamilyMemberListCard extends StatelessWidget {
  final FamilyMember member;

  const FamilyMemberListCard({super.key, required this.member});

  @override
  Widget build(BuildContext context) {
    final bool isPending = member.hasPendingPrescription;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      child: Row(
        children: [
          // Avatar
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.person, color: Colors.blue, size: 28),
          ),
          const SizedBox(width: 12),
          // Name and status
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  member.name,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  'រោគសញ្ញា: ${member.lastActivity ?? ''}',
                  style: TextStyle(
                    fontSize: 12,
                    color: isPending ? Colors.red : Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
          // Status badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: isPending ? Colors.red.shade50 : Colors.blue.shade50,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: isPending ? Colors.red.shade200 : Colors.blue.shade200,
              ),
            ),
            child: Text(
              isPending ? 'មិនទាន់ទទួលថ្នាំ' : 'ធម្មតា',
              style: TextStyle(
                color: isPending ? Colors.red : Colors.blue,
                fontWeight: FontWeight.w600,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }
}