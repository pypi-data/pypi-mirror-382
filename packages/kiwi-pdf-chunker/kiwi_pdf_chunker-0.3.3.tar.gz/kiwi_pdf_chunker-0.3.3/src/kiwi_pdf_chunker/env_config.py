import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Allow users to point anywhere via env vars
DOCLING_ARTIFACTS_PATH = os.environ.get("DOCLING_ARTIFACTS_PATH")
EASYOCR_MODULE_PATH = os.environ.get("EASYOCR_MODULE_PATH")

# If not set, default to user-home locations
if not DOCLING_ARTIFACTS_PATH:
    DOCLING_ARTIFACTS_PATH = str(Path.home() / ".kiwi_pdf_chunker" / "docling_models")
if not EASYOCR_MODULE_PATH:
    EASYOCR_MODULE_PATH = str(Path.home() / ".kiwi_pdf_chunker" / "easyocr_models")

# Export so downstream libs see them
os.environ["DOCLING_ARTIFACTS_PATH"] = DOCLING_ARTIFACTS_PATH
os.environ["EASYOCR_MODULE_PATH"] = EASYOCR_MODULE_PATH
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

def _verify_docling_models():
    base = Path(DOCLING_ARTIFACTS_PATH)
    layout = base / "ds4sd--docling-layout-heron"
    table_top  = base / "ds4sd--tableformer"
    table_meta = base / "ds4sd--docling-models" / "model_artifacts" / "tableformer"

    if not layout.exists() or not (table_top.exists() or table_meta.exists()):
        raise RuntimeError(
            "Docling models not found.\n"
            f"Expected at: {base}\n"
            "Must contain:\n"
            "  - ds4sd--docling-layout-heron/\n"
            "  - ds4sd--tableformer/  (or)  ds4sd--docling-models/model_artifacts/tableformer/\n"
            "\nSee README: “Install models locally”."
        )

def _note_easyocr_absent():
    root = Path(EASYOCR_MODULE_PATH)
    flat_ok   = (root / "craft_mlt_25k.pth").exists() and any(root.glob("english_*.pth")) and (root / "dict" / "en.txt").exists()
    nested_ok = (root / "model" / "craft_mlt_25k.pth").exists() and any((root / "model").glob("english_*.pth")) and (root / "dict" / "en.txt").exists()
    if not (flat_ok or nested_ok):
        logger.debug("EasyOCR cache not present (OCR for Docling table parsing is disabled).")

_verify_docling_models()
_note_easyocr_absent()
