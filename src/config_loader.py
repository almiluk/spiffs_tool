import json
import os
import argparse
from typing import Dict, Any
from system_resolver import SystemResolver


class ConfigurationError(Exception):
    pass


class ConfigLoader:
    def __init__(self):
        self.config = {}
        self.resolver = SystemResolver()

    def load_arduino_json(self, path: str = None) -> Dict[str, Any]:
        """Loads configuration from arduino.json if it exists."""
        if not path:
            path = "arduino.json"
            if not os.path.exists(path):
                # Try looking in .vscode/arduino.json as well
                path = os.path.join(".vscode", "arduino.json")
                if not os.path.exists(path):
                    return {}
        elif not os.path.exists(path):
            print(f"Warning: Config file not found at {path}")
            return {}

        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError:
            print(f"Warning: Failed to parse {path}")
            return {}
        except Exception as e:
            print(f"Warning: Error reading {path}: {e}")
            return {}

    def parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description="ESP32 SPIFFS Builder and Flasher"
        )

        # General options
        parser.add_argument(
            "--arduino-config", help="Path to arduino.json configuration file"
        )

        # SPIFFS options
        parser.add_argument(
            "--data-dir",
            default="data",
            help="Directory containing data for SPIFFS",
        )
        parser.add_argument(
            "--page-size", type=int, help="SPIFFS page size (default: 256)"
        )
        parser.add_argument(
            "--block-size", type=int, help="SPIFFS block size (default: 4096)"
        )
        parser.add_argument(
            "--partition-size",
            help="Size of the SPIFFS partition (e.g. 0x10000)",
        )
        parser.add_argument(
            "--partition-offset", help="Offset of the SPIFFS partition"
        )

        # Flashing options
        parser.add_argument("--port", help="Serial port for flashing")
        parser.add_argument(
            "--baud", default="460800", help="Baud rate for flashing"
        )
        parser.add_argument(
            "--chip", default="esp32", help="Chip type (esp32, esp32s2, etc.)"
        )

        # Tool paths
        parser.add_argument("--mkspiffs-path", help="Path to mkspiffs binary")
        parser.add_argument(
            "--esptool-path", help="Path to esptool binary/script"
        )

        # Actions
        parser.add_argument(
            "--build-only", action="store_true", help="Only build the image"
        )
        parser.add_argument(
            "--flash-only", action="store_true", help="Only flash the image"
        )
        parser.add_argument(
            "--image-file",
            default="spiffs.bin",
            help="Path to SPIFFS image file (default: spiffs.bin)",
        )

        return parser.parse_args()

    def merge_config(
        self, args: argparse.Namespace, json_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merges CLI args with JSON config. CLI args take precedence."""

        # Parse 'configuration' string from json_config if present
        json_params = {}
        if "configuration" in json_config:
            try:
                items = json_config["configuration"].split(',')
                for item in items:
                    if '=' in item:
                        k, v = item.split('=', 1)
                        json_params[k.strip()] = v.strip()
            except Exception as e:
                print(f"Warning: Failed to parse configuration string: {e}")

        # Resolve Chip
        json_chip = None
        if "board" in json_config:
            parts = json_config["board"].split(':')
            if len(parts) >= 3:
                json_chip = parts[2]
                if len(parts) >= 2:
                    json_chip = parts[1]

        final_config = {
            "data_dir": args.data_dir,
            "page_size": args.page_size or 256,
            "block_size": args.block_size or 4096,
            "partition_size": args.partition_size,
            "partition_offset": args.partition_offset,
            "port": args.port or json_config.get("port"),
            "baud": args.baud or json_params.get("UploadSpeed", "460800"),
            "chip": args.chip or json_chip or "esp32",
            "mkspiffs_path": args.mkspiffs_path,
            "esptool_path": args.esptool_path,
            "build_only": args.build_only,
            "flash_only": args.flash_only,
            "image_file": args.image_file,
        }

        # Extract PartitionScheme
        partition_scheme = json_params.get("PartitionScheme", "default")

        # Try to find partition file and parse it if size/offset are missing
        if (
            final_config["partition_size"] is None
            or final_config["partition_offset"] is None
        ):
            size, offset = self.resolver.resolve_partition_info(
                partition_scheme
            )
            if size is not None and final_config["partition_size"] is None:
                final_config["partition_size"] = size
            if offset is not None and final_config["partition_offset"] is None:
                final_config["partition_offset"] = offset

        # Validate required fields
        if (
            not final_config["flash_only"]
            and final_config["partition_size"] is None
        ):
            raise ConfigurationError(
                "Partition size could not be determined. Please provide --partition-size or check your partition scheme."
            )

        if (
            not final_config["build_only"]
            and final_config["partition_offset"] is None
        ):
            raise ConfigurationError(
                "Partition offset could not be determined. Please provide --partition-offset or check your partition scheme."
            )

        # Resolve tools if not provided
        if (
            final_config["mkspiffs_path"] is None
            or final_config["esptool_path"] is None
        ):
            mkspiffs, esptool = self.resolver.resolve_tools()
            if final_config["mkspiffs_path"] is None:
                final_config["mkspiffs_path"] = mkspiffs or "mkspiffs"
            if final_config["esptool_path"] is None:
                final_config["esptool_path"] = esptool or "esptool.py"

        return final_config
