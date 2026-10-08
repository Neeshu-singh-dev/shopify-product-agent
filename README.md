# Shopify Product Agent

Version 1 is a local Windows product-image optimizer. Jarvis Manager is now the orchestration layer around the specialist agents.

## V1 Product Agent
- JPG/JPEG/PNG/BMP/TIF/TIFF/AVIF/HEIC/HEIF → WebP
- WebP is optimized/re-saved
- GIF is copied unchanged
- Originals are never modified
- Aspect ratio and transparency are preserved
- Images are resized down only when they exceed the selected maximum dimensions
- Creates an optimized folder inside each product folder
- Creates image-optimization-report.csv

## Jarvis Manager
The Manager receives a natural-language request, creates a small execution plan, selects a registered specialist, executes it, and returns a normalized result.

Current registered specialist:
- Product Agent — wraps the existing V1 image engine without rewriting it.

Reserved future boundaries:
- Image Agent — creative image generation/editing
- Video Agent — GitHub-only initially; no heavy local video dependencies

### Manager CLI

From the repository root:

```bat
.venv\\Scripts\\python.exe -m manager "Optimize the product images in this folder" --root "C:\\Products"
```

Optional settings:

```bat
.venv\\Scripts\\python.exe -m manager "Optimize the product images in this folder" --root "C:\\Products" --quality 88 --max-width 2000 --max-height 2000
```

The command prints a JSON result containing the agent, task status, summary, output report path, statistics, and errors.

## Development

Python 3.14+ is supported.

```bat
python -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.venv\\Scripts\\python.exe app\\main.py
```

V1 does not require an API or internet connection after dependencies are installed.

The final portable Windows EXE will be built separately and should be tested on a PC without Python before release.
