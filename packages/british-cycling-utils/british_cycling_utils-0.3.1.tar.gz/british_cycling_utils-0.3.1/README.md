# british-cycling-utils

## About

Python library package to manipulate data exported from British Cycling.
Unofficial and not affiliated.  

## Installation

Install from GitHub, e.g.:

```sh
pip install git+https://github.com/elliot-100/british-cycling-utils
```

I recommend installing a specific version, e.g.:

```sh
pip install git+https://github.com/elliot-100/british-cycling-utils@v0.1.2
```

## Example code

### Load club subscriptions from a CSV previously exported from the BC Club Management Tool

```python
from pathlib import Path

from british_cycling_utils.club_subscription import ClubSubscription


file_path = Path(__file__).parent / "exported.csv"
input_subscriptions_data = ClubSubscription.list_from_bc_csv(file_path)
print(f"Loaded {len(input_subscriptions_data)} subscriptions from CSV.")
```