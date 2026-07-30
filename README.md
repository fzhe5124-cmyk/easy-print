<div align="center">
  <img src="easy_print/icons/logo.png" width="180" alt="Easy-Print"/>
  <h1>Easy-Print</h1>
  <p><i>Cut models. Generate connectors. Print. Done.</i></p>
  <p>
    <img src="https://img.shields.io/badge/Blender-4.2%20–%205.2-ec7a1c" alt="Blender"/>
    <img src="https://img.shields.io/badge/license-GPL--3.0-3178c6" alt="License"/>
    <img src="https://img.shields.io/badge/version-0.1.0-2ea44f" alt="Version"/>
    <img src="https://img.shields.io/badge/platform-cross--platform-8b8b8b" alt="Platform"/>
  </p>
</div>

---

<img width="1920" height="1080" alt="Demo" src="https://github.com/user-attachments/assets/193c4ce4-8204-4638-add8-599353109149" />

## ✦ Overview

Easy-Print simplifies the 3D printing workflow — draw a line across your model to split it, then generate interlocking connectors on the cut surfaces in one click. Choose from three connector types, all auto-sized with adjustable clearance for real-world print tolerances.

> **Tab & Slot** · **Peg & Hole** · **Dovetail** — pick the right joint for your project.

## ✦ Features

|     |     |
|:----|:----|
| **Line-Based Cutting**   | Draw a line to define the cut plane — no manual knife tooling. |
| **Three Connector Types** | Tab & Slot, Peg & Hole, and Dovetail — each auto-sized to the surface. |
| **Multi-Connector Placement** | Place one or many connectors per face; count, margin, and spacing are configurable. |
| **Adjustable Clearance** | Tolerance gap tuned for FDM and SLA printers (default 2%). |
| **Live Adjustment**      | Scroll to dial depth; Shift+Scroll to change size — preview updates in real time. |
| **X-Ray Preview**        | See through the model during adjustment for precise alignment. |
| **Orthographic Toggle**  | View switches to ortho automatically while drawing the cut line. |
| **Blender 4.2 – 5.2**   | Works across four major Blender versions with no external dependencies. |

## ✦ Demo

https://github.com/user-attachments/assets/be9648e3-b187-439e-9894-697de5bae5ba

## ✦ Installation

### From Blender Extensions *(recommended)*
1. **Edit** → **Preferences** → **Add-ons**
2. Click the dropdown ⏷ → **Get Extensions**
3. Search **"Easy-Print"** → **Install**

### Manual
1. Download `easy_print.zip` from [Releases](https://github.com/fzhe5124-cmyk/easy-print/releases)
2. **Edit** → **Preferences** → **Add-ons** → ⏷ → **Install from Disk**
3. Select the file and enable **Easy-Print**

## ✦ Usage

### 1. Cut

<div align="center">

| Step          | Action                                                                 |
|:--------------|:------------------------------------------------------------------------|
| **Select**    | Pick a mesh object in Object Mode                                      |
| **Cut Model** | Click the button in the side panel (press **N** → Easy-Print tab)      |
| **Draw Line** | Click and drag across the model                                        |
| **Confirm**   | Release to preview the plane, then click to cut                        |

</div>

### 2. Connect

<div align="center">

| Step                      | Action                                         |
|:--------------------------|:-----------------------------------------------|
| **Select Both Halves**    | Select the two resulting mesh objects          |
| **Choose Type**           | Pick a connector from the dropdown             |
| **Generate**              | Click **Generate Connectors**                  |

</div>

### 3. Adjust

<div align="center">

| Hotkey              | Action                     |
|:--------------------|:---------------------------|
| **Scroll**          | Change connector depth     |
| **Shift + Scroll**  | Change connector size      |
| **Left Click**      | Confirm and finalize       |
| **Right Click**     | Cancel and discard         |

</div>

## ✦ Connector Types

<div align="center">

| Type              | Shape            | Best For                                  |
|:------------------|:-----------------|:------------------------------------------|
| **Tab & Slot**    | Rectangular      | General purpose — strongest hold          |
| **Peg & Hole**    | Cylindrical      | Alignment pins, snap-fit registration     |
| **Dovetail**      | Trapezoidal rail | Sliding assembly, no fasteners needed     |

</div>

## ✦ Requirements

- Blender **4.2** or newer
- No external Python packages needed

## ✦ License

**GNU GPL v3.0** — free to use, modify, and share.

## ✦ Author

**Double_G** — [fzhe5124@gmail.com](mailto:fzhe5124@gmail.com)

## ✦ Links

- [Blender Extensions page](https://extensions.blender.org/add-ons/easy-print/)
- [GitHub repository](https://github.com/fzhe5124-cmyk/easy-print)
