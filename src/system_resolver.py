import os
from typing import Tuple, Optional


class SystemResolver:
    def __init__(self):
        self.arduino_home = self._find_arduino_home()

    def _find_arduino_home(self) -> Optional[str]:
        """Locates the Arduino15 directory."""
        home = os.path.expanduser("~")
        possible_paths = [
            os.path.join(home, "Library", "Arduino15"),  # macOS
            os.path.join(home, ".arduino15"),  # Linux
            os.path.join(home, "AppData", "Local", "Arduino15"),  # Windows
        ]

        for p in possible_paths:
            if os.path.exists(p):
                return p
        return None

    def resolve_partition_info(
        self, scheme: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Locates and parses the partition CSV file."""
        if not self.arduino_home:
            print("Warning: Could not locate Arduino15 directory.")
            return None, None

        # Find esp32 package tools
        base_path = os.path.join(
            self.arduino_home, "packages", "esp32", "hardware", "esp32"
        )
        if not os.path.exists(base_path):
            print(f"Warning: ESP32 package not found at {base_path}")
            return None, None

        # Get version
        try:
            versions = [
                v
                for v in os.listdir(base_path)
                if not v.startswith('.')
                and os.path.isdir(os.path.join(base_path, v))
            ]
            if not versions:
                return None, None
            versions.sort(reverse=True)
            version = versions[0]
        except OSError:
            return None, None

        partitions_dir = os.path.join(
            base_path, version, "tools", "partitions"
        )
        csv_path = os.path.join(partitions_dir, f"{scheme}.csv")

        if not os.path.exists(csv_path):
            print(f"Warning: Partition file not found: {csv_path}")
            return None, None

        return self._parse_partition_csv(csv_path)

    def _parse_partition_csv(
        self, csv_path: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Parses the CSV to find spiffs partition."""
        try:
            with open(csv_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 5:
                        name = parts[0]
                        subtype = parts[2]
                        if name == "spiffs" or subtype == "spiffs":
                            offset = parts[3]
                            size = parts[4]
                            return size, offset
        except Exception as e:
            print(f"Warning: Error parsing {csv_path}: {e}")

        return None, None

    def resolve_tools(self) -> Tuple[Optional[str], Optional[str]]:
        """Locates mkspiffs and esptool in Arduino15 packages."""
        if not self.arduino_home:
            return None, None

        packages_path = os.path.join(
            self.arduino_home, "packages", "esp32", "tools"
        )

        mkspiffs_path = None
        esptool_path = None

        # Find mkspiffs
        mkspiffs_base = os.path.join(packages_path, "mkspiffs")
        if os.path.exists(mkspiffs_base):
            try:
                versions = sorted(os.listdir(mkspiffs_base), reverse=True)
                if versions:
                    mkspiffs_path = os.path.join(
                        mkspiffs_base, versions[0], "mkspiffs"
                    )
            except OSError:
                pass

        # Find esptool
        esptool_base = os.path.join(packages_path, "esptool_py")
        if os.path.exists(esptool_base):
            try:
                versions = sorted(os.listdir(esptool_base), reverse=True)
                if versions:
                    esptool_path = os.path.join(
                        esptool_base, versions[0], "esptool.py"
                    )
            except OSError:
                pass

        return mkspiffs_path, esptool_path
