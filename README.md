# On Battery Notifier

A lightweight cross-platform system tray app that reminds you when your device is running on battery power instead of AC power.

## Features

* System tray integration with configurable icon
* Battery status monitoring in the background
* Customizable reminder intervals
* Optional delayed notifications with progressive intervals
* Simple GUI dialogs for settings
* Persistent configuration saved locally
* Build support for:
  * PyInstaller
  * Nuitka
  * One-file or standalone binaries
* Linux and Windows dependency automation

## How It Works

When your system is unplugged from AC power:

* A tray notification alerts you
* Reminders repeat at your chosen interval
* Optional delay mode increases time between repeated alerts

## Tray Menu Options

* **Set reminder interval**
* **Enable/disable delayed notifications**
* **Exit application**

## Configuration

Settings are stored in:

```bash
~/.config/On Battery Notifier.json
```

Saved preferences include:

* Initial reminder interval
* Delay enabled/disabled
* Delay multiplier

## Build Options

### PyInstaller

```bash
python build.py --pyinst
```

### Nuitka

```bash
python build.py --nuitka
```

### One-file binary

```bash
python build.py --pyinst --onefile
```

### Install dependencies only

```bash
python build.py --deps
```

## Dependencies

* Python 3
* Poetry
* pystray
* Pillow
* easygui
* PyInstaller or Nuitka

## Supported Platforms

* Linux
* Windows

## Use Cases

* Laptop battery conservation
* Prevent accidental battery drain
* Workstation power awareness
* Long-running unplugged sessions

## License

MIT
