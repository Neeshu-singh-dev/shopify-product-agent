# Tests

V1 should be tested with:
- JPG, JPEG, PNG, BMP, TIFF
- WebP
- AVIF/HEIC/HEIF when supported by installed codecs
- GIF
- transparent PNG
- EXIF-rotated image
- oversized image requiring downscaling
- multiple product folders
- corrupt/unsupported files

Verify that original files remain unchanged and that each product folder receives an optimized folder plus the CSV report.
