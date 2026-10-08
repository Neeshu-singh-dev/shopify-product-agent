from __future__ import annotations

import argparse
import json

from .manager import create_default_manager


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis Shopify Multi-Agent Manager")
    parser.add_argument("request", help="Natural-language task for Jarvis")
    parser.add_argument("--root", required=True, help="Product root folder")
    parser.add_argument("--quality", type=int, default=88)
    parser.add_argument("--max-width", type=int, default=2000)
    parser.add_argument("--max-height", type=int, default=2000)
    args = parser.parse_args()

    manager = create_default_manager()
    results = manager.handle(
        args.request,
        root=args.root,
        quality=args.quality,
        max_width=args.max_width,
        max_height=args.max_height,
    )
    print(json.dumps([result.to_dict() for result in results], indent=2))


if __name__ == "__main__":
    main()
