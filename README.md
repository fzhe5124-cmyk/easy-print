<div align="center">
  <img src="easy_print/icons/logo.png" width="200" alt="Easy-Print"/>
  <h1>Easy-Print</h1>
  <p>A Blender add-on for cutting 3D models and generating interlocking connectors for 3D printing.</p>
  <p>
    <img src="https://img.shields.io/badge/Blender-4.2%20–%205.2-orange" alt="Blender"/>
    <img src="https://img.shields.io/badge/license-GPL--3.0-blue" alt="License"/>
    <img src="https://img.shields.io/badge/version-0.1.0-brightgreen" alt="Version"/>
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform"/>
  </p>
</div>

---

<img width="1920" height="1080" alt="Easy-Print Demo" src="https://github.com/user-attachments/assets/193c4ce4-8204-4638-add8-599353109149" />

## Overview

Easy-Print simplifies the 3D printing workflow by allowing you to cut a model along any plane and automatically generate interlocking connectors — Tab & Slot, Peg & Hole, or Dovetail — on the cut surfaces. All connectors are auto-sized and include adjustable clearance for print tolerances.

## Features

- **Line-based cutting** — Draw a line across the model to define the cut plane
- **Three connector types** — Tab & Slot (rectangular), Peg & Hole (cylindrical), Dovetail (trapezoidal rail)
- **Auto-sizing** — Connector dimensions adapt to the cut surface automatically
- **Multiple connectors** — Place one or many connectors on a single cut surface; count, margin, and distribution are fully configurable
- **Clearance control** — Adjustable tolerance gap for FDM and SLA printing
- **Post-generation adjustment** — Scroll to change depth; Shift+Scroll to change size
- **X-ray preview** — Transparent view during adjustment for precise alignment
- **Orthographic toggle** — View switches automatically during interactive cutting
- **Blender 4.2 – 5.2** — Compatible across four major versions

## Demo

https://github.com/user-attachments/assets/be9648e3-b187-439e-9894-697de5bae5ba

## Installation

### Blender Extensions (recommended)

1. Edit → Preferences → Add-ons
2. Click the dropdown arrow → **Get Extensions**
3. Search "Easy-Print"
4. Click **Install**

### Manual

1. Download `easy_print.zip` from [Releases](https://github.com/fzhe5124-cmyk/easy-print/releases)
2. Edit → Preferences → Add-ons → ▼ → **Install from Disk**
3. Select the downloaded file and enable

## Usage

### Cut

<div align="center">

| Step          | Action                                                                  |
|:--------------|:------------------------------------------------------------------------|
| Select        | Select a mesh object in Object Mode                                     |
| Cut Model     | Click the button in the Easy-Print panel (N key → Easy-Print tab)       |
| Draw Line     | Click and drag across the model surface                                 |
| Confirm       | Release to preview, click to cut                                        |

</div>

### Connect

<div align="center">

| Step                 | Action                                         |
|:---------------------|:-----------------------------------------------|
| Select Both Halves   | Select the two resulting mesh objects          |
| Choose Type          | Pick a connector type from the dropdown        |
| Generate             | Click **Generate Connectors**                  |

</div>

### Adjust

<div align="center">

| Input              | Action                     |
|:-------------------|:---------------------------|
| Scroll             | Change connector depth     |
| Shift + Scroll     | Change connector size      |
| Left Click         | Confirm and finalize       |
| Right Click / Esc  | Cancel and discard         |

</div>

## Connector Types

<div align="center">

| Type          | Shape              | Use Case                                   |
|:--------------|:-------------------|:-------------------------------------------|
| Tab & Slot    | Rectangular        | General-purpose, most stable               |
| Peg & Hole    | Cylindrical        | Alignment pins, snap-fit joints            |
| Dovetail      | Trapezoidal rail   | Sliding assembly, lateral shear resistance |

</div>

## Requirements

- Blender 4.2 or newer
- No external dependencies

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

## Author

Double_G — [fzhe5124@gmail.com](mailto:fzhe5124@gmail.com)

## Links

- [Blender Extensions](https://extensions.blender.org/add-ons/easy-print/)
- [GitHub Repository](https://github.com/fzhe5124-cmyk/easy-print)
