import os
import shutil
from datetime import datetime, date
import calendar
from pathlib import Path

main_dir = Path.cwd()
parent = main_dir.parent


# Get current year and month
now = datetime.now()
year = now.year
month = now.month

# Path to the source file to copy
source_file = "test.txt"

if not os.path.isfile(source_file):
    print(f"Warning: '{source_file}' not found. Directories will be created without copying the file.")

# Get number of days in the current month
_, num_days = calendar.monthrange(year, month)

for day in range(1, num_days + 1):
    current_date = date(year, month, day)

    # weekday(): Monday = 0, Sunday = 6
    if current_date.weekday() < 5:  # 0–4 → Monday–Friday
        date_str = current_date.strftime("%Y%m%d")
        new_dir = os.path.join(parent, f"publication_{date_str}")

        # Create main directory
        os.makedirs(new_dir, exist_ok=True)

        # Create subdirectories
        for sub in ["assets", "video", "cover_photo"]:
            os.makedirs(os.path.join(new_dir, sub), exist_ok=True)

        # Copy test.txt into the main directory (if it exists)
        if os.path.isfile(source_file):
            dest_file = os.path.join(new_dir, os.path.basename(source_file))
            shutil.copy(source_file, dest_file)

        print(f"Created: {new_dir}")


