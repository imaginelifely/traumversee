from pathlib import Path
import json
import sys

from learner_model import (
    load_model,
    update_model,
    save_model
)


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


def find_experience_by_id(
    experience_id
):
    experience_files = sorted(
        EXPERIENCE_DIR.glob("*.json")
    )

    for experience_path in experience_files:

        experience = load_experience_file(
            experience_path
        )

        if experience.get(
            "experience_id"
        ) == experience_id:

            return experience

    return None


def create_learning_event(
    experience,
    selected_option,
    correct
):
    mastery = experience[
        "mastery_evidence"
    ]

    return {
        "concept_id": experience[
            "concept_id"
        ],
        "experience_id": experience[
            "experience_id"
        ],
        "selected_answer": selected_option[
            "id"
        ],
        "correct": correct,
        "evidence_type": mastery[
            "evidence_type"
        ],
        "mastery_signal": mastery[
            "mastery_signal"
        ]
    }


def present_experience(
    experience
):
    learning_objective = experience[
        "learning_objective"
    ]

    experience_content = experience[
        "experience"
    ]

    assessment = experience[
        "assessment"
    ]

    print()
    print("=" * 60)

    print(
        f"🎮 {experience_content['title']}"
    )

    print("=" * 60)
    print()

    print(
        f"Concept: {experience['concept']}"
    )

    print()

    print(
        "🎯 Learning Objective"
    )

    print(
        learning_objective["statement"]
    )

    print()

    print(
        "📖 Scenario"
    )

    print(
        experience_content["scenario"]
    )

    print()

    print(
        "⚡ Challenge"
    )

    print(
        experience_content["challenge"]
    )

    print()

    print(
        "🧠 Decision"
    )

    print(
        assessment["question"]
    )

    print()

    print(
        "Choose your answer:"
    )

    print()

    options = assessment[
        "options"
    ]

    for index, option in enumerate(
        options,
        start=1
    ):
        print(
            f"[{index}] {option['text']}"
        )

    print()

    while True:

        choice = input(
            f"Your choice (1-{len(options)}): "
        ).strip()

        if (
            choice.isdigit()
            and
            1 <= int(choice) <= len(options)
        ):
            break

        print(
            f"Please choose a number from "
            f"1 to {len(options)}."
        )

    selected_option = options[
        int(choice) - 1
    ]

    correct_answer = assessment[
        "correct_answer"
    ]

    correct = (
        selected_option["id"]
        == correct_answer
    )

    print()

    if correct:

        print("✅ Correct!")

        print()

        print(
            experience[
                "feedback"
            ]["correct"]
        )

        print()

        print(
            experience[
                "feedback"
            ]["explanation"]
        )

        print()

        print(
            "🧠 Mastery evidence:"
        )

        print(
            experience[
                "mastery_evidence"
            ]["mastery_signal"]
        )

    else:

        print("❌ Not quite.")

        print()

        print(
            experience[
                "feedback"
            ]["explanation"]
        )

        print()

        print(
            "💡 Think about the sequence "
            "described in the feedback."
        )

    # -----------------------------------------
    # Create learning event
    # -----------------------------------------

    learning_event = create_learning_event(
        experience,
        selected_option,
        correct
    )

    print()

    print(
        "📊 Learning Event"
    )

    print(
        json.dumps(
            learning_event,
            indent=2,
            ensure_ascii=False
        )
    )

    # -----------------------------------------
    # Update learner model
    # -----------------------------------------

    model = load_model()

    model = update_model(
        model,
        learning_event
    )

    save_model(
        model
    )

    # -----------------------------------------
    # Show updated learner model
    # -----------------------------------------

    concept_state = model[
        "concepts"
    ][
        experience["concept_id"]
    ]

    print()

    print(
        "🧠 Current Learner Model"
    )

    print(
        f"Attempts: "
        f"{concept_state['attempts']}"
    )

    print(
        f"Correct: "
        f"{concept_state['correct']}"
    )

    print(
        f"Incorrect: "
        f"{concept_state['incorrect']}"
    )

    print(
        f"Mastery: "
        f"{concept_state['mastery']:.2f}"
    )

    print()

    print("=" * 60)


def main():

    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "python scripts\\experience_presenter.py "
            "<concept_id_or_experience_id>"
        )

        return

    identifier = " ".join(
        sys.argv[1:]
    )

    # Try concept ID first
    experience = find_experience_by_concept(
        identifier
    )

    # If not found, try experience ID
    if not experience:

        experience = find_experience_by_id(
            identifier
        )

    if not experience:

        print(
            f"No experience found for: "
            f"{identifier}"
        )

        return

    present_experience(
        experience
    )


if __name__ == "__main__":
    main()