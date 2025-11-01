#!/usr/bin/env python3
"""
Daily Planner PDF Generator
- Half-hour schedule (6:00 AM – 7:00 PM) with two slim color columns for blocks
- Right column for Date, Top 3 Things, Notes, Habits
- Compact margins, 2-column layout with a small gap
- Fully data-driven: pass values to generate_planner_pdf()

Dependencies: reportlab
    pip install reportlab
"""

import tomllib
import logging
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger(__name__)

# ---------- Helpers ----------

def _hex_to_rgb(hex_code, default=None):
    if not hex_code:
        return default
    h = hex_code.strip().lstrip('#')
    if len(h) not in (3, 6):
        return default
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    try:
        r = int(h[0:2], 16)/255.0
        g = int(h[2:4], 16)/255.0
        b = int(h[4:6], 16)/255.0
        return colors.Color(r, g, b)
    except Exception:
        return default

def _time_range_half_hours(start_h=6, end_h=19):
    """
    Yields times from start_h:00 to end_h:30 inclusive in 30-min steps.
    end_h is the final hour label (e.g., 19 -> 7:30 PM row will be included).
    """
    t = datetime(2000, 1, 1, start_h, 0)
    end = datetime(2000, 1, 1, end_h, 30)
    while t <= end:
        try:
            yield t.strftime("%-I:%M")
        except ValueError:
            # Windows doesn't support -, use %I and strip leading zero
            yield t.strftime("%I:%M").lstrip("0")
        t += timedelta(minutes=30)

def _format_checkbox(checked):
    return "[x]" if checked else "[ ]"

def _parse_schedule_text(schedule_str):
    """Parse a pipe-delimited schedule string into start_time, span, and task_name."""
    parts = [p.strip() for p in schedule_str.split("|")]
    if len(parts) != 3:
        raise ValueError(f"Schedule string must have 3 parts (start_time | span | task_name): {schedule_str}")
    start_time, span_str, task_name = parts
    try:
        span = int(span_str)
    except ValueError:
        raise ValueError(f"Span must be an integer: {span_str}")
    return start_time, span, task_name

def _calculate_end_time(start_time, span):
    """Calculate end time from start time and span (number of 30-min blocks)."""
    time_obj = datetime.strptime(start_time, "%H:%M")
    end_obj = time_obj + timedelta(minutes=30 * span)
    return end_obj.strftime("%H:%M")

# ---------- Core Generator ----------

