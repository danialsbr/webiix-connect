import 'package:flutter/material.dart';
import 'package:flutter_hbb/common.dart';
import 'package:flutter_hbb/desktop/pages/desktop_home_page.dart';
import 'package:flutter_hbb/desktop/pages/desktop_setting_page.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:get/get.dart';

/// Webiix Connect dark glass app shell (WEBIIX_CONNECT_REDESIGN / Dark UI mockup).
enum WebiixNav { home, devices, settings, about }

class WebiixNavController extends GetxController {
  final nav = WebiixNav.home.obs;

  void go(WebiixNav value) => nav.value = value;

  void openSettings({SettingsTabKey tab = SettingsTabKey.general}) {
    pendingSettingsTab = tab;
    nav.value = WebiixNav.settings;
  }

  SettingsTabKey pendingSettingsTab = SettingsTabKey.general;
}

class WebiixAppShell extends StatefulWidget {
  const WebiixAppShell({super.key});

  @override
  State<WebiixAppShell> createState() => _WebiixAppShellState();
}

class _WebiixAppShellState extends State<WebiixAppShell> {
  late final WebiixNavController _nav;

  @override
  void initState() {
    super.initState();
    if (Get.isRegistered<WebiixNavController>()) {
      _nav = Get.find<WebiixNavController>();
    } else {
      _nav = Get.put(WebiixNavController());
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bg = isDark ? const Color(0xFF080F20) : const Color(0xFFF6F8FC);
    final sidebar = isDark ? const Color(0xFF0D1930) : Colors.white;
    final border = isDark ? const Color(0xFF31425D) : const Color(0xFFDCE4EF);

    return Scaffold(
      backgroundColor: bg,
      body: Row(
        children: [
          Obx(() => _Sidebar(
                selected: _nav.nav.value,
                background: sidebar,
                border: border,
                onSelect: _nav.go,
              )),
          Expanded(child: Obx(() => _body(_nav.nav.value))),
        ],
      ),
    );
  }

  Widget _body(WebiixNav nav) {
    switch (nav) {
      case WebiixNav.home:
      case WebiixNav.devices:
        return DesktopHomePage(
          key: ValueKey('webiix-home-${nav.name}'),
          webiixDevicesOnly: nav == WebiixNav.devices,
        );
      case WebiixNav.settings:
        return DesktopSettingPage(
          key: ValueKey('webiix-settings-${_nav.pendingSettingsTab.name}'),
          initialTabkey: _nav.pendingSettingsTab,
        );
      case WebiixNav.about:
        return DesktopSettingPage(
          key: const ValueKey('webiix-about'),
          initialTabkey: SettingsTabKey.about,
        );
    }
  }
}

class _Sidebar extends StatelessWidget {
  const _Sidebar({
    required this.selected,
    required this.background,
    required this.border,
    required this.onSelect,
  });

  final WebiixNav selected;
  final Color background;
  final Color border;
  final ValueChanged<WebiixNav> onSelect;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final idle = isDark ? const Color(0xFFB6C5DC) : const Color(0xFF52637B);
    final brand = isDark ? MyTheme.accentDark : MyTheme.accent;

    return Container(
      width: 88,
      decoration: BoxDecoration(
        color: background.withOpacity(isDark ? 0.92 : 1),
        border: Border(right: BorderSide(color: border.withOpacity(0.7))),
      ),
      child: Column(
        children: [
          const SizedBox(height: 18),
          SvgPicture.asset(
            'assets/icon.svg',
            width: 28,
            height: 28,
            colorFilter: ColorFilter.mode(brand, BlendMode.srcIn),
          ),
          const SizedBox(height: 6),
          Text(
            'Webiix',
            style: TextStyle(
              color: isDark ? Colors.white : brand,
              fontSize: 11,
              fontWeight: FontWeight.w700,
              height: 1.1,
            ),
          ),
          Text(
            'connect',
            style: TextStyle(
              color: idle,
              fontSize: 10,
              fontWeight: FontWeight.w500,
              height: 1.1,
            ),
          ),
          const SizedBox(height: 28),
          _NavBtn(
            icon: Icons.home_rounded,
            label: 'Home',
            selected: selected == WebiixNav.home,
            brand: brand,
            idle: idle,
            onTap: () => onSelect(WebiixNav.home),
          ),
          _NavBtn(
            icon: Icons.devices_rounded,
            label: 'Devices',
            selected: selected == WebiixNav.devices,
            brand: brand,
            idle: idle,
            onTap: () => onSelect(WebiixNav.devices),
          ),
          _NavBtn(
            icon: Icons.settings_rounded,
            label: 'Settings',
            selected: selected == WebiixNav.settings,
            brand: brand,
            idle: idle,
            onTap: () => onSelect(WebiixNav.settings),
          ),
          _NavBtn(
            icon: Icons.info_outline_rounded,
            label: 'About',
            selected: selected == WebiixNav.about,
            brand: brand,
            idle: idle,
            onTap: () => onSelect(WebiixNav.about),
          ),
          const Spacer(),
          Container(
            margin: const EdgeInsets.only(bottom: 16),
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [brand, brand.withOpacity(0.55)],
              ),
              border: Border.all(color: brand.withOpacity(0.5)),
            ),
            alignment: Alignment.center,
            child: const Text(
              'W',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w700,
                fontSize: 16,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _NavBtn extends StatelessWidget {
  const _NavBtn({
    required this.icon,
    required this.label,
    required this.selected,
    required this.brand,
    required this.idle,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool selected;
  final Color brand;
  final Color idle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
      child: Material(
        color: selected ? brand : Colors.transparent,
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(14),
          child: SizedBox(
            width: double.infinity,
            height: 58,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 22, color: selected ? Colors.white : idle),
                const SizedBox(height: 4),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: selected ? Colors.white : idle,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Frosted card used on the Webiix home dashboard.
class WebiixGlassCard extends StatelessWidget {
  const WebiixGlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(20),
    this.height,
  });

  final Widget child;
  final EdgeInsets padding;
  final double? height;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(MyTheme.radiusCard),
        color: isDark
            ? const Color(0xFF14233D).withOpacity(0.72)
            : Colors.white.withOpacity(0.92),
        border: Border.all(
          color: isDark
              ? MyTheme.accentDark.withOpacity(0.35)
              : MyTheme.border,
        ),
        boxShadow: [
          BoxShadow(
            color: (isDark ? Colors.black : const Color(0xFF15233B))
                .withOpacity(0.18),
            blurRadius: 24,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      padding: padding,
      child: child,
    );
  }
}
