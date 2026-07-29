
<div align="center">
  <img src="easy_print/icons/logo.png" width="256" alt="Easy-Print Logo"/>
  <h1>Easy-Print</h1>
  <p><b>A Blender add-on for cutting models and generating interlocking 3D printing connectors</b></p>
  <p>
    <img src="https://img.shields.io/badge/Blender-4.2%20–%205.2-orange" alt="Blender"/>
    <img src="https://img.shields.io/badge/license-GPL--3.0-blue" alt="License"/>
    <img src="https://img.shields.io/badge/version-0.1.0-brightgreen" alt="Version"/>
  </p>
</div>

---
<img width="1920" height="1080" alt="Easy-Print" src="https://github.com/user-attachments/assets/193c4ce4-8204-4638-add8-599353109149" />

## 📖 Overview

Easy-Print lets you split 3D models and add interlocking connectors with just a few clicks. Draw a line across your model to cut it in half, then generate matching male/female connectors — Tab & Slot, Peg & Hole, or Dovetail — ready for 3D printing.

## ✨ Features

- ✂️ **One-Click Cut** — Draw a line across the model, click to split
- 🔗 **Auto Connectors** — Tab & Slot, Peg & Hole, Dovetail with auto-sizing
- 🎛 **Interactive Adjust** — Scroll to change depth, Shift+Scroll to change size
- 👁 **X-Ray Preview** — See connectors clearly during adjustment
- 🖨 **Print Ready** — Built-in clearance for 3D printing tolerances
- 🔄 **Wide Compatiblity** — Blender 4.2 through 5.2

## 🎬 Demo


https://github.com/user-attachments/assets/be9648e3-b187-439e-9894-697de5bae5ba 



<!-- Place your demo video here -->
<!-- 
<p align="center">
  <video src="show-vedio.mp4" width="600" controls></video>
</p>
-->

## 📦 Installation

### Via Blender Extensions (recommended)
1. Open Blender → Edit → Preferences → Add-ons
2. Click the down arrow ▼ → **Install from Repository**
3. Search "Easy-Print"
4. Enable the add-on

### Manual Installation
1. Download the latest `easy_print.zip` from [Releases](https://github.com/fzhe5124-cmyk/easy-print/releases)
2. Blender → Edit → Preferences → Add-ons → ▼ → **Install from Disk**
3. Select the downloaded `.zip` file
4. Enable "Easy-Print"

## 🚀 Usage

### 1. Cut
| Step | Action |
|------|--------|
| **Select** | Select a mesh object |
| **Cut Model** | Click "Cut Model" in the Easy-Print panel |
| **Draw Line** | Click and drag across the model surface |
| **Confirm** | Release → Click to cut |

> The view automatically switches to orthographic mode during drawing.

### 2. Connect
| Step | Action |
|------|--------|
| **Select Both Halves** | Select the two resulting pieces |
| **Choose Type** | Pick Tab & Slot, Peg & Hole, or Dovetail |
| **Generate** | Click "Generate Connectors" |

### 3. Adjust
After generation, you can fine-tune the connectors:

| Input | Action |
|-------|--------|
| **Scroll** | Adjust connector height/depth |
| **Shift+Scroll** | Adjust connector width/size |
| **LMB Click** | Confirm and keep results |
| **RMB / Esc** | Cancel and discard |

## 🔧 Connector Types

| Type | Preview | Best For |
|------|---------|----------|
| **Tab & Slot** | Rectangular box connectors | Most stable, general use |
| **Peg & Hole** | Cylindrical snap-fit pins | Alignment-critical assemblies |
| **Dovetail** | Sliding trapezoidal rail | Lateral assembly, no screws |

## 📋 Requirements

- Blender 4.2 or newer (up to 5.2 tested)
- No external Python packages required

## 📄 License

This project is licensed under **GNU General Public License v3.0**.

## 👤 Author

**Double_G** — fzhe5124@gmail.com


<div align="center">
  <p>⭐ If you find this useful, consider starring the repo!</p>
</div>
