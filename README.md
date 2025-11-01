# Hourly Planner PDF Generator

A Python tool for generating customizable daily planner PDFs with half-hour time slots, color-coded blocks, and sections for priorities, notes, and habit tracking.

## Features

- **Half-hour schedule** from 6:00 AM to 7:30 PM
- **Two slim color columns** for visual time blocking
- **Right sidebar** with:
  - Date field
  - Top 3 priorities
  - Notes section (12 lines)
  - Habit checklist
- **Fully data-driven** - pass all content as parameters
- **Color-coded time blocks** using hex colors
- **Compact layout** optimized for letter-size paper
- **Cross-platform** Windows, macOS, and Linux support

## Installation

This project uses `uv` for Python package management.

```bash
# Install dependencies
uv sync
```

## Usage

### Using TOML Configuration Files (Recommended)

The easiest way to generate planners is using TOML configuration files.

Create a TOML file with this format:

```toml
# Date text to display at the top
date_text = "_Fri 10/31 Halloween_"

# Schedule texts - pipe-delimited format: start_time | span | task_name
# span = number of 30-minute blocks (e.g., 2 = 1 hour)
# task_name with "*" prefix will be added to top_three
schedule_texts = [
    "06:00 | 2 | Morning routine",
    "07:00 | 2 | Breakfast",
    "08:00 | 7 | *Costume Work",
    "11:30 | 2 | *Lunch + walk",
    "13:00 | 1 | CVS & Ribbon",
    "15:00 | 2 | *Mockup"
]

# Notes section
notes = [
    "Next Strawberry mtg: 11/12 @ 1 PM",
    "Grocery list: milk, eggs, berries"
]

# Habits to track (will all be unchecked)
habits = [
    "Walk",
    "Stretch",
    "Water x3",
    "10 min sweat"
]
```

**Key features:**
- Output PDF filename automatically derived from TOML filename (e.g., `2025-10-31.toml` → `2025-10-31.pdf`)
- Schedule entries are pipe-delimited: `start_time | span | task_name`
- Tasks with `*` prefix automatically added to "Top 3 Things"
- Color blocks automatically generated and cycled through a color palette
- Habits are always unchecked (ready to track)

### Running with TOML

#### Direct Python Execution

```bash
# Generate from TOML file
uv run python main.py -t your_schedule.toml

# Example
uv run python main.py -t 2025-10-31.toml

# View help
uv run python main.py --help
```

#### Windows Batch Script (Convenient)

For Windows users, a batch script `hourly.bat` is provided for easier execution:

**Setup:**
1. Copy `hourly.bat` to a folder in your system PATH
2. Edit the batch file to update the project path if different from `E:\Dropbox\Dev\Projects\Life Projects\hourly_planner`

**Usage:**
```cmd
# Navigate to your TOML files directory
cd E:\Dropbox\daily_planner

# Run the planner
hourly 2025-10-31.toml

# The PDF will be generated in the same directory as the TOML file
```

The batch script handles:
- Locating the TOML file in your current directory
- Switching to the project directory
- Running the planner with the correct paths
- Returning to your original directory

### Python API Example

You can also use the Python API directly:

```python
from core.planner_generator import generate_planner_pdf

generate_planner_pdf(
    output_path="My_Planner.pdf",
    date_text="____________________",
    schedule_texts={
        "06:00": "Coffee",
        "08:30": "Morning routine",
        "09:00": "Work session",
    },
    blocks=[
        {"start": "09:00", "end": "10:30", "left_color": "#FFD54F", "right_color": None},
    ],
    top_three=["Task 1", "Task 2", "Task 3"],
    notes=["Note 1", "Note 2"],
    habits={"Walk": True, "Stretch": False},
)
```

## Color Palette

The TOML format automatically cycles through these colors for schedule blocks:

1. `#FFF200` - Yellow
2. `#B5E61D` - Green
3. `#FFAEC9` - Pink
4. `#FFC90E` - Orange
5. `#ED1C24` - Red
6. `#99D9EA` - Blue
7. `#FFD54F` - Light Yellow
8. `#90CAF9` - Light Blue

## Configuration Options

### Parameters

- **`output_path`** (str): Output PDF filename
- **`date_text`** (str): Date to display at the top
- **`schedule_texts`** (dict): Map of "HH:MM" (24-hour format) to text labels
- **`blocks`** (list): Time blocks with color fills
  - `start`: Start time in "HH:MM" format (24-hour)
  - `end`: End time in "HH:MM" format (24-hour)
  - `left_color`: Hex color for left column (e.g., "#FFD54F")
  - `right_color`: Hex color for right column (or None)
- **`top_three`** (list): List of 3 priority items
- **`notes`** (list or str): Notes section content
- **`habits`** (dict): Habit names mapped to bool (checked/unchecked)

### Layout Options

- **`left_margin`**, **`right_margin`**, **`top_margin`**, **`bottom_margin`**: Page margins
- **`gap_width`**: Gap between left and right columns
- **`time_col_width`**: Width of time label column
- **`color_col_width`**: Width of color block columns
- **`text_col_width`**: Width of schedule text column
- **`right_col_width`**: Width of right sidebar

## Example TOML File

Create a TOML file with your daily schedule. See the format specification in `docs/toml_format_v2.md` for details.

## Project Structure

```
hourly_planner/
├── core/
│   └── planner_generator.py      # Main PDF generation logic
├── docs/
│   └── toml_format_v2.md         # TOML format specification
├── main.py                        # Main entry point
├── hourly.bat                     # Windows batch script (optional)
├── pyproject.toml                 # Project dependencies
└── README.md                      # This file
```

## Requirements

- Python >= 3.12
- reportlab >= 4.4.4
- tomli >= 0.10.2 (for TOML parsing)

## Troubleshooting

### TOML Parsing Errors

If you get a TOML parsing error, check these common issues:

1. **Arrays must use proper TOML syntax:**
   ```toml
   # CORRECT
   schedule_texts = [
       "06:00 | 2 | Task",
       "07:00 | 1 | Task2"
   ]
   ```

2. **Strings must be quoted:**
   ```toml
   # CORRECT
   notes = ["Note 1", "Note 2"]
   
   # WRONG
   notes = [Note 1, Note 2]
   ```

3. **Array items must be comma-separated:**
   ```toml
   # CORRECT
   habits = ["Walk", "Stretch"]
   
   # WRONG
   habits = ["Walk" "Stretch"]
   ```

### Time Format

- All times must be in 24-hour format: `HH:MM` (e.g., `"06:00"`, `"14:30"`, `"19:00"`)
- Valid time range: 06:00 to 19:30 (6:00 AM to 7:30 PM)

### Span Calculation

The `span` is the number of 30-minute blocks:
- `span = 1` → 30 minutes
- `span = 2` → 1 hour
- `span = 4` → 2 hours
- `span = 7` → 3.5 hours

## License

[Add your license here]

