# Background Removal App

[![CI](https://github.com/PietjePuh/BackgroundRemoval/actions/workflows/ci.yml/badge.svg)](https://github.com/PietjePuh/BackgroundRemoval/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Streamlit application for automatic image background removal powered by the [rembg](https://github.com/danielgatis/rembg) library. Upload one or many images, choose your output format, and replace backgrounds with solid colors, blur effects, or custom images.

![Screenshot placeholder](https://via.placeholder.com/800x400?text=App+Screenshot)

## Features

- **Batch processing** -- Upload up to 10 images at once and download all results as a ZIP
- **Output format selection** -- Choose between PNG (transparent), WEBP, or JPEG output
- **Before/after comparison** -- Side-by-side view of original and processed images
- **Background replacement** -- Replace the removed background with:
  - Transparent (default)
  - Solid color (color picker)
  - Blurred original (adjustable radius)
  - Custom image upload
- **Smart resizing** -- Large images are automatically resized to prevent memory issues
- **Rate limiting** -- Built-in protection against excessive processing requests
- **Security hardened** -- File size limits, format validation, dimension checks, path traversal prevention

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

Clone the repository:

```bash
git clone https://github.com/PietjePuh/BackgroundRemoval.git
cd BackgroundRemoval
```

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run bg_remove.py
```

The app will be available at [http://localhost:8501](http://localhost:8501) in your web browser.

### Running with Docker

Build and run the Docker image:

```bash
docker build -t background-removal .
docker run -p 8501:8501 background-removal
```

The app will be available at [http://localhost:8501](http://localhost:8501).

## Usage

### Single Image

- Select your desired output format and background mode in the sidebar
- Upload an image (PNG, JPG, or JPEG, up to 10MB)
- View the before/after comparison
- Click the download button to save the result

### Batch Processing

- Upload multiple images using the file uploader (up to 10 at once)
- Each image is processed and displayed in an expandable section
- Use "Download All as ZIP" to get all results in a single archive

### Background Replacement

| Mode                 | Description                                               |
| -------------------- | --------------------------------------------------------- |
| **Transparent**      | Default -- keeps the background transparent (PNG/WEBP)    |
| **Solid Color**      | Pick any color using the color picker                     |
| **Blurred Original** | Applies a Gaussian blur to the original background        |
| **Custom Image**     | Upload your own background image                          |

### Output Formats

| Format   | Transparency      | Best For                              |
| -------- | ----------------- | ------------------------------------- |
| **PNG**  | Yes               | Web, editing, quality preservation    |
| **WEBP** | Yes               | Web optimization, smaller file sizes  |
| **JPEG** | No (white fallback) | Sharing, compatibility              |

## Development

### Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

### Run tests

```bash
pytest tests/ -v
```

### Run linter

```bash
ruff check .
ruff format --check .
```

### Project Structure

```text
BackgroundRemoval/
├── bg_remove.py            # Main Streamlit application
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies (includes test/lint tools)
├── Dockerfile              # Multi-stage Docker build
├── .dockerignore           # Docker build exclusions
├── .streamlit/
│   └── config.toml         # Streamlit server configuration
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions: lint, test, Docker build
├── tests/
│   ├── conftest.py         # Shared test fixtures and mock setup
│   ├── test_validation.py  # File upload validation tests
│   ├── test_output_format.py   # Output format conversion tests
│   ├── test_batch_processing.py # Batch processing and ZIP tests
│   ├── test_background_replacement.py # Background replacement tests
│   ├── test_resize.py      # Image resize logic tests
│   └── test_rate_limit_logic.py # Rate limiting tests
├── zebra.jpg               # Sample image
├── wallaby.png             # Sample image
└── __init__.py
```

## Image Guidelines

- Maximum file size: 10MB per image
- Maximum batch size: 10 images
- Source dimensions: up to 6000x6000 pixels
- Large images are automatically resized to 2000px max dimension
- Supported input formats: PNG, JPG, JPEG

## API / Functions Reference

| Function                                | Purpose                                            |
| --------------------------------------- | -------------------------------------------------- |
| `process_image(image_bytes)`            | Core background removal with validation and caching |
| `validate_uploaded_file(upload)`        | Check file size constraints                        |
| `convert_image_to_format(img, format)`  | Convert PIL image to PNG/WEBP/JPEG bytes           |
| `apply_background_replacement(...)`     | Apply transparent/solid/blur/custom background     |
| `create_zip_archive(images_data)`       | Bundle multiple images into a ZIP                  |
| `resize_image(image, max_size)`         | Resize maintaining aspect ratio                    |
| `check_rate_limit()`                    | Session-based rate limiting (5 req/min)            |

## License

MIT

## Acknowledgments

- [rembg](https://github.com/danielgatis/rembg) -- Background removal engine
- [Streamlit](https://streamlit.io) -- Web application framework
- [Pillow](https://python-pillow.org/) -- Image processing
