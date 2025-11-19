.PHONY: pack clean

OUTPUT = spiffs_tool.pyz
SOURCE_DIR = src
ENTRY_POINT = main:main

pack:
	python3 -m zipapp $(SOURCE_DIR) -m "$(ENTRY_POINT)" -o $(OUTPUT) -p "/usr/bin/env python3"
	chmod +x $(OUTPUT)

clean:
	rm -f $(OUTPUT)
