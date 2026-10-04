from pathlib import Path
import json


MODEL_PATH = Path(
    "knowledge/processed/learner_model.json"
)

EVIDENCE_TYPE_WEIGHTS = {
    "decision": 1,
    "application_decision": 2
}

MIN_EVIDENCE_FOR_MASTERY = 3


def create_empty_model():
    return {
        "learner_id": "local_user",
        "concepts": {}
    }


def load_model(path=MODEL_PATH):
    if not path.exists():
        return create_empty_model()

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def save_model(model, path=MODEL_PATH):
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        json.dumps(
            model,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def calculate_mastery(evidence):
    """Calculate weighted accuracy; mastery status separately requires 3 events."""
    total_weight = 0
    correct_weight = 0

    for event in evidence:
        weight = EVIDENCE_TYPE_WEIGHTS.get(
            event.get("evidence_type"),
            1
        )
        total_weight += weight

        if event.get("correct") is True:
            correct_weight += weight

    if not total_weight:
        return 0.0

    return correct_weight / total_weight


def get_concept_mastery(concept_state):
    evidence = concept_state.get("evidence")

    if evidence:
        return calculate_mastery(evidence)

    return concept_state.get("mastery", 0.0)


def determine_status(concept_state):
    if not concept_state:
        return "new"

    mastery = get_concept_mastery(
        concept_state
    )

    if mastery < 0.5:
        return "needs_reinforcement"

    if mastery < 0.8:
        return "developing"

    evidence = concept_state.get("evidence")
    evidence_count = (
        len(evidence)
        if evidence
        else concept_state.get("attempts", 0)
    )

    if evidence_count < MIN_EVIDENCE_FOR_MASTERY:
        return "developing"

    return "mastered"


def update_model(
    model,
    learning_event
):
    concept_id = learning_event[
        "concept_id"
    ]

    if concept_id not in model["concepts"]:
        model["concepts"][concept_id] = {
            "attempts": 0,
            "correct": 0,
            "incorrect": 0,
            "mastery": 0.0,
            "evidence": []
        }

    concept = model["concepts"][
        concept_id
    ]

    concept["attempts"] += 1

    if learning_event["correct"]:
        concept["correct"] += 1
    else:
        concept["incorrect"] += 1

    evidence = concept.setdefault(
        "evidence",
        []
    )
    evidence.append(
        learning_event
    )
    concept["mastery"] = calculate_mastery(
        evidence
    )

    return model


def main():

    model = load_model()

    print(
        json.dumps(
            model,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()