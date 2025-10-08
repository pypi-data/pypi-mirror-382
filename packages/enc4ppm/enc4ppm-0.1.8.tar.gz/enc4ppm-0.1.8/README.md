# Encoding For Predictive Process Monitoring (enc4ppm)

`enc4ppm` is a Python package than provides common process mining encodings.

[Documentation and reference](https://rgraziosi-fbk.github.io/enc4ppm/).

## Features

- Frequency, simple-index and complex-index encodings
- Next activity, remaining time and outcome labelings
- Save encoder to disk for later use
- Freeze encoder on training set, then use it on unseen data (automatic handling of unknown values)
- Standardize numerical features
- Convert categorical features to one-hot encoding, or keep them as strings
- Add time features (time since case start and time since last event) to the encoding

## Installation

Using pip:

```bash
pip install enc4ppm
```

## Example

The following example performs frequency encoding with latest payload for next activity prediction task:

```python
import pandas as pd

from enc4ppm.frequency_encoder import FrequencyEncoder
from enc4ppm.constants import LabelingType

# Load log
log = pd.read_csv('bpic2012.csv')

# Create encoder
encoder = FrequencyEncoder(
    labeling_type=LabelingType.NEXT_ACTIVITY,
    include_latest_payload=True,
    attributes=['AMOUNT_REQ'],
)

# Encode log
encoded_log = encoder.encode(log)
```

## Development

### Documentation

Documentation is provided by mkdocs. To build and push the documentation website to GitHub, run the following command: `mkdocs gh-deploy`.

## License

MIT License
