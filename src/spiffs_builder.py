import subprocess
import os
import sys


class SpiffsBuilder:
    def __init__(self, config):
        self.config = config

    def build(self):
        """Builds the SPIFFS image."""
        print("Building SPIFFS image...")

        mkspiffs_path = self.config.get("mkspiffs_path", "mkspiffs")
        data_dir = self.config.get("data_dir", "data")
        out_file = self.config.get("out_file", "spiffs.bin")
        page_size = self.config.get("page_size", 256)
        block_size = self.config.get("block_size", 4096)
        partition_size = self.config.get("partition_size")

        if not partition_size:
            print(
                "Error: Partition size is required. Please provide --partition-size or ensure it's in the config."
            )
            return False

        if not os.path.exists(data_dir):
            print(f"Error: Data directory '{data_dir}' not found.")
            return False

        # Construct command
        # mkspiffs -c <data_dir> -p <page_size> -b <block_size> -s <partition_size> <out_file>
        cmd = [
            mkspiffs_path,
            "-c",
            data_dir,
            "-p",
            str(page_size),
            "-b",
            str(block_size),
            "-s",
            str(partition_size),
            out_file,
        ]

        print(f"Running: {' '.join(cmd)}")

        try:
            subprocess.check_call(cmd)
            print(f"SPIFFS image created: {out_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running mkspiffs: {e}")
            return False
        except FileNotFoundError:
            print(
                f"Error: mkspiffs binary not found at '{mkspiffs_path}'. Please check the path."
            )
            return False
