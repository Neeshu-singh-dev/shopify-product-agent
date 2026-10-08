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

The Image Agent is **local-first and API-free**. It does not require an OpenAI API key or any paid API.

It currently supports:
- Local text-to-image generation with Diffusers.
- Local image-to-image editing.
- Local background removal through the optional rembg stack.

The default generation model is `runwayml/stable-diffusion-v1-5`. The provider is lazy-loaded, so the normal Product Agent does not load a large AI model.

### Local AI installation

The core project remains lightweight. Install the optional local stack only when you want creative Image Agent features:

```bat
.venv\\Scripts\\python.exe -m pip install -r requirements-local.txt
```

For an NVIDIA GPU, install a PyTorch build compatible with your installed NVIDIA driver/CUDA environment before running generation. The first model run downloads the selected model weights to the local machine.

### Image generation

```bat
.venv\\Scripts\\python.exe -m manager "Create a premium jewelry product image" --root "C:\\Products" --output "C:\\Products\\generated.png"
```

Use `--prompt` for a more specific creative instruction:

```bat
.venv\\Scripts\\python.exe -m manager "Create image" --root "C:\\Products" --prompt "A luxury gold ring on an ivory studio background, premium jewelry photography" --output "C:\\Products\\ring.png" --size 512x512
```

### Image editing

```bat
.venv\\Scripts\\python.exe -m manager "Edit image" --root "C:\\Products" --input "C:\\Products\\ring.png" --output "C:\\Products\\ring-edited.png" --prompt "Place the ring on a premium cream marble surface with soft studio lighting"
```

### Background removal

```bat
.venv\\Scripts\\python.exe -m manager "Remove background" --root "C:\\Products" --input "C:\\Products\\ring.png" --output "C:\\Products\\ring-transparent.png"
```

### Why local instead of an API?

Jarvis is intentionally designed so the Image Agent does not depend on a paid cloud API. Local providers can be replaced or expanded later without changing the Manager contract. Large modern image models can require much more VRAM than a 6GB GPU, so the first local provider uses a lighter model and memory-saving CPU offload rather than assuming every model will fit.

**Commercial-use note:** model weights have their own licenses. Before using a downloaded model for commercial Shopify/client work, verify that model's current license. We are not treating every open-source model as automatically commercial-safe.
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

The V1 Product Agent works without any API key. The local Image Agent does not require a paid API; internet is only needed when downloading model packages/weights for the first time, unless the required models are already cached locally.

The final portable Windows EXE will be built separately and should be tested on a PC without Python before release.