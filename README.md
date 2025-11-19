# ESP32 SPIFFS CLI Tool

A cross-platform Python command-line tool for building and flashing SPIFFS images for ESP32 microcontrollers. It is designed to integrate seamlessly with VSCode Arduino projects by reading configuration from `arduino.json`.

## Features

- **Automatic Configuration**: Reads project settings (board, port, baud rate) directly from `arduino.json` or `.vscode/arduino.json`.
- **Smart Partition Discovery**: Automatically locates the correct partition scheme CSV in your system's `Arduino15` directory to determine SPIFFS partition size and offset.
- **Tool Auto-Discovery**: Automatically finds `mkspiffs` and `esptool` binaries in your `Arduino15` packages, so you don't need to add them to your PATH.
- **Flexible Overrides**: All configuration parameters can be overridden via CLI arguments.
- **Single-File Executable**: Can be packed into a single `.pyz` file for easy distribution and usage.

## Installation

Download the latest release from the [Releases Page](../../releases).

## Prerequisites

- Python 3.x
- ESP32 board support installed via Arduino CLI (or in Arduino IDE).

## Usage

Once you have the `spiffs_tool.pyz` executable, you can run it directly.

### Help
To see all available options:
```bash
./spiffs_tool.pyz -h
```

### Common Commands

**Build and Flash (Default behavior):**
```bash
./spiffs_tool.pyz
```

**Only Build Image:**
```bash
./spiffs_tool.pyz --build-only
```

**Only Flash Image:**
```bash
./spiffs_tool.pyz --flash-only
```

**Specify Data Directory:**
```bash
./spiffs_tool.pyz --data-dir my_data_folder
```

**Specify Arduino Config File:**
```bash
./spiffs_tool.pyz --arduino-config .vscode/arduino.json
```

**Override Port and Baud Rate:**
```bash
./spiffs_tool.pyz --port /dev/ttyUSB0 --baud 115200
```

**Specify Image File:**
```bash
./spiffs_tool.pyz --image-file my_spiffs.bin
```

## Building from Source

If you want to modify the tool or build it yourself:

### Running from Source
```bash
python3 src/main.py [options]
```

### Building the Executable
You can pack the tool into a single executable file using the provided Makefile:

```bash
make pack
```

This creates `spiffs_tool.pyz` and makes it executable.

## Configuration

The tool prioritizes configuration in the following order:
1.  **CLI Arguments**: Flags like `--port`, `--baud`, `--partition-size` take highest precedence.
2.  **arduino.json**: Settings found in `arduino.json` (e.g., `port`, `configuration` string).
3.  **System Discovery**: Partition tables and tool paths found in the `Arduino15` directory.
4.  **Defaults**: Fallback values (e.g., default baud rate 460800).

## License

[MIT](LICENSE)
