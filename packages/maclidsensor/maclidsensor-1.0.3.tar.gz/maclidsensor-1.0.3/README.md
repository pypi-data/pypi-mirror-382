# MacLidSensor - MacBook Lid Angle Sensor Interface

A lightweight Python module for reading MacBook lid angle sensor data using the HID interface on macOS.
This package provides direct access to the built-in Apple lid angle sensor — no kernel extensions or private APIs required.

[![image](https://img.shields.io/pypi/v/maclidsensor.svg)](https://pypi.python.org/pypi/maclidsensor)

## Features

- **Instant angle readings** — Read the current MacBook lid angle in degrees
- **Minimal dependencies** — Only relies on hidapi
- **Simple class API** — Easy to integrate into scripts or applications

## Requirements

- macOS (tested on Apple Silicon)
- Python 3.7+
- Modern MacBook with lid angle sensor

## Installation

Install via pip:
```bash
pip install maclidsensor
```

## Quick Start

```python
from maclidsensor.sensor import LidSensor

sensor = LidSensor()
angle = sensor.read()
print(f"Lid angle: {angle}°")
```

Output example:
```yaml
Lid angle: 108.0°
```

## Acknowledgements
Based on reverse engineering of the IOKit HID interface used by Apple's internal sensor framework.

This package was made possible by the reverse engineering work done by Sam Henri Gold in the [LidAngleSensor project](https://github.com/samhenrigold/LidAngleSensor). The key insights about the HID Feature Reports and data format were discovered through that original research.

- [Another python library that has more features](https://github.com/tcsenpai/pybooklid)

## License

This project is licensed MIT LICENSE.

See the [LICENSE file](./LICENSE) for full details.


## Contributing

Contributions are welcome! Whether you’ve discovered a new sensor variant, want to improve error handling, or just fix typos — all PRs are appreciated.

### How to Contribute

1. Fork the repository on GitHub

2. Create a new branch for your feature or bug fix

```bash
git checkout -b feature/my-improvement
```

3. Make your changes, ensuring code is clean and concise

4. Run tests or verify the sensor behavior on your MacBook

5. Commit and push your changes:

```bash
git commit -m "Add: Improved connection logic for sensor detection"
git push origin feature/my-improvement
```

6. Open a Pull Request on GitHub and describe your change clearly

### Guidelines

- Keep commits atomic and well-labeled

- Use type hints where applicable

- Avoid breaking public APIs

- Add docstrings for new classes or functions

If you encounter a model that doesn’t work or returns unexpected data, please open an issue and include your:

- macOS version

- MacBook model

- hid.enumerate() output snippet

Your feedback helps improve compatibility across devices.
