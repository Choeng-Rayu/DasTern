// import 'package:flutter/material.dart';
// import 'package:dastern_mobile/models/form_field_config.dart';

// class CustomForm extends StatelessWidget {
//   final List<FormFieldConfig> fields;
//   final VoidCallback onSubmit;

//   const CustomForm({
//     required this.fields,
//     required this.onSubmit,
//     super.key
//   });

//   @override
//   Widget build(BuildContext context) {
//     return Column(
//       children: [
//         ...fields.map((fields) => TextField(
//           controller: fields.controller,
//           decoration: InputDecoration(
//             labelText: fields.label,
//             hintText: fields.hint,
//           ),
//         )),
//         ElevatedButton(
//           onPressed: onSubmit,
//           child: Text('បញ្ជូន'),
//         ),
//       ],
//     );
//   }
// }
