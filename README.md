# Home Assistant Integration - GoXLR Utility

[GoXLR Utility](https://github.com/GoXLR-on-Linux/goxlr-utility) integration for [Home Assistant](https://www.home-assistant.io/).

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=timmo001&repository=homeassistant-integration-goxlr-utility&category=integration)

This integration is available in the [Home Assistant Community Store](https://hacs.xyz/).

## Setup and Configuration

- You currently need to add ` --http-bind-address 0.0.0.0` to the `goxlr-daemon` command in your respective OS. See [here](https://github.com/GoXLR-on-Linux/goxlr-utility/issues/64) for progress on this being added to the UI.
    - For Windows, the easiest way is to edit the shortcut in `%appdata%\Microsoft\Windows\Start Menu\Programs\Startup` and add the argument to the end of the `Target` field.
- Add to Home Assistant using the UI
