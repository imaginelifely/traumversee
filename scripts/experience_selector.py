from pathlib import Path
import json
import sys


MODEL_PATH = Path(
    "knowledge/processed/learner_model.json"
)

EXPERIENCE_DIR = Path(
    "knowledge/concepts/cn/experience_specs"
)


def load_json(path):

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def get_concept_state(
    concept_id,
    model
):

    return model.get(
        "concepts",
        {}
    ).get(
        concept_id
    )


def determine_status(
    concept_state
):

    if not concept_state:

        return "new"

    mastery = concept_state[
        "mastery"
    ]

    if mastery < 0.5:

        return "needs_reinforcement"

    elif mastery < 0.8:

        return "developing"

    return "mastered"


def find_experience(
    concept_id
):

    for path in sorted(
        EXPERIENCE_DIR.glob("*.json")
    ):

        experience = load_json(path)

        if experience.get(
            "concept_id"
        ) == concept_id:

            return experience

    return None


def select_experience(
    concept_id,
    model
):

    concept_state = get_concept_state(
        concept_id,
        model
    )

    status = determine_status(
        concept_state
    )

    experience = find_experience(
        concept_id
    )

    if not experience:

        return {
            "concept_id": concept_id,
            "status": status,
            "next_action": "no_experience_available"
        }

    if status == "new":

        next_action = "introduce"

    elif status == "needs_reinforcement":

        next_action = "reinforce"

    elif status == "developing":

        next_action = "practice"

    else:

        next_action = "progress"

    return {
        "concept_id": concept_id,
        "concept": experience[
            "concept"
        ],
        "experience_id": experience[
            "experience_id"
        ],
        "title": experience[
            "experience"
        ]["title"],
        "status": status,
        "next_action": next_action
    }


def main():

    if len(sys.argv) < 2:

        print(
            "Usage: "
            "python scripts\\experience_selector.py "
            "<concept_id>"
        )

        return

    concept_id = sys.argv[1]

    if not MODEL_PATH.exists():

        print(
            "Learner model not found."
        )

        return

    model = load_json(
        MODEL_PATH
    )

    result = select_experience(
        concept_id,
        model
    )

    print()

    print(
        "=" * 60
    )

    print(
        "🎯 Traumverse Experience Selector"
    )

    print(
        "=" * 60
    )

    print()

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )

    print()

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()