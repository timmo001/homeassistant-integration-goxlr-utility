# Home Assistant Integration - GoXLR Utility

[GoXLR Utility](https://github.com/GoXLR-on-Linux/goxlr-utility) integration for [Home Assistant](https://www.home-assistant.io/) using the [goxlrutilityapi](https://github.com/timmo001/goxlr-utility-api-py) Python package. This is a third party application from [@GoXLR-on-Linux](https://github.com/GoXLR-on-Linux) that allows for control of the GoXLR on Linux, Mac and Windows.

> This integration does not connect to the official GoXLR application!

Be sure to check out the [GoXLR Utility](https://github.com/GoXLR-on-Linux/goxlr-utility) project for more information.

![Screenshot](https://user-images.githubusercontent.com/28114703/236408810-50061d16-7b16-4065-9b52-143b8e4a3ea6.png)

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=timmo001&repository=homeassistant-integration-goxlr-utility&category=integration)

This integration is available in the [Home Assistant Community Store](https://hacs.xyz/).

## Setup and Configuration

- ~~You currently need to add `--http-bind-address 0.0.0.0` to the `goxlr-daemon` command in your respective OS. See [here](https://github.com/GoXLR-on-Linux/goxlr-utility/issues/64) for progress on this being added to the UI. For Windows, the easiest way is to edit the shortcut in `%appdata%\Microsoft\Windows\Start Menu\Programs\Startup` and add the argument to the end of the `Target` field.~~ Enable `Allow UI network access` the the settings to allow remote access on the network
- Add to Home Assistant using the UI

## Features

### Binary Sensors

- Button Pressed
- Slider muted

### Sensors

- Volume

### Lights

- Accent
- Buttons (Inactive, Active)
- Faders (Bottom, Top)
