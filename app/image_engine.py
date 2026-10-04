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

# Product photos can legitimately be very large. Keep a safety ceiling,
# but raise Pillow's default so large source images can still be resized.
MAX_SOURCE_PIXELS = 300_000_000
Image.MAX_IMAGE_PIXELS = MAX_SOURCE_PIXELS

SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".avif", ".heic", ".heif", ".webp"}


def safe_product_name(name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    return value or "product"


def prepare_output_dir(product_dir: Path) -> Path:
    output_dir = product_dir / "optimized"
    output_dir.mkdir(exist_ok=True)

    # The optimized folder is owned by this tool. Re-running optimization
    # should rebuild it rather than create -2, -3, etc. copies.
    for item in output_dir.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    return output_dir


def optimize_product_folder(product_dir: Path, quality: int, max_width: int, max_height: int, log=print):
    output_dir = prepare_output_dir(product_dir)

    images = sorted(
        [p for p in product_dir.iterdir() if p.is_file()],
        key=lambda p: p.name.lower(),
    )

    rows = []
    number = 1
    product_name = safe_product_name(product_dir.name)

    for source in images:
        ext = source.suffix.lower()

        if ext == ".gif":
            destination = output_dir / f"{product_name}{number}.gif"
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

        destination = output_dir / f"{product_name}{number}.webp"

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


def build_summary(rows):
    images_found = len(rows)
    converted = sum(1 for row in rows if row[3] == "Converted to WebP" and row[6] == "OK")
    gif_unchanged = sum(1 for row in rows if row[3] == "GIF unchanged" and row[6] == "OK")
    webp_optimized = sum(1 for row in rows if row[3] == "WebP optimized" and row[6] == "OK")
    failed = sum(1 for row in rows if row[6] == "FAILED")
    original_bytes = sum(int(row[4] or 0) for row in rows)
    output_bytes = sum(int(row[5] or 0) for row in rows)
    saved_bytes = max(0, original_bytes - output_bytes)
    savings_percent = (saved_bytes / original_bytes * 100) if original_bytes else 0
    return {
        "images_found": images_found,
        "converted": converted,
        "gif_unchanged": gif_unchanged,
        "webp_optimized": webp_optimized,
        "failed": failed,
        "original_bytes": original_bytes,
        "output_bytes": output_bytes,
        "saved_bytes": saved_bytes,
        "savings_percent": savings_percent,
    }


def optimize_root(root: Path, quality: int, max_width: int, max_height: int, progress=None, log=print):
    product_dirs = sorted(
        [p for p in root.iterdir() if p.is_dir() and p.name.lower() != "optimized"],
        key=lambda p: p.name.lower(),
    )
    all_rows = []

    for index, product_dir in enumerate(product_dirs, start=1):
        log(f"Processing product folder: {product_dir.name}")
        all_rows.extend(optimize_product_folder(product_dir, quality, max_width, max_height, log))

        if progress:
            progress(index / max(1, len(product_dirs)))

    report = root / "image-optimization-report.csv"

    with report.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "product_folder", "source_file", "output_file", "action",
            "original_size_bytes", "output_size_bytes", "status", "error"
        ])
        writer.writerows(all_rows)

    return report, all_rows, build_summary(all_rows)