def generate_planner_pdf(
    output_path="Daily_Planner.pdf",
    date_text="____________________",
    # schedule_texts: dict of "HH:MM" -> string (e.g., "08:00", "08:30", ... in 24h)
    schedule_texts=None,
    # blocks: list of dicts with time ranges and color fills for the two slim columns:
    #   {"start":"08:00","end":"10:30","left_color":"#FFD54F","right_color":"#90CAF9"}
    blocks=None,
    # top 3 priorities
    top_three=None,
    # notes: list of lines or a single string with \n
    notes=None,
    # habits: dict name->bool
    habits=None,
    # layout tuning
    left_margin=0.25*inch,
    right_margin=0.25*inch,
    top_margin=0.25*inch,
    bottom_margin=0.25*inch,
    gap_width=10,  # px gap between columns
    # column widths
    time_col_width=45,
    color_col_width=15,
    text_col_width=190,
    right_col_width=250,
):
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    heading3 = styles["Heading3"]

    # Defaults
    if schedule_texts is None:
        schedule_texts = {}
    if blocks is None:
        blocks = []
    if top_three is None:
        top_three = ["", "", ""]
    if isinstance(notes, str):
        notes_lines = notes.splitlines()
    elif isinstance(notes, list):
        notes_lines = notes
    else:
        notes_lines = [""] * 12
    if habits is None:
        habits = {"Walk": False, "Stretch": False, "Water": False, "10 min sweat": False}

    # Precompute block fills per half-hour row
    # Build a quick lookup for each half-hour stamp -> (left_color, right_color)
    def _hh_to_dt(hhmm):
        return datetime.strptime(hhmm, "%H:%M")

    # Expand blocks into per-row assignment
    row_fills = {}
    for blk in blocks:
        s = _hh_to_dt(blk["start"])
        e = _hh_to_dt(blk["end"])
        # iterate half-hours between s (inclusive) and e (exclusive)
        t = s
        while t < e:
            key = t.strftime("%H:%M")
            left_rgb = _hex_to_rgb(blk.get("left_color"), None)
            right_rgb = _hex_to_rgb(blk.get("right_color"), None)
            row_fills[key] = (left_rgb, right_rgb)
            t += timedelta(minutes=30)

    # Build left schedule table data
    left_rows = []
    # create rows from 06:00 to 19:30
    t = datetime(2000, 1, 1, 6, 0)
    end = datetime(2000, 1, 1, 19, 30)
    while t <= end:
        try:
            label = t.strftime("%-I:%M")
        except ValueError:
            # Windows doesn't support -, use %I and strip leading zero
            label = t.strftime("%I:%M").lstrip("0")
        key24 = t.strftime("%H:%M")
        left_rows.append([label, "", "", schedule_texts.get(key24, "")])
        t += timedelta(minutes=30)

    # Create table
    from reportlab.platypus import Table, TableStyle
    time_table = Table(left_rows, colWidths=[time_col_width, color_col_width, color_col_width, text_col_width])
    style_cmds = [
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    # Apply color fills per row for the two slim columns
    for row_idx in range(len(left_rows)):
        # Recover the 24h key back from label by recomputation:
        # safer: recompute based on index
        t = datetime(2000, 1, 1, 6, 0) + timedelta(minutes=30*row_idx)
        key24 = t.strftime("%H:%M")
        if key24 in row_fills:
            left_col, right_col = row_fills[key24]
            if left_col:
                style_cmds.append(('BACKGROUND', (1, row_idx), (1, row_idx), left_col))
            if right_col:
                style_cmds.append(('BACKGROUND', (2, row_idx), (2, row_idx), right_col))

    time_table.setStyle(TableStyle(style_cmds))

    # Right column
    right_flow = []

    # Date at top-left (we'll place this above the 2-col table when building doc)
    date_para = Paragraph(f"<b>Date:</b> {date_text}", normal)

    # Top 3
    right_flow.append(Paragraph("<b>Top 3 Things</b>", heading3))
    three_rows = [[f"{i+1}.", top_three[i] if i < len(top_three) else ""] for i in range(3)]
    three_table = Table(three_rows, colWidths=[20, right_col_width - 20])
    three_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    right_flow.append(three_table)
    right_flow.append(Spacer(1, 12))

    # Notes
    right_flow.append(Paragraph("<b>Notes</b>", heading3))
    # Ensure at least 10 lines; pad/cut for fit
    target_lines = 12
    lines = (notes_lines + [""] * target_lines)[:target_lines]
    notes_table = Table([[line] for line in lines], colWidths=[right_col_width])
    notes_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    right_flow.append(notes_table)
    right_flow.append(Spacer(1, 12))

    # Habits
    right_flow.append(Paragraph("<b>Habits</b>", heading3))
    habit_rows = [[name, "[x]" if val else "[ ]"] for name, val in habits.items()]
    habit_table = Table(habit_rows, colWidths=[right_col_width - 60, 40])
    habit_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
    ]))
    right_flow.append(habit_table)

    # Two-column container
    two_col = Table([[time_table, "", right_flow]], colWidths=[time_col_width + 2*color_col_width + text_col_width, 10, right_col_width])
    two_col.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))

    # Build PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )
    elements = [date_para, Spacer(1, 6), two_col]
    doc.build(elements)

# ---------- TOML Configuration Loader ----------

