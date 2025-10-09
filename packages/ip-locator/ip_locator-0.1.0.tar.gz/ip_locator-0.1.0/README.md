# IP Locator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![uv](https://img.shields.io/badge/uv-managed-blue.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/jmeiracorbal/ip-locator)

A command-line tool to get detailed geolocation and network information about IP addresses. Discover location, ISP, timezone, coordinates, and other details about any IP address.

## Features

- **IP address geolocation** - Detailed location information for any IP
- **Network information** - ISP, ASN, organization details
- **Geographic data** - Country, city, region, coordinates
- **Timezone information** - Current time, UTC offset, DST status
- **Map integration** - Direct Google Maps link with coordinates
- **Clean interface** - Colored terminal output

## Installation

### Option 1: Install as command-line tool

Install directly from the repository:

```bash
pip install git+https://github.com/jmeiracorbal/ip-locator.git
```

Or clone and install locally:

```bash
git clone https://github.com/jmeiracorbal/ip-locator.git
cd ip-locator
pip install .
```

After installation, run from anywhere:

```bash
ip-locator
```

### Option 2: Download pre-built executable

1. Go to [Releases](https://github.com/jmeiracorbal/ip-locator/releases)
2. Download the executable for your platform:
   - **Linux**: `ip-locator` (binary)
   - **macOS**: `ip-locator` (binary)
   - **Windows**: `ip-locator.exe` (executable)
3. Run directly without installation

**Linux/macOS:**

```bash
chmod +x ip-locator
./ip-locator
```

**Windows:**

```cmd
ip-locator.exe
```

### Option 3: Run with uv (for development)

```bash
git clone https://github.com/jmeiracorbal/ip-locator.git
cd ip-locator
uv run python main.py
```

## Usage

After installation or running the executable, enter an IP address to get detailed information including geolocation, ISP, timezone, and network details.

## Requirements

- Python 3.8 or higher
- Internet connection (for IP lookup API)

## Data Source

This tool uses the [ipwho.is](https://ipwho.is) API to fetch IP address information.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Original author**: [HUNXBYTS](https://github.com/HUNXBYTS)
- **Modified by**: [jmeiracorbal](https://github.com/jmeiracorbal)
- **Based on**: Ghost Tracker tool

## Support

If you run into any issues or have questions:
- Create an issue on GitHub
- Check the [Releases](https://github.com/jmeiracorbal/ip-locator/releases) page for the latest version

---

**Note**: This tool is for educational and legitimate purposes. Respect privacy and use it responsibly.
