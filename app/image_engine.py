from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".avif", ".heic", ".heif", ".webp"}


def safe_product_name(name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    return value or "product"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    i = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{i}{path.suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def optimize_product_folder(product_dir: Path, quality: int, max_width: int, max_height: int, log=print):
    output_dir = product_dir / "optimized"
    output_dir.mkdir(exist_ok=True)

    images = sorted(
        [p for p in product_dir.iterdir() if p.is_file()],
        key=lambda p: p.name.lower(),
    )

    rows = []
    number = 1

    for source in images:
        ext = source.suffix.lower()
        if ext == ".gif":
            destination = unique_path(output_dir / f"{safe_product_name(product_dir.name)}{number}.gif")
            try:
                shutil.copy2(source, destination)
                rows.append([product_dir.name, source.name, destination.name, "GIF unchanged",
                             source.stat().st_size, destination.stat().st_size, "OK", ""])
                number += 1
                log(f"GIF unchanged: {source.name}")
            except Exception as exc:
                rows.append([product_dir.name, source.name, "", "GIF unchanged",
                             source.stat().st_size, 0, "FAILED", str(exc)])
            continue

        if ext not in SUPPORTED:
            continue

        destination = unique_path(output_dir / f"{safe_product_name(product_dir.name)}{number}.webp")
        try:
            original_size = source.stat().st_size
            with Image.open(source) as image:
                image = ImageOps.exif_transpose(image)
                image.load()

                if image.width > max_width or image.height > max_height:
                    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                if "A" in image.getbands():
                    image = image.convert("RGBA")
                else:
                    image = image.convert("RGB")

                image.save(destination, "WEBP", quality=quality, method=6)

            output_size = destination.stat().st_size
            action = "WebP optimized" if ext == ".webp" else "Converted to WebP"
            rows.append([product_dir.name, source.name, destination.name, action,
                         original_size, output_size, "OK", ""])
            log(f"{action}: {source.name}")
            number += 1
        except Exception as exc:
            rows.append([product_dir.name, source.name, "", "Skipped",
                         source.stat().st_size if source.exists() else 0, 0, "FAILED", str(exc)])
            log(f"FAILED: {source.name} — {exc}")

    return rows


def optimize_root(root: Path, quality: int, max_width: int, max_height: int, progress=None, log=print):
    product_dirs = sorted([p for p in root.iterdir() if p.is_dir() and p.name.lower() != "optimized"],
                          key=lambda p: p.name.lower())
    all_rows = []
    for index, product_dir in enumerate(product_dirs, start=1):
        log(f"Processing product folder: {product_dir.name}")
        all_rows.extend(optimize_product_folder(product_dir, quality, max_width, max_height, log))
        if progress:
            progress(index / max(1, len(product_dirs)))

    report = root / "image-optimization-report.csv"
    with report.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["product_folder", "source_file", "output_file", "action",
                         "original_size_bytes", "output_size_bytes", "status", "error"])
        writer.writerows(all_rows)

    return report, all_rows
