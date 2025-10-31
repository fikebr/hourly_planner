i want to develop a new format for the toml document that gets parsed and then converted into the parameters for the generate_planner_pdf function in core.planner_generator.

1) output_path: instead of the output_path in the toml i want the generate_from_toml function to derive the name from the toml file itself. the output pdf should be named exactly like the toml but with a pdf extension.

2) date_text: this is the same as v1

3) schedule: the schedule will be an array of strings that are pipe delimited.

schedule_texts = [
    "06:00 | 2 | mourning routine",
    "07:00 | 2 | breakfast",
    "08:00 | 7 | *Costume Work"
]

where the...
1st element is the start time (start_time)
2nd element is the number of blocks it span. ex. 2 = 1 hour or 2 blocks (span)
3rd element is the task element. if there is a "*" prefix then this is also one of the top_three items. (task_name)

4) blocks

the right col of blocks will not get set from the toml.

the left col will derive it's definition from the "schedule_texts" section.
the generate_from_toml will have a list of colors and the color of the block_section will be taken from that list.
each block_group will get it's start from the "start_time" of "schedule_texts".
the end time relates to the "span" of the "task" (example if the start_time is 06:00 and the span is 2 then the end time is 07:00)

4) notes: the notes section will come from the toml "notes" section

notes = [
    "Next Strawberry mtg: 11/12 @ 1 PM",
    "Grocery list: milk, eggs, berries"
]

5) habits: the habits will always be false or unchecked.

habits = [
    "Walk",
    "Stretch",
    "Water x3",
    "10 min sweat"
]


-----

# Date text to display at the top
date_text = "_Fri 10/31 Halloween_"

schedule_texts = [
    "06:00 | 2 | mourning routine",
    "07:00 | 2 | breakfast",
    "08:00 | 7 | *Costume Work"
]

notes = [
    "Next Strawberry mtg: 11/12 @ 1 PM",
    "Grocery list: milk, eggs, berries"
]

habits = [
    "Walk",
    "Stretch",
    "Water x3",
    "10 min sweat"
]
