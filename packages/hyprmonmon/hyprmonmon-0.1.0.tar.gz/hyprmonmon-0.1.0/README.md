# hyprmonmon

Manage, remember and monitor different display layouts for hyprland.

Install `click`, `hyprpy` and `nwg-displays`.

Add the following autostart to `hyprland.conf`:
```
exec-once = hyprmonmon watch
```

To configure the current layout using `nwg-displays`, run: `hyprmonmon
config`.

To re-apply the current layout use `hyprmonmon apply`.

By default, `hyprmonmon config` will ask `nwg-displays` to configure 10
workspaces, to use a different amount of workspaces, use `hyprmonmon config
--num_ws 5`.

`hyprmonmon` will save the display / workspace layout in config files based
on the fingerprint of your current setup. The fingerprint is based on a hash
of the name and description of each active display.

If a new display is connected, `hyprmonmon watch` will automatically try to
load the config for the new fingerprint.

The per-fingerprint config files can be found in `~/.config/hyprmonmon`.
