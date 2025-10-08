# Ambient-WDS (Weather Data Shipper)
*A lightweight Python tool to query data from Ambient Weather's API, convert it, and upload it to [APRS.fi](https://aprs.fi).*
*by Jake Barbieur, N9DMT*

<img src="https://gitlab.com/jake-barbieur/ambient-wds/-/raw/main/images/ambient-wds-logo.png?ref_type=heads" alt="ambient-wds-logo" width="40%">

## Overview
This project started as a proof of concept for [W9PVR](https://w9pvr.org), a ham radio club that recently voted to install a weather station at our D-Star site. While Ambient Weather provides HTML widgets for displaying data on websites, some club members wanted the data sent to aprs.fi, which is widely used in the amateur radio community.

`ambient-wds` is designed to:

- Query data from the Ambient Weather API  
- Format the data appropriately for APRS weather packets  
- Upload the packets to [APRS.fi](https://aprs.fi)

<img src="https://gitlab.com/jake-barbieur/ambient-wds/-/raw/main/images/ambient-wds-flow.png?ref_type=heads" alt="ambient-wds-flow-diagram">

It's a simple, configurable, and lightweight tool, ideal for hams who want their station data online once the station is installed.

## Setup

To get started with `ambient-wds`, make sure you have the following:

### 1. Ambient Weather Station

This tool has been tested with the [WS-2902](https://ambientweather.com/ws-2902-smart-weather-station). Other Ambient Weather models may work but are untested.

**Installation Requirements:**

- Follow the [Ambient Weather Network setup instructions](https://ambientweather.com/faqs/question/view/id/1602/?srsltid=AfmBOory_H5e3tYn7ac9Xg65kUkEacU7vqcynmUxMFYYyohAi1vRsRud) to properly configure and register your station.
- Ensure your station is powered on and connected to the internet.  
- Create an account on the Ambient Weather Network to access your station's data online.
- Set a location for your station. [These instructions](https://ambientweather.com/faqs/question/view/id/2047/?srsltid=AfmBOopk7lzXCvZPrvehDkFvc7z-5se9eF-iYKxHhQnByONaAEl3K-Im) go through that process.

### 2. Python Environment

Ensure you have Python 3.10 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).

### 3. Install `ambient-wds`

Install the package via pip:

`pip install ambient-wds`


## Usage

Once you have installed `ambient-wds` and configured your station and keys, you can run the tool from the command line:

`ambient-wds [parameters]`

### Interactive Setup (Recommended)

To generate a configuration file in your home directory (`~/ambient-wds/config.yaml`) and set up your keys and callsign:

`ambient-wds --setup`

- The tool will prompt you for your Ambient Weather `APP_KEY` and `API_KEY`, your `APRS CALLSIGN`, `SSID`, `server`, and other optional parameters.

- Press Enter to accept the default values for each prompt.

- If a configuration file already exists, you will be prompted before overwriting it.

### Obtaining an APRS Passcode
To obtain an APRS passcode, go to https://apps.magicbug.co.uk/passcode/, and enter your callsign.

### Obtaining an App Key and API Key
To obtain your Ambient Weather App and API keys, log into your Ambient Weather account and navigate to https://ambientweather.net/account/keys. From there you can create both an API key and an APP key. They are both necessary.

### Running ambient-wds

After setup, start polling your weather station and sending data to APRS:

`ambient-wds`

You can override any configuration value using command-line options:

`ambient-wds --poll-seconds 400`

### Running Continuously

`ambient-wds` is designed to run continuously and poll your weather station at the interval you specify (default: every 300 seconds).  

For uninterrupted operation, you can run it in a background terminal, or set it up using your operating system's method for persistent tasks (e.g., systemd, launchd, Task Scheduler). The tool is intended to be fully cross-platform.


### Configuration File
By default, `ambient-wds` reads a YAML configuration file at `~/ambient-wds/config.yaml`.
All parameters in the file can be overridden via environment variables or command-line options.

Example `config.yaml`:
```
APP_KEY: your_app_key_here
API_KEY: your_api_key_here
CALLSIGN: N9DMT
SSID: 13
APRS_PASSCODE: 12345
APRS_SERVER: noam.aprs2.net
APRS_PORT: 14580
POLL_SECONDS: 300
```

## Parameters

This tool supports configuration from four sources, checked in the following priority order:

1. **Command-line options** — Passed with `--kebab-case` flags (e.g., `--app-key my_app_key`).  
2. **Environment variables** — Uppercase snake case (e.g., `APP_KEY=my_app_key`).  
3. **YAML config file (`config.yaml`)** — Keys in uppercase snake case (e.g., `APP_KEY: my_app_key`).  
4. **Default value** (see table)

If a parameter is provided in multiple places, the command-line option will override the environment variable, which will override the YAML config file.  

| Parameter       | CLI Option        | Environment Variable | YAML Config Key | Default Value    | Description                                                    |
|-----------------|-------------------|----------------------|-----------------|------------------|----------------------------------------------------------------|
| API_KEY         | `--api-key`       | `API_KEY`            | `API_KEY`       |                  | Your API key for accessing Ambient Weather's API.              |
| APP_KEY         | `--app-key`       | `APP_KEY`            | `APP_KEY`       |                  | Your application key for accessing Ambient Weather's API.      |
| APRS_PASSCODE   | `--aprs-passcode` | `APRS_PASSCODE`      | `APRS_PASSCODE` |                  | The APRS passcode for your callsign.                           |
| APRS_SERVER     | `--aprs-server`   | `APRS_SERVER`        | `APRS_SERVER`   | `noam.aprs2.net` | The APRS server to connect to (e.g., `noam.aprs2.net`).        |
| APRS_PORT       | `--aprs-port`     | `APRS_PORT`          | `APRS_PORT`     | `14580`          | The port number for the APRS server (e.g., `14580`).           |
| CALLSIGN        | `--callsign`      | `CALLSIGN`           | `CALLSIGN`      |                  | Your APRS callsign.                                            |
| SSID            | `--ssid`          | `SSID`               | `SSID`          | `13`             | The SSID (Secondary Station Identifier) for your APRS station. |
| POLL_SECONDS    | `--poll-seconds`  | `POLL_SECONDS`       | `POLL_SECONDS`  | `300`            | The interval (in seconds) for polling data from the API.       |
| CONFIG_FILE     | `--config-file`   | `CONFIG_FILE`        | N/A             | `config.yaml`    | Path to the YAML config file.                                  |

## License
This project is licensed under the MIT License.
