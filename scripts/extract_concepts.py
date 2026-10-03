from pathlib import Path
import json


INPUT_PATH = Path("knowledge/processed/cn_sections.json")
OUTPUT_DIR = Path("knowledge/concepts/cn")


def load_sections():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Section file not found: {INPUT_PATH}"
        )

    return json.loads(
        INPUT_PATH.read_text(encoding="utf-8")
    )


def create_concept_candidate(section):
    """
    Create a conservative concept candidate from a source section.

    This first version does NOT use an LLM.
    It preserves the source section as the factual basis.
    """

    return {
        "id": f"candidate_{section['id']}",
        "subject": "computer_networks",
        "name": section["title"],
        "type": "concept_candidate",

        "source_claims": [
            {
                "id": f"{section['id']}_source",
                "statement": section["text"],
                "source_section": section["number"],
                "source_title": section["title"],
                "source_pages": section["source_pages"]
            }
        ],

        "inferences": [],

        "experience": {
            "hooks": [],
            "scenarios": [],
            "practical_extension": None
        },

        "learner_model": {
            "mastery": None,
            "confidence": None,
            "misconceptions": [],
            "evidence": []
        },

        "source": {
            "section": section["number"],
            "section_title": section["title"],
            "pages": section["source_pages"]
        },

        "traceability": {
            "source_verified": True,
            "generated_content": []
        }
    }


def main():
    sections = load_sections()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    created = 0

    for section in sections:
        concept = create_concept_candidate(section)

        output_path = (
            OUTPUT_DIR
            / f"{section['id']}.json"
        )

        output_path.write_text(
            json.dumps(
                concept,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        created += 1

    print(f"Created {created} concept candidates.")
    print(f"Saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()