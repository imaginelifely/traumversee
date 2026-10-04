from pathlib import Path
import json

from learner_model import get_concept_mastery


MODEL_PATH = Path(
    "knowledge/processed/learner_model.json"
)


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

    return get_concept_mastery(
        concept
    )


def run_selected_experience(
    experience_id
):
    from experience_presenter import (
        find_experience_by_id,
        present_experience
    )

    experience = find_experience_by_id(
        experience_id
    )

    if not experience:
        print(
            f"No experience found for ID: "
            f"{experience_id}"
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


def get_next_decision(
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
        "Welcome to your adaptive learning experience."
    )

    print()

    # -------------------------------------------------
    # Start with the learner's current concept
    # -------------------------------------------------

    current_concept_id = (
        "cn_packet_switching"
    )

    model = load_model()

    mastery_before = get_mastery(
        model,
        current_concept_id
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

    # -------------------------------------------------
    # Ask the adaptive engine what to do
    # -------------------------------------------------

    decision = get_next_decision(
        current_concept_id
    )

    print()
    print(
        "🎯 Adaptive Decision"
    )
    print()

    print(
        json.dumps(
            decision,
            indent=2,
            ensure_ascii=False
        )
    )

    # -------------------------------------------------
    # If the learner should progress to another
    # concept, switch to that concept
    # -------------------------------------------------

    if decision.get(
        "next_action"
    ) == "progress":

        next_concept = decision.get(
            "next_concept"
        )

        if not next_concept:

            print()
            print(
                "No next concept available."
            )

            return

        current_concept_id = (
            next_concept["concept_id"]
        )

        print()
        print(
            "➡️ Progressing to:"
        )

        print(
            next_concept["concept"]
        )

        # Ask selector for an experience
        # belonging to the new concept.
        decision = get_next_decision(
            current_concept_id
        )

    # -------------------------------------------------
    # If no experience exists
    # -------------------------------------------------

    if not decision.get(
        "experience_id"
    ):

        print()
        print(
            "⚠️ No experience is currently "
            "available for this concept."
        )

        print()
        print(
            json.dumps(
                decision,
                indent=2,
                ensure_ascii=False
            )
        )

        return

    # -------------------------------------------------
    # Start the selected experience
    # -------------------------------------------------

    print()

    print(
        "📚 Selected Experience:"
    )

    print(
        decision["title"]
    )

    input(
        "Press ENTER to begin..."
    )

    experience = run_selected_experience(
        decision["experience_id"]
    )

    if experience is None:
        return

    # -------------------------------------------------
    # Reload learner model after experience
    # -------------------------------------------------

    model_after = load_model()

    mastery_after = get_mastery(
        model_after,
        current_concept_id
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

    # -------------------------------------------------
    # Decide what should happen next
    # -------------------------------------------------

    next_decision = get_next_decision(
        current_concept_id
    )

    print()
    print(
        "🎯 Next Learning Decision"
    )

    print()

    print(
        json.dumps(
            next_decision,
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