def generate_from_toml(toml_path="test_v2_format.toml"):
    """Generate a planner PDF from a TOML configuration file."""
    try:
        toml_file = Path(toml_path)
        
        if not toml_file.exists():
            logger.error(f"TOML file not found: {toml_path}")
            raise FileNotFoundError(f"TOML file not found: {toml_path}")
        
        logger.info(f"Reading configuration from {toml_path}")
        try:
            with open(toml_file, "rb") as f:
                config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            logger.error(f"Invalid TOML syntax in {toml_path}")
            logger.error(f"Error: {str(e)}")
            logger.error("")
            logger.error("Please check the TOML syntax and try again.")
            raise SystemExit(1)
        
        # 1. Derive output_path from toml filename (same directory as TOML file)
        output_path = str(toml_file.with_suffix('.pdf'))
        
        # 2. Date text
        date_text = config.get("date_text", "____________________")
        
        # 3. Parse schedule_texts array
        schedule_texts_raw = config.get("schedule_texts", [])
        schedule_texts_dict = {}
        top_three = []
        blocks = []
        
        # Define color palette for blocks (cycles through these colors)
        color_palette = [
            "#FFF200",  # yellow
            "#B5E61D",  # green
            "#FFAEC9",  # pink
            "#FFC90E",  # orange
            "#ED1C24",  # red
            "#99D9EA",  # blue
            "#FFD54F",  # light yellow
            "#90CAF9",  # light blue
        ]
        
        for idx, schedule_str in enumerate(schedule_texts_raw):
            try:
                start_time, span, task_name = _parse_schedule_text(schedule_str)
                
                # Check if this is a top_three item (starts with "*")
                if task_name.startswith("*"):
                    clean_task_name = task_name[1:].strip()
                    top_three.append(clean_task_name)
                    schedule_texts_dict[start_time] = clean_task_name
                else:
                    schedule_texts_dict[start_time] = task_name
                
                # Calculate end time
                end_time = _calculate_end_time(start_time, span)
                
                # Create block with color from palette (cycle through colors)
                color = color_palette[idx % len(color_palette)]
                blocks.append({
                    "start": start_time,
                    "end": end_time,
                    "left_color": color,
                    "right_color": None
                })
                
            except ValueError as e:
                logger.warning(f"Skipping invalid schedule entry: {e}")
        
        # 4. Notes
        notes = config.get("notes", [])
        
        # 5. Habits - convert array to dict with all False values
        habits_list = config.get("habits", [])
        habits = {habit: False for habit in habits_list}
        
        # Prepare parameters
        params = {
            "output_path": output_path,
            "date_text": date_text,
            "schedule_texts": schedule_texts_dict,
            "blocks": blocks,
            "top_three": top_three,
            "notes": notes,
            "habits": habits,
        }
        
        logger.info(f"Generating PDF: {params['output_path']}")
        generate_planner_pdf(**params)
        logger.info(f"Successfully generated {params['output_path']}")
        
    except SystemExit:
        # TOML parsing error already logged, exit gracefully
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Please check that the file path is correct and try again.")
        raise SystemExit(1)
    except ValueError as e:
        logger.error(f"Invalid data format: {e}")
        logger.error("Please check your TOML file for correct data formats.")
        raise SystemExit(1)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        logger.error("Please check the log file for details.")
        import traceback
        logger.debug(traceback.format_exc())
        raise SystemExit(1)

# ---------- Example Usage ----------

if __name__ == "__main__":
    # Example data
    schedule = {
        "06:00": "Coffee & quiet",
        "08:30": "Strawberry plan",
        "09:00": "Coaching",
        "10:30": "Costume work",
        "12:00": "Lunch + walk",
        "14:00": "Nap",
        "15:00": "Nora time",
        "16:00": "Groceries",
        "16:30": "Groceries",
        "17:00": "Mockups",
        "18:00": "Dinner",
    }

    blocks = [
        {"start": "09:00", "end": "10:30", "left_color": "#FFD54F", "right_color": None},   # Morning session
        {"start": "16:30", "end": "17:30", "left_color": "#90CAF9", "right_color": "#90CAF9"}, # Work session
    ]

    top3 = ["Costume", "Strawberry", "Mockups"]
    notes = [
        "Next Strawberry mtg: 11/12 @ 1 PM",
        "",
        "Grocery list: milk, eggs, berries",
    ]
    habits = {"Walk": True, "Stretch": True, "Water": True, "10 min sweat": False}

    generate_planner_pdf(
        output_path="Daily_Planner_Example.pdf",
        date_text="____________________",
        schedule_texts=schedule,
        blocks=blocks,
        top_three=top3,
        notes=notes,
        habits=habits,
    )
    print("Wrote Daily_Planner_Example.pdf")
