from __future__ import annotations

import argparse
import json

from .manager import create_default_manager


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis Shopify Multi-Agent Manager")
    parser.add_argument("request", help="Natural-language task for Jarvis")
    parser.add_argument("--root", required=True, help="Product root folder")
    parser.add_argument("--prompt", help="Image generation/edit prompt")
    parser.add_argument("--input", dest="input_path", help="Input image for editing/background removal")
    parser.add_argument("--output", dest="output_path", help="Output image path")
    parser.add_argument("--model", default="runwayml/stable-diffusion-v1-5", help="Local Hugging Face model id")
    parser.add_argument("--size", default="512x512", help="Local image size, WIDTHxHEIGHT")
    parser.add_argument("--image-quality", default="standard", help="Reserved for future provider-specific quality controls")
    parser.add_argument("--background", default="auto", help="Reserved for provider-specific background controls")
    parser.add_argument("--output-format", default="png", choices=["png", "jpeg", "webp"])
    parser.add_argument("--quality", type=int, default=88, help="Product image WebP quality")
    parser.add_argument("--max-width", type=int, default=2000)
    parser.add_argument("--max-height", type=int, default=2000)
    args = parser.parse_args()

    manager = create_default_manager()
    results = manager.handle(
        args.request,
        root=args.root,
        prompt=args.prompt or args.request,
        input_path=args.input_path,
        output_path=args.output_path,
        model=args.model,
        size=args.size,
        image_quality=args.image_quality,
        background=args.background,
        output_format=args.output_format,
        quality=args.quality,
        max_width=args.max_width,
        max_height=args.max_height,
    )
    print(json.dumps([result.to_dict() for result in results], indent=2))


if __name__ == "__main__":
    main()
