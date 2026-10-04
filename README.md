# Shopify Product Agent

Version 1 is a local Windows product-image optimizer.

## V1
- JPG/JPEG/PNG/BMP/TIF/TIFF/AVIF/HEIC/HEIF → WebP
- WebP is optimized/re-saved
- GIF is copied unchanged
- Originals are never modified
- Aspect ratio and transparency are preserved
- Images are resized down only when they exceed the selected maximum dimensions
- Creates an optimized folder inside each product folder
- Creates image-optimization-report.csv

## Development

Python 3.14+ is supported.

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app\main.py
```

V1 does not require an API or internet connection after dependencies are installed.

The final portable Windows EXE will be built separately and should be tested on a PC without Python before release.
