from pathlib import Path
import json


MODEL_PATH = Path(
    "knowledge/processed/learner_model.json"
)


def create_empty_model():
    return {
        "learner_id": "local_user",
        "concepts": {}
    }


def load_model():
    if not MODEL_PATH.exists():
        return create_empty_model()

    return json.loads(
        MODEL_PATH.read_text(
            encoding="utf-8"
        )
    )


def save_model(model):
    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    MODEL_PATH.write_text(
        json.dumps(
            model,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


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

    concept["mastery"] = (
        concept["correct"]
        / concept["attempts"]
    )

    concept["evidence"].append(
        learning_event
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