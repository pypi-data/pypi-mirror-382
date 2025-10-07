# DataIdea

A Python package to simplify common data analysis tasks and workflows.

## Overview

DataIdea provides utilities for data analysts to streamline repetitive tasks in the data analysis process. It builds upon popular libraries like pandas, numpy, and scikit-learn to offer a more user-friendly interface for common operations.

## Features

- **Dataset Management**: Easily load built-in datasets or your own custom data
- **Model Persistence**: Simple functions to save and load machine learning models
- **Performance Monitoring**: Time your function execution with the `timer` decorator
- **Logging Utilities**: Log events and LLM interactions via our API
- **YouTube Integration**: Download video data for analysis

## Installation

```bash
pip install dataidea
```

For development:
```bash
git clone https://github.com/dataideaorg/dataidea.git
cd dataidea
poetry install
```

## Quick Start

```python
import dataidea as di

# Load a built-in dataset
df = di.load_dataset('titanic')

# Save a machine learning model
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier().fit(X, y)
di.save_model(model, 'model.di')

# Load the model
loaded_model = di.load_model('model.di')

# Time a function
from dataidea.utils import timer
@timer
def process_data(data):
    return processed_data

# Download YouTube video
from dataidea.io import download_youtube
download_youtube(url="https://www.youtube.com/watch?v=example", output_folder="videos")
```

## Available Datasets

DataIdea includes datasets for practice: `titanic`, `boston`, `fpl`, `mall`, `air_passengers`, `melbourne`, and more.

## Documentation

For detailed documentation, visit [https://docs.dataidea.org](https://docs.dataidea.org).

## License

MIT License