//! Webiix Connect baked-in defaults for the free self-hosted client.

use hbb_common::config::{
    self, DEFAULT_LOCAL_SETTINGS, DEFAULT_SETTINGS, WEBIXX_ID_SERVER, WEBIXX_KEY,
    WEBIXX_RELAY_SERVER,
};

/// Apply Webiix Connect branding and default relay configuration.
///
/// Sets the display name, seeds ID / Relay / Key defaults, and prefers a
/// white/light UI (matching https://webiix.co/) while still allowing Dark.
pub fn apply() {
    *config::APP_NAME.write().unwrap() = "Webiix Connect".to_owned();

    {
        let mut defaults = DEFAULT_SETTINGS.write().unwrap();
        defaults.insert(
            "custom-rendezvous-server".to_owned(),
            WEBIXX_ID_SERVER.to_owned(),
        );
        defaults.insert("relay-server".to_owned(), WEBIXX_RELAY_SERVER.to_owned());
        defaults.insert("key".to_owned(), WEBIXX_KEY.to_owned());
    }

    // Local UI defaults — light/white like the website; not overwritten so
    // Settings → Theme (Light / Dark / Follow System) still works.
    {
        let mut local = DEFAULT_LOCAL_SETTINGS.write().unwrap();
        local.insert("theme".to_owned(), "light".to_owned());
    }
}
