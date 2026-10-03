from pathlib import Path
import re
import json


INPUT_PATH = Path("knowledge/processed/cn_raw.txt")
OUTPUT_PATH = Path("knowledge/processed/cn_sections.json")


SECTION_PATTERN = re.compile(
    r"^(?P<number>\d+(?:\.\d+)+)\s+(?P<title>.+?)\s*$"
)

PAGE_PATTERN = re.compile(
    r"^===== PAGE (?P<page>\d+) =====$"
)


def parse_sections():
    text = INPUT_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    sections = []
    current_page = None
    current_section = None

    # We only start parsing after the actual Chapter 1 heading.
    content_started = False
    foundation_seen = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Track PDF page numbers.
        page_match = PAGE_PATTERN.match(line)

        if page_match:
            current_page = int(page_match.group("page"))
            continue

        # Detect the actual beginning of Chapter 1.
        if not content_started:
            if line == "CHAPTER":
                foundation_seen = True
                continue

            if foundation_seen and line == "ONE":
                foundation_seen = "ONE"
                continue

            if foundation_seen == "ONE" and line == "FOUNDATION":
                content_started = True
                continue

            continue

        # Detect numbered sections such as:
        # 1.1 Applications
        # 1.1.1 Classes of Applications
        section_match = SECTION_PATTERN.match(line)

        if section_match:
            if current_section:
                current_section["text"] = "\n".join(
                    current_section["text"]
                ).strip()

                sections.append(current_section)

            number = section_match.group("number")
            title = section_match.group("title")

            current_section = {
                "id": f"cn_{number.replace('.', '_')}",
                "number": number,
                "title": title,
                "source_pages": [current_page],
                "text": [],
            }

            continue

        # Add normal content to the current section.
        if current_section:
            if current_page not in current_section["source_pages"]:
                current_section["source_pages"].append(current_page)

            current_section["text"].append(line)

    # Save final section.
    if current_section:
        current_section["text"] = "\n".join(
            current_section["text"]
        ).strip()

        sections.append(current_section)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(sections, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Parsed {len(sections)} sections.")
    print(f"Saved structured sections to: {OUTPUT_PATH}")


if __name__ == "__main__":
    parse_sections()