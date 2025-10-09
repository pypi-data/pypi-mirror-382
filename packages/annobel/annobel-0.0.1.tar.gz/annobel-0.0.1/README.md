# annobel

Automatic + manual YOLO-format bounding box annotation tool with a Tkinter GUI
(editor) and console fallback.

> Version: 0.0.1 (Alpha)

## Overview
`annobel` streamlines creating and refining object detection datasets. It
wraps Ultralytics YOLOv8 models for optional automatic bounding box proposal,
then lets you refine or create labels manually. The tool stores annotations in
standard YOLO text format (`class x_center y_center width height`, normalized
values).

### Main Features
- Automatic annotation (detection) using Ultralytics YOLOv8 model variants or local weights.
- Manual drawing, moving, resizing, deleting bounding boxes.
- Class list management (add / rename) saved to a `classes.txt` file.
- Autosave after every modification.
- Console fallback when `tkinter` is not present.
- Per-image navigation and keyboard shortcuts.
- Optional subset filtering of detection classes.
- Non-destructive: detection stage creates / overwrites only label files.

## Installation
```bash
pip install annobel
```

### Dependencies
- Python >= 3.8
- `ultralytics` (YOLO) – installed automatically.
- `pillow` for image handling.

## Quick Start (CLI)
After installation:
```bash
annobel
```
You will be prompted (GUI or console fallback) to choose:
1. Mode: Automatic Annotation (YOLO) or Manual Annotation / Editing.
2. Image & label directories.
3. (Auto mode) model selection (download variant or local path) and optional class subset.

Labels are saved as `<image_stem>.txt` in the labels directory. A `classes.txt`
is created/updated as needed.

## Programmatic Usage
```python
from annobel import run  

run(
    images_dir="/path/to/images",
    mode="auto",                 # or "manual"
    model_path="yolov8n.pt",      # only needed for auto mode
    conf=0.25,
    classes_filter_ids=[0, 2],    # optional subset
)
```
For full interactive loop (menu reappears after exiting editor):
```python
from annobel import main
main()
```

## Directory Structure (Generated)
```
images/
  img001.jpg
  img002.jpg
labels/
  img001.txt
  img002.txt
  classes.txt
```

## YOLO Label Format Recap
Each line: `class_id x_center y_center width height` with all coordinates
normalized to `[0,1]` relative to image width/height.

## Keyboard & Mouse Shortcuts (Editor)
- A: Add mode
- E: Edit mode
- C: Change class of selected box
- M: Manage classes dialog
- Delete: Remove selected box
- ← / →: Previous / next image
- Q: Return to main menu
- I: Print info about current boxes
- Mouse (Add mode): Click-drag to draw box
- Mouse (Edit mode): Drag box interior to move; handles to resize; right-click to delete

## Recommended Workflow
1. Place raw images into an `images` directory.
2. Run auto mode with a YOLO model (e.g., `yolov8n.pt`) to bootstrap labels.
3. Inspect & refine with manual editor (resize, delete, add boxes, change classes).
4. Iterate until dataset is satisfactory.

## Ultralytics Notice & Licensing
This package depends on the external `ultralytics` project for YOLO model
loading and inference. Key points:
- Ultralytics repository: https://github.com/ultralytics/ultralytics
- Their code / weights are subject to the AGPL-3.0 license by default and/or
  alternative commercial terms offered by Ultralytics. See their LICENSE and
  documentation for the authoritative terms.
- This package does NOT bundle or redistribute model weights; it only invokes
  the `YOLO` API when you request detection.
- If you deploy or integrate this in a network service or commercial product,
  ensure you meet the obligations of the Ultralytics license (e.g., providing
  source, offering access, or acquiring a commercial license if required).

You (the end user) are solely responsible for verifying that your intended use
of the models and resulting annotations complies with applicable licenses and
data privacy regulations.

## Contributing
1. Fork repository
2. Create a feature branch: `git checkout -b feature/awesome`
3. Install dev extras: `pip install -e .[dev]`
4. Run linters / tests: `flake8`, `black --check .`, `pytest`
5. Submit PR

## Versioning / Changelog
- 0.0.1: Initial packaged release (renamed to annobel)

## Roadmap Ideas
- Export to COCO format
- Integrated image augmentation preview
- Polygon / segmentation support
- Multi-threaded batch detection
- Custom hotkey configuration
- Dark / light UI themes

## Security / Privacy
Images are processed locally. No images or labels are uploaded by this package.
Be cautious with sensitive imagery and model weight redistribution restrictions.

## Disclaimer
Provided "AS IS" under AGPL-3.0-or-later. No warranty of fitness for a particular
purpose. Always validate annotations before using for training.

## License
- This package: AGPL-3.0-or-later (see LICENSE)
- Ultralytics YOLO: AGPL-3.0 (or commercial) – external dependency

---
© 2025 Sayali Dongre
