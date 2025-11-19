import subprocess
import sys


class Flasher:
    def __init__(self, config):
        self.config = config

    def flash(self):
        """Flashes the SPIFFS image."""
        print("Flashing SPIFFS image...")

        esptool_path = self.config.get("esptool_path", "esptool.py")
        port = self.config.get("port")
        baud = self.config.get("baud", "460800")
        chip = self.config.get("chip", "esp32")
        image_file = self.config.get("image_file", "spiffs.bin")
        partition_offset = self.config.get("partition_offset")

        if not port:
            print(
                "Error: Serial port is required. Please provide --port or ensure it's in arduino.json."
            )
            return False

        if not partition_offset:
            print(
                "Error: Partition offset is required. Please provide --partition-offset."
            )
            return False

        # Construct command
        # esptool.py --chip <chip> --port <port> --baud <baud> write_flash <offset> <image_file>
        cmd = [
            sys.executable,
            esptool_path,  # Assuming esptool_path is a script, if binary, remove sys.executable
        ]

        # If esptool_path is just "esptool" or "esptool.py" and it's in path, we might call it directly.
        # But often it's installed via pip as a script.
        # Let's try to be smart: if it ends in .py, use python to run it. If not, run directly.
        if esptool_path.endswith(".py"):
            cmd = [sys.executable, esptool_path]
        else:
            cmd = [esptool_path]

        cmd.extend(
            [
                "--chip",
                chip,
                "--port",
                port,
                "--baud",
                str(baud),
                "write-flash",
                str(partition_offset),
                image_file,
            ]
        )

        print(f"Running: {' '.join(cmd)}")

        try:
            subprocess.check_call(cmd)
            print("Flashing complete.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running esptool: {e}")
            return False
        except FileNotFoundError:
            print(
                f"Error: esptool binary/script not found at '{esptool_path}'."
            )
            return False
