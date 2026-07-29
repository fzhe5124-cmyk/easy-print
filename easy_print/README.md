# Easy-Print — Blender 3D Printing Plugin

## Overview
A Blender 4.2+ addon for cutting 3D models and generating interlocking connectors (male/female) on cut surfaces for 3D printing assembly. Draw a line across the model to cut it, then generate matching connectors on both halves.

## Installation
- Blender 4.2+: Download from extensions.blender.org
- Manual: Copy folder to `%APPDATA%/Blender Foundation/Blender/{version}/extensions/user_default/`
- Enable: Edit → Preferences → Add-ons → Search "Easy-Print"

## Usage
1. **Cut**: Select mesh → Click "Cut Model" → Draw line → Release → Click
2. **Connect**: Select both halves → Choose connector type → "Generate Connectors"
3. **Adjust**: Scroll = height, Shift+Scroll = size, Click = confirm

## Connector Types
| Type | Description |
|------|-------------|
| **Tab & Slot** | Rectangular, most stable |
| **Peg & Hole** | Cylindrical snap-fit |
| **Dovetail** | Sliding trapezoidal rail |

## Compatibility
- Blender 4.2 through 5.2
- No external Python dependencies

## Links
- [Blender Extensions](https://extensions.blender.org/add-ons/easy-print/)
