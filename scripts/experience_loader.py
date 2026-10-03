from pathlib import Path
import json
import sys


EXPERIENCE_DIR = Path(
    "knowledge/concepts/cn/experience_specs"
)


def load_experience_file(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Experience file not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def find_experience_by_concept(
    concept_id
):
    experience_files = sorted(
        EXPERIENCE_DIR.glob("*.json")
    )

    for experience_path in experience_files:

        experience = load_experience_file(
            experience_path
        )

        if experience.get(
            "concept_id"
        ) == concept_id:

            return experience

    return None


def main():

    if len(sys.argv) < 2:

        print(
            "Usage: "
            "python scripts\\experience_loader.py "
            "<concept_id>"
        )

        print()

        print(
            "Example:"
        )

        print(
            "python scripts\\experience_loader.py "
            "cn_packet_switching"
        )

        return

    concept_id = sys.argv[1]

    experience = find_experience_by_concept(
        concept_id
    )

    if not experience:

        print(
            f"No experience found for concept: "
            f"{concept_id}"
        )

        return

    print(
        json.dumps(
            experience,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()