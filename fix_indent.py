import re

file_path = "c:/Users/pujar/OneDrive/Desktop/AgriShield-TN/app/pages/2_Analyze_Leaf.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "# ── 1. RESULT HEADER CARD ─────────────────────────────────────────────"
end_marker = "# ── 4. VISUAL ANALYSIS (expander) ─────────────────────────────────────"

part1, rest = content.split(start_marker, 1)
middle, part2 = rest.split(end_marker, 1)

# Using a regex to capture f'''...''' blocks and applying textwrap.dedent
import textwrap

def dedent_match(m):
    return "f'''" + textwrap.dedent(m.group(1)) + "'''"

middle_fixed = re.sub(r"f'''(.*?)'''", dedent_match, middle, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(part1 + start_marker + middle_fixed + end_marker + part2)

print("Fixed indentation.")
