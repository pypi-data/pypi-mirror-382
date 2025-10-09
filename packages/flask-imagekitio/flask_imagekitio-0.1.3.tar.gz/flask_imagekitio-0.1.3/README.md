# Flask-ImageKitIO

Flask-ImageKitIO provides a simple interface to use ImageKitIO API with Flask.

```{warning}
🚧 This package is under heavy development..
```

## Installation

Install the extension with pip:

```bash
pip install flask-imagekitio
```

Install with poetry:

```bash
poetry add flask-imagekitio
```

## Configuration

This are some of the settings available

| Config                  | Description                         | Type | Default |
| ----------------------- | ----------------------------------- | ---- | ------- |
| IMAGEKITIO_URL_ENDPOINT | The ImagekitIO account url endpoint | str  | `None`  |
| IMAGEKITIO_PRIVATE_KEY  | The ImagekitIO Private Key          | str  | `None`  |
| IMAGEKITIO_PUBLIC_KEY   | The ImagekitIO Public Key           | str  | `None`  |

## Usage

Once installed ImagekitIO is easy to use. Let's walk through setting up a basic application. Also please note that this is a very basic guide: we will be taking shortcuts here that you should never take in a real application.

To begin we'll set up a Flask app:

```python
from flask import Flask

from flask_imagekitio import ImagekitIO

app = Flask(__name__)

imagekitio = ImagekitIO()
imagekitio.init_app(app)

result = imagekit.upload_file(data, file.filename)
img_url = imagekit.url({
    'src': result.url,
    'transformation': [
        {
            'width': '600',
            'aspect_ratio': '5-3'
        }
    ]
})
```
