# Osdag Bridge
## Overview
This repository contains the source code for Osdag bridge component of [Osdag](https://github.com/osdag-admin/Osdag).
## Technical Stack

- **Framework**: PySide6 (Qt for Python)
- **Language**: Python 3.8+
- **Architecture**: Model-View pattern with modular design

## Project Structure

```
OsBridge/
├── src/
│   └── osbridge/
│       ├── template_page.py      # Main application window
│       ├── input_dock.py          # Basic inputs panel
│       ├── additional_inputs.py   # Additional inputs dialog
│       ├── backend.py             # Backend logic and validation
│       ├── common.py              # Shared constants and utilities
│       └── resources/             # Images and resources
├── README.md
└── requirements.txt
```
## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/garvit000/osdag_bridge.git
cd osdag_bridge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies
```
PySide6>=6.5.0
```
## Usage

### Running the Application

Run as a module from src directory:
```bash
python -m osbridge.template_page
```
