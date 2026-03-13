import time
from pathlib import Path

import pyperclip

OUTPUT_FILE = Path("searchword.txt")
POLL_INTERVAL = 1.0

last_value = None

print(f"Watching clipboard. Appending to: {OUTPUT_FILE.resolve()}")
print("Press Ctrl+C to stop.\n")

while True:
    try:
        current = pyperclip.paste()

        if current and current != last_value:
            last_value = current

            with OUTPUT_FILE.open("a", encoding="utf-8") as f:
                f.write(current.strip())
                f.write("\n||\n")

            # print("Appended new clipboard content.")
        time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(POLL_INTERVAL)
