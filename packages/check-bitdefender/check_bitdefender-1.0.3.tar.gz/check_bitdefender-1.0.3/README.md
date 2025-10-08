# 🛡️ Check BitDefender GravityZone

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/lduchosal/check_bitdefender)

A comprehensive **Nagios plugin** for monitoring BitDefender GravityZone for Endpoint API endpoints. Built with modern Python practices and designed for enterprise monitoring environments.

## ✨ Features

- 🔐 **Authentication** - Support for API Token
- 🎯 **Multiple Endpoints** - Monitor onboarding status, last seen, last scan, and endpoint details
- 📊 **Nagios Compatible** - Standard exit codes and performance data output
- 🏗️ **Clean Architecture** - Modular design with testable components
- 🔧 **Flexible Configuration** - File-based configuration with sensible defaults
- 📈 **Verbose Logging** - Multi-level debugging support
- 🐍 **Modern Python** - Built with Python 3.9+ using type hints and async patterns

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment (recommended)
python -m venv /usr/local/libexec/nagios/check_bitdefender
source /usr/local/libexec/nagios/check_bitdefender/bin/activate

# Install from source
pip install git+https://github.com/lduchosal/check_bitdefender.git
```

### Basic Usage

```bash
# List all endpoints
check_bitdefender endpoints

# Check onboarding status
check_bitdefender onboarding -d endpoint.domain.tld

# Check last seen (days since endpoint last connected)
check_bitdefender lastseen -d endpoint.domain.tld

# Check last scan (days since last antivirus scan)
check_bitdefender lastscan -d endpoint.domain.tld

# Get detailed endpoint info
check_bitdefender detail -d endpoint.domain.tld
```

## 📋 Available Commands

| Command | Description | Default Thresholds |
|---------|-------------|-------------------|
| `endpoints` | List all endpoints | W:10, C:25 |
| `onboarding` | Check endpoint onboarding status | W:2, C:1 |
| `lastseen` | Check days since endpoint was last seen | W:7, C:30 |
| `lastscan` | Check days since endpoint was last scanned | W:7, C:30 |
| `detail` | Get detailed endpoint information | - |

### Onboarding Status Values

- `0` - Onboarded ✅
- `1` - InsufficientInfo ⚠️
- `2` - Unknown ❌

## ⚙️ Configuration

### Authentication Setup

Create `check_bitdefender.ini` in your Nagios directory or current working directory:

#### API Token Authentication
```ini
[auth]
token = your-api-token-here

[settings]
timeout = 5
parent_id = your-company-id-here  # Optional: specify company/parent ID
```

### BitDefender GravityZone API Setup

1. **Log into GravityZone Control Center**
2. **Navigate to My Account > API Keys**
3. **Generate a new API key** with appropriate permissions
4. **Copy the API token** to your configuration file

📚 [Complete API Setup Guide](https://www.bitdefender.com/business/support/en/77209-370443-gravityzone.html)

## 🔧 Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `-c, --config` | Configuration file path | `-c /custom/path/config.ini` |
| `-m, --endpointId` | Endpoint ID (GUID) | `-m "12345678-1234-1234-1234-123456789abc"` |
| `-d, --computerDnsName` | Computer DNS Name (FQDN) | `-d "server.domain.com"` |
| `-W, --warning` | Warning threshold | `-W 10` |
| `-C, --critical` | Critical threshold | `-C 100` |
| `-v, --verbose` | Verbosity level | `-v`, `-vv`, `-vvv` |
| `--version` | Show version | `--version` |

## 🏢 Nagios Integration

### Command Definitions

```cfg
# BitDefender GravityZone Commands
define command {
    command_name    check_bitdefender_onboarding
    command_line    $USER1$/check_bitdefender/bin/check_bitdefender onboarding -d $HOSTALIAS$
}

define command {
    command_name    check_bitdefender_lastseen
    command_line    $USER1$/check_bitdefender/bin/check_bitdefender lastseen -d $HOSTALIAS$ -W 7 -C 30
}

define command {
    command_name    check_bitdefender_lastscan
    command_line    $USER1$/check_bitdefender/bin/check_bitdefender lastscan -d $HOSTALIAS$ -W 7 -C 30
}

```

### Service Definitions

```cfg
# BitDefender GravityZone Services
define service {
    use                     generic-service
    service_description     BITDEFENDER_ONBOARDING
    check_command           check_bitdefender_onboarding
    hostgroup_name          bitdefender
}

define service {
    use                     generic-service
    service_description     BITDEFENDER_LASTSEEN
    check_command           check_bitdefender_lastseen
    hostgroup_name          bitdefender
}

