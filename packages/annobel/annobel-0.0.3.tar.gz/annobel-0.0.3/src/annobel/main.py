"""Main runtime module for the annobel package (AGPL-3.0-or-later).

Provides programmatic run() and interactive main() entrypoints.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from . import _core


def run(
    images_dir: str,
    labels_dir: str | None = None,
    mode: str = "manual",
    model_path: str = "",
    classes_file: str = "",
    conf: float = 0.25,
    open_editor_after_detect: bool = True,
    write_empty_detection_files: bool = True,  # default changed to True in 0.0.3
    classes_filter_ids: Optional[List[int]] = None,
    force_mode_dialog: bool = False,
):
    cfg = _core.CONFIG.copy()
    cfg.update(
        {
            "images_dir": images_dir,
            "labels_dir": labels_dir or str(Path(images_dir) / "labels"),
            "mode": mode,
            "model_path": model_path,
            "classes_file": classes_file or str(Path(labels_dir or Path(images_dir) / "labels") / "classes.txt"),
            "conf": conf,
            "open_editor_after_detect": open_editor_after_detect,
            "write_empty_detection_files": write_empty_detection_files,
            "classes_filter_ids": classes_filter_ids or [],
            "force_mode_dialog": force_mode_dialog,
        }
    )
    _core.CONFIG.update(cfg)
    _core.validate_and_fill()
    _core.run_mode(cfg["mode"])


def main():  # interactive
    _core.main()


if __name__ == "__main__":  # pragma: no cover
    main()
