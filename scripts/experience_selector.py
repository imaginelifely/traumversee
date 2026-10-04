from pathlib import Path
import json
import sys

from learner_model import determine_status


MODEL_PATH = Path(
    "knowledge/processed/learner_model.json"
)

EXPERIENCE_DIR = Path(
    "knowledge/concepts/cn/experience_specs"
)

GRAPH_PATH = Path(
    "knowledge/concepts/cn/concept_graph.json"
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


def find_experiences(
    concept_id
):

    experiences = []

    for path in sorted(
        EXPERIENCE_DIR.glob("*.json")
    ):

        experience = load_json(
            path
        )

        if experience.get(
            "concept_id"
        ) == concept_id:

            experiences.append(
                experience
            )

    return experiences


def find_concept(
    graph,
    concept_id
):

    for concept in graph.get(
        "concepts",
        []
    ):

        if concept["id"] == concept_id:
            return concept

    return None


def find_next_concept(
    concept_id,
    model,
    graph
):

    relationships = graph.get(
        "relationships",
        []
    )

    candidates = []

    for relationship in relationships:

        if relationship["from"] != concept_id:
            continue

        next_id = relationship["to"]

        concept = find_concept(
            graph,
            next_id
        )

        if not concept:
            continue

        state = get_concept_state(
            next_id,
            model
        )

        if not state:

            candidates.append(
                {
                    "concept_id": next_id,
                    "concept": concept["name"],
                    "reason": "not_started",
                    "relationship": relationship["type"]
                }
            )

    if not candidates:
        return None

    return candidates[0]


def select_experience(
    concept_id,
    model
):

    graph = load_json(
        GRAPH_PATH
    )

    concept_state = get_concept_state(
        concept_id,
        model
    )

    status = determine_status(
        concept_state
    )

    experiences = find_experiences(
        concept_id
    )

    # -----------------------------------------
    # No experience available
    # -----------------------------------------

    if not experiences:

        return {
            "concept_id": concept_id,
            "status": status,
            "next_action": "no_experience_available"
        }

    # -----------------------------------------
    # Concept mastered
    # -----------------------------------------

    if status == "mastered":

        next_concept = find_next_concept(
            concept_id,
            model,
            graph
        )

        if next_concept:

            return {
                "concept_id": concept_id,
                "status": status,
                "next_action": "progress",
                "next_concept": next_concept
            }

        return {
            "concept_id": concept_id,
            "concept": experiences[0][
                "concept"
            ],
            "status": status,
            "next_action": "concept_complete"
        }

    # -----------------------------------------
    # New learner
    # -----------------------------------------

    if status == "new":

        selected = experiences[0]

        next_action = "introduce"

    # -----------------------------------------
    # Needs reinforcement
    # -----------------------------------------

    elif status == "needs_reinforcement":

        selected = experiences[0]

        next_action = "reinforce"

    # -----------------------------------------
    # Developing
    # -----------------------------------------

    else:

        if len(experiences) >= 2:

            selected = experiences[1]

        else:

            selected = experiences[0]

        next_action = "practice"

    return {
        "concept_id": concept_id,
        "concept": selected[
            "concept"
        ],
        "experience_id": selected[
            "experience_id"
        ],
        "title": selected[
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
    print("=" * 60)
    print(
        "🎯 Traumverse Experience Selector"
    )
    print("=" * 60)
    print()

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )

    print()
    print("=" * 60)


if __name__ == "__main__":

    main()