define service {
    use                     generic-service
    service_description     BITDEFENDER_LASTSCAN
    check_command           check_bitdefender_lastscan
    hostgroup_name          bitdefender
}

```

## 🏗️ Architecture

This plugin follows **clean architecture** principles with clear separation of concerns:

```
check_bitdefender/
├── 📁 cli/                     # Command-line interface
│   ├── commands/               # Individual command handlers
│   │   ├── endpoints.py        # List endpoints command
│   │   ├── onboarding.py       # Onboarding status command
│   │   ├── lastseen.py         # Last seen command
│   │   ├── lastscan.py         # Last scan command
│   │   └── detail.py           # Endpoint detail command
│   └── decorators.py           # Common CLI decorators
├── 📁 core/                    # Core business logic
│   ├── auth.py                 # Authentication management
│   ├── config.py               # Configuration handling
│   ├── defender.py             # BitDefender API client
│   ├── exceptions.py           # Custom exceptions
│   └── nagios.py               # Nagios plugin framework
├── 📁 services/                # Business services
│   ├── endpoint_service.py     # Endpoints business logic
│   ├── onboarding_service.py   # Onboarding check logic
│   ├── lastseen_service.py     # Last seen check logic
│   ├── lastscan_service.py     # Last scan check logic
│   ├── detail_service.py       # Detail retrieval logic
│   └── models.py               # Data models
└── 📁 tests/                   # Comprehensive test suite
    ├── unit/                   # Unit tests
    └── integration/            # Integration tests
```

### Key Design Principles

- **🎯 Single Responsibility** - Each module has one clear purpose
- **🔌 Dependency Injection** - Easy testing and mocking
- **🧪 Testable** - Comprehensive test coverage
- **📈 Extensible** - Easy to add new commands and features
- **🔒 Secure** - No secrets in code, proper credential handling

## 🧪 Development

### Development Setup

```bash
# Clone repository
git clone https://github.com/lduchosal/check_bitdefender.git
cd check_bitdefender

# Create development environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Code Quality Tools

```bash
# Format code
black check_bitdefender/

# Lint code
flake8 check_bitdefender/

# Type checking
mypy check_bitdefender/

# Run tests
pytest tests/ -v --cov=check_bitdefender
```

### Building & Publishing

```bash
# Build package
python -m build

# Test installation
pip install dist/*.whl

# Publish to PyPI
python -m twine upload dist/*
```

## 🔍 Output Examples

### Successful Check
```
DEFENDER OK - Onboarding status: 0 (Onboarded) | onboarding=0;1;2;0;2
```

### Warning State
```
DEFENDER WARNING - Last seen: 10 days ago | lastseen=10;7;30;0;
```

### Critical State
```
DEFENDER CRITICAL - Last scan: 35 days ago | lastscan=35;7;30;0;
```

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Authentication Errors** | Verify BitDefender GravityZone API token |
| **Network Connectivity** | Check firewall rules for cloudgz.gravityzone.bitdefender.com |
| **Import Errors** | Ensure all dependencies are installed |
| **Configuration Issues** | Validate config file syntax and paths |

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
# Maximum verbosity
check_bitdefender lastseen -d endpoint.domain.tld -vvv

# Check specific configuration
check_bitdefender onboarding -c /path/to/config.ini -d endpoint.domain.tld -vv
```

### Required Network Access

Ensure connectivity to:
- `cloudgz.gravityzone.bitdefender.com`

## 📊 Exit Codes

| Code | Status | Description |
|------|--------|-------------|
| `0` | OK | Value within acceptable range |
| `1` | WARNING | Value exceeds warning threshold |
| `2` | CRITICAL | Value exceeds critical threshold |
| `3` | UNKNOWN | Error occurred during execution |

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow [PEP 8](https://pep8.org/) style guide
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [nagiosplugin](https://nagiosplugin.readthedocs.io/) framework
- Powered by [Click](https://click.palletsprojects.com/) for CLI interface
- Integrates with [BitDefender GravityZone API](https://www.bitdefender.com/business/support/en/77209-370443-gravityzone.html)

---

<div align="center">

**[⭐ Star this repository](https://github.com/lduchosal/check_bitdefender)** if you find it useful!

[🐛 Report Bug](https://github.com/lduchosal/check_bitdefender/issues) • [💡 Request Feature](https://github.com/lduchosal/check_bitdefender/issues) • [📖 Documentation](https://github.com/lduchosal/check_bitdefender/blob/main/README.md)

</div>