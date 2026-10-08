# Shopify Product Agent

Version 1 is a local Windows product-image optimizer. Jarvis Manager is the orchestration layer around the specialist agents.

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

Current registered specialists:
- Product Agent — wraps the existing V1 image engine without rewriting it.
- Image Agent — uses the OpenAI Images API for image generation, image editing, and transparent-background removal.

Reserved future boundary:
- Video Agent — GitHub-only initially; no heavy local video dependencies.

## Image Agent

The Image Agent supports:
- Generate an image from a prompt
- Edit an existing image using a prompt
- Remove an image background and return a transparent PNG

The Image Agent requires an OpenAI API key in the local environment:

```bat
set OPENAI_API_KEY=your_api_key_here
```

The key is read from the environment and is not stored in the repository.

### Image generation

```bat
.venv\\Scripts\\python.exe -m manager "Create a premium jewelry product image" --root "C:\\Products" --output "C:\\Products\\generated.png"
```

Use `--prompt` when the image prompt should differ from the Manager request:

```bat
.venv\\Scripts\\python.exe -m manager "Create image" --root "C:\\Products" --prompt "A luxury gold ring on a clean ivory studio background" --output "C:\\Products\\ring.png"
```

### Image editing

```bat
.venv\\Scripts\\python.exe -m manager "Edit image" --root "C:\\Products" --input "C:\\Products\\ring.png" --output "C:\\Products\\ring-edited.png" --prompt "Place the ring on a premium cream marble surface with soft studio lighting"
```

### Background removal

```bat
.venv\\Scripts\\python.exe -m manager "Remove background" --root "C:\\Products" --input "C:\\Products\\ring.png" --output "C:\\Products\\ring-transparent.png"
```

Image-generation quality is controlled separately from Product Agent WebP quality:
- `--image-quality` controls generated/edited image quality.
- `--quality` controls Product Agent WebP compression quality.

## Manager CLI

From the repository root:

```bat
.venv\\Scripts\\python.exe -m manager "Optimize the product images in this folder" --root "C:\\Products"
```

Optional Product Agent settings:

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

The V1 Product Agent remains usable without an API key. The Image Agent requires an OpenAI API key and internet access when its creative actions are invoked.

The final portable Windows EXE will be built separately and should be tested on a PC without Python before release.