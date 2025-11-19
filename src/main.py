import sys
from config_loader import ConfigLoader, ConfigurationError
from spiffs_builder import SpiffsBuilder
from flasher import Flasher


def main():
    loader = ConfigLoader()

    try:
        # 1. Parse CLI args
        args = loader.parse_args()

        # 2. Load arduino.json (optional)
        json_config = loader.load_arduino_json(args.arduino_config)

        # 3. Merge config
        config = loader.merge_config(args, json_config)
    except ConfigurationError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # 4. Execute actions
    if not config["flash_only"]:
        builder = SpiffsBuilder(config)
        if not builder.build():
            sys.exit(1)

    if not config["build_only"]:
        flasher = Flasher(config)
        if not flasher.flash():
            sys.exit(1)


if __name__ == "__main__":
    main()
