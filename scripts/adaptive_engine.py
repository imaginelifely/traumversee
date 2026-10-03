from pathlib import Path
import json
import sys


MODEL_PATH = Path(
    "knowledge/processed/learner_model.json"
)


def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "Learner model not found. "
            "Run an experience first."
        )

    return json.loads(
        MODEL_PATH.read_text(
            encoding="utf-8"
        )
    )


def get_recommendation(
    concept_id,
    model
):

    concepts = model.get(
        "concepts",
        {}
    )

    if concept_id not in concepts:

        return {
            "concept_id": concept_id,
            "status": "new",
            "mastery": 0.0,
            "recommendation": "introduce"
        }

    concept = concepts[
        concept_id
    ]

    mastery = concept[
        "mastery"
    ]

    if mastery < 0.5:

        status = "needs_reinforcement"

        recommendation = (
            "reinforce"
        )

    elif mastery < 0.8:

        status = "developing"

        recommendation = (
            "practice"
        )

    else:

        status = "mastered"

        recommendation = (
            "progress"
        )

    return {
        "concept_id": concept_id,
        "status": status,
        "mastery": mastery,
        "attempts": concept[
            "attempts"
        ],
        "correct": concept[
            "correct"
        ],
        "incorrect": concept[
            "incorrect"
        ],
        "recommendation": recommendation
    }


def main():

    if len(sys.argv) < 2:

        print(
            "Usage: "
            "python scripts\\adaptive_engine.py "
            "<concept_id>"
        )

        print()

        print(
            "Example:"
        )

        print(
            "python scripts\\adaptive_engine.py "
            "cn_packet_switching"
        )

        return

    concept_id = sys.argv[1]

    model = load_model()

    recommendation = get_recommendation(
        concept_id,
        model
    )

    print()

    print(
        "=" * 60
    )

    print(
        "🧠 Traumverse Adaptive Engine"
    )

    print(
        "=" * 60
    )

    print()

    print(
        json.dumps(
            recommendation,
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