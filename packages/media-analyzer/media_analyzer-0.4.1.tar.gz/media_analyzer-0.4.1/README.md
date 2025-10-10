# Media Analyzer

Media Analyzer is a Python library designed to analyze media files, providing insights into their
content and metadata. It supports various functionalities, including image classification,
captioning, optical character recognition (OCR), and facial recognition.

## Features

- **GPS**: Gather GPS coordinates from exif, and reverse geocode to get the country, province and
  city.
- **Exif**: Extract exif data/metadata from photos, videos, gifs, etc.
- **Weather**: Get weather info at the time the photo/video was taken.
    * temperature
    * dewpoint
    * relative humidity
    * precipitation
    * wind gust
    * pressure
    * sun hours
    * condition

* **Quality Detection**: Detect objectively measurable quality of images:
    * Sharpness
    * Noise
    * Exposure
    * Dynamic range
    * Color clipping (white/black levels)
    * A composite score is generated, so photos can be ranked by quality.

- **Image Classification**: Identify objects, scene type, activities, animals, and events present in
  images.
- **Image Captioning**: Generate descriptive captions for images using models like BLIP or
  LLM-based captioners.
- **Embedding**: Generate clip embeddings for images and text. Can be used to cluster images or
  search semantically through images.
- **Optical Character Recognition (OCR)**: Extract text from images to identify documents, receipts,
  menus, and more.
- **LLM**: Get detailed image summary, more indepth than just a caption, using an LLM. Can also be
  used to generate a summary of a document shown in a photo or video.
- **Facial Recognition**: Detect faces in images and provide details such as age, sex, bounding box,
  and facial landmarks. Includes an embedding of the face, which can be used for clustering.
- **Datetime Taken**: Photo and video files are messy and have unreliable datetime tags. This
  packages uses six different methods with varying priority to get the datetime a photo is taken,
  including the timezone if possible.
- **Data Url**: Generate data url for tiny preload thumbnail.
- **Special type detection**: Detect slow motion, night sight, motion photos, and more.
- **Color Analysis**: Get prominent colors from an image, with theme colors based off the colors.

## Installation

To install Media Analyzer, use pip:

```bash
pip install media-analyzer
```

### Requirements

You must have the following in PATH.

* ExifTool: https://exiftool.org/
* Tesseract OCR: https://tesseract-ocr.github.io/tessdoc/Installation.html

## Examples

Example output of the main analyze function can be viewed
at [example_output.json](https://github.com/RuurdBijlsma/media-analyzer/blob/main/examples/example_output.json).
Further example code is available
at [/examples](https://github.com/RuurdBijlsma/media-analyzer/tree/main/examples).

## Usage

Here's a basic example of how to use Media Analyzer:

```python
from media_analyzer import MediaAnalyzer
from pathlib import Path

analyzer = MediaAnalyzer()
media_file = Path("image.jpg")
result = analyzer.photo(media_file)

print(result)
```

### Disable analysis modules

The analysis is done based on modules, the following modules are available and enabled by default (
click the links to
see the possible modules).

#### [File-based Modules](https://ruurdbijlsma.github.io/media-analyzer/media_analyzer.html#FileModule)

#### [Visual Modules](https://ruurdbijlsma.github.io/media-analyzer/media_analyzer.html#VisualModule)

Modules can be turned off by changing the config provided to the MediaAnalyzer class:

```python
from media_analyzer import MediaAnalyzer, AnalyzerSettings, FileModule, VisualModule
from pathlib import Path

config = AnalyzerSettings(
    enabled_file_modules={FileModule.EXIF},  # Only do exif data analysis on file
    enabled_visual_modules={VisualModule.CAPTION},  # Only do caption module as visual module
)
analyzer = MediaAnalyzer(config=config)
media_file = Path(__file__).parents[1] / "tests/assets/tent.jpg"
result = analyzer.photo(media_file)
```

### Configuration

The AnalyzerSettings class allows you to customize various aspects of the analysis:

    media_languages: List of languages for OCR to consider.
    theme_color_variant: The color variant used for the generated theme.
    captions_provider: The provider for image captioning (e.g., 'BLIP', 'LLM').
    llm_provider: The provider for the large language model (LLM), which can be used for summaries and captions.
    enable_text_summary: Enable or disable text summarization.
    enable_document_summary: Enable or disable document summarization.
    document_detection_threshold: Confidence threshold for document detection.
    face_detection_threshold: Confidence threshold for face detection.
    enabled_file_modules: List of file modules to enable (e.g., exif data, gps, weather detection).
    enabled_visual_modules: List of visual modules to enable (e.g., 'classification', 'captioning', 'ocr', 'facial_recognition').

Full docs can be found at https://ruurdbijlsma.github.io/media-analyzer.

## Attribution

* Meteostat for weather info: https://dev.meteostat.net/python/
* Reverse geocoding data from geonames: https://download.geonames.org/
* ExifTool for exif and similar data: https://exiftool.org/

## How to publish a release

* Merge to main
* Create tag `git tag 0.3.1`
* Push tag `git push --tags`
* Wait for GitHub action.