import 'package:auto_size_text/auto_size_text.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../common.dart';

Widget getConnectionPageTitle(BuildContext context, bool isWeb) {
  final secondary = Theme.of(context).brightness == Brightness.dark
      ? MyTheme.textSecondaryDark
      : MyTheme.textSecondaryLight;
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        children: [
          Expanded(
            child: AutoSizeText(
              translate('Remote access'),
              maxLines: 1,
              style: Theme.of(context)
                  .textTheme
                  .titleLarge
                  ?.merge(const TextStyle(height: 1, fontSize: 24)),
            ),
          ),
          Tooltip(
            waitDuration: Duration(milliseconds: 300),
            message: translate(isWeb ? "web_id_input_tip" : "id_input_tip"),
            child: Icon(
              Icons.help_outline_outlined,
              size: 16,
              color: secondary,
            ),
          ),
        ],
      ),
      const SizedBox(height: 4),
      Text(
        translate('Connect to another device or share this desktop'),
        style: TextStyle(fontSize: 13, color: secondary, height: 1.3),
      ),
    ],
  ).marginOnly(right: 4);
}
