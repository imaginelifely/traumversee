from pathlib import Path
import json


MODEL_PATH = Path(
    "knowledge/processed/learner_model.json"
)

CONCEPT_ID = "cn_packet_switching"


def load_model():

    if not MODEL_PATH.exists():

        return {
            "learner_id": "local_user",
            "concepts": {}
        }

    return json.loads(
        MODEL_PATH.read_text(
            encoding="utf-8"
        )
    )


def get_mastery(
    model,
    concept_id
):

    concept = model.get(
        "concepts",
        {}
    ).get(
        concept_id
    )

    if not concept:
        return None

    return concept["mastery"]


def run_experience(
    concept_id
):

    from experience_presenter import (
        find_experience_by_concept,
        present_experience
    )

    experience = find_experience_by_concept(
        concept_id
    )

    if not experience:

        print(
            f"No experience found for concept: "
            f"{concept_id}"
        )

        return None

    print()
    print(
        "🚀 Starting Traumverse experience..."
    )
    print()

    present_experience(
        experience
    )

    return experience


def run_selector(
    concept_id
):

    from experience_selector import (
        select_experience
    )

    model = load_model()

    return select_experience(
        concept_id,
        model
    )


def main():

    print()
    print("=" * 60)
    print("🌌 TRAUMVERSE")
    print("=" * 60)
    print()

    print(
        "Welcome to your learning experience."
    )

    print(
        "Today's concept: Packet Switching"
    )

    print()

    # -----------------------------------------
    # Load learner model
    # -----------------------------------------

    model = load_model()

    mastery_before = get_mastery(
        model,
        CONCEPT_ID
    )

    if mastery_before is None:

        print(
            "🆕 This is your first encounter "
            "with this concept."
        )

    else:

        print(
            f"🧠 Current mastery: "
            f"{mastery_before:.2f}"
        )

    print()

    input(
        "Press ENTER to begin..."
    )

    # -----------------------------------------
    # Present experience
    # -----------------------------------------

    experience = run_experience(
        CONCEPT_ID
    )

    if experience is None:
        return

    # -----------------------------------------
    # Reload learner model
    # -----------------------------------------

    model_after = load_model()

    mastery_after = get_mastery(
        model_after,
        CONCEPT_ID
    )

    print()
    print(
        "🔄 Traumverse is adapting..."
    )

    print()

    if mastery_after is not None:

        print(
            f"Updated mastery: "
            f"{mastery_after:.2f}"
        )

    print()

    # -----------------------------------------
    # Select next experience
    # -----------------------------------------

    next_experience = run_selector(
        CONCEPT_ID
    )

    print(
        "🎯 Next Learning Decision"
    )

    print()

    print(
        json.dumps(
            next_experience,
            indent=2,
            ensure_ascii=False
        )
    )

    print()

    print("=" * 60)

    print(
        "🌌 Traumverse session complete."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()