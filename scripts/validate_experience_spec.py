from pathlib import Path
import json


GRAPH_PATH = Path(
    "knowledge/concepts/cn/concept_graph.json"
)

SECTIONS_PATH = Path(
    "knowledge/processed/cn_sections.json"
)

EXPERIENCE_DIR = Path(
    "knowledge/concepts/cn/experience_specs"
)


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def validate_experience(
    graph,
    sections,
    experience
):
    errors = []

    concept_ids = {
        concept["id"]
        for concept in graph.get("concepts", [])
    }

    section_numbers = {
        section["number"]
        for section in sections
    }

    # -----------------------------------------
    # Check main concept
    # -----------------------------------------

    experience_concept = experience.get(
        "concept_id"
    )

    if experience_concept not in concept_ids:
        errors.append(
            f"Unknown experience concept: "
            f"{experience_concept}"
        )

    # -----------------------------------------
    # Check prerequisites
    # -----------------------------------------

    for prerequisite in experience.get(
        "prerequisites",
        []
    ):
        if prerequisite not in concept_ids:
            errors.append(
                f"Unknown prerequisite concept: "
                f"{prerequisite}"
            )

    # -----------------------------------------
    # Check assessment target
    # -----------------------------------------

    assessment = experience.get(
        "assessment",
        {}
    )

    expected_concept = assessment.get(
        "expected_concept"
    )

    if expected_concept not in concept_ids:
        errors.append(
            f"Unknown assessment concept: "
            f"{expected_concept}"
        )

    # -----------------------------------------
    # Check learning objective
    # -----------------------------------------

    learning_objective = experience.get(
        "learning_objective",
        {}
    )

    if not learning_objective.get(
        "statement"
    ):
        errors.append(
            "Missing learning objective statement."
        )

    # -----------------------------------------
    # Check experience content
    # -----------------------------------------

    experience_content = experience.get(
        "experience",
        {}
    )

    required_experience_fields = [
        "type",
        "title",
        "scenario",
        "challenge",
        "learner_action"
    ]

    for field in required_experience_fields:

        if not experience_content.get(field):
            errors.append(
                f"Missing experience field: "
                f"{field}"
            )

    # -----------------------------------------
    # Check feedback
    # -----------------------------------------

    feedback = experience.get(
        "feedback",
        {}
    )

    if not feedback.get("correct"):
        errors.append(
            "Missing correct feedback."
        )

    if not feedback.get("explanation"):
        errors.append(
            "Missing feedback explanation."
        )

    # -----------------------------------------
    # Check mastery evidence
    # -----------------------------------------

    mastery = experience.get(
        "mastery_evidence",
        {}
    )

    if mastery.get("concept") != experience_concept:
        errors.append(
            "Mastery evidence concept does not "
            "match experience concept."
        )

    # -----------------------------------------
    # Check traceability
    # -----------------------------------------

    traceability = experience.get(
        "traceability",
        {}
    )

    if not traceability.get("source"):
        errors.append(
            "Missing source traceability."
        )

    if not traceability.get(
        "generated_fields"
    ):
        errors.append(
            "Missing generated_fields "
            "in traceability."
        )

    # -----------------------------------------
    # Check source section exists
    # -----------------------------------------

    source = traceability.get(
        "source",
        {}
    )

    source_section = source.get(
        "section"
    )

    if source_section not in section_numbers:
        errors.append(
            f"Unknown source section: "
            f"{source_section}"
        )

    return errors


def main():

    # -----------------------------------------
    # Load knowledge graph
    # -----------------------------------------

    graph = load_json(
        GRAPH_PATH
    )

    # -----------------------------------------
    # Load parsed source sections
    # -----------------------------------------

    sections = load_json(
        SECTIONS_PATH
    )

    # -----------------------------------------
    # Find all experience specs
    # -----------------------------------------

    experience_files = sorted(
        EXPERIENCE_DIR.glob("*.json")
    )

    if not experience_files:
        print(
            "❌ No experience specs found."
        )

        raise SystemExit(1)

    total = 0
    passed = 0
    failed = 0

    print(
        f"Validating "
        f"{len(experience_files)} "
        f"experience spec(s)..."
    )

    print()

    # -----------------------------------------
    # Validate every experience
    # -----------------------------------------

    for experience_path in experience_files:

        total += 1

        print(
            f"Validating: "
            f"{experience_path.name}"
        )

        try:

            experience = load_json(
                experience_path
            )

            errors = validate_experience(
                graph,
                sections,
                experience
            )

            if errors:

                failed += 1

                print(
                    "  ❌ Failed"
                )

                for error in errors:

                    print(
                        f"     - {error}"
                    )

            else:

                passed += 1

                print(
                    "  ✅ Passed"
                )

        except Exception as error:

            failed += 1

            print(
                "  ❌ Failed"
            )

            print(
                f"     - {error}"
            )

        print()

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    print(
        "=" * 40
    )

    print(
        "Experience Validation Summary"
    )

    print(
        "=" * 40
    )

    print(
        f"Total:  {total}"
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    # -----------------------------------------
    # Final result
    # -----------------------------------------

    if failed > 0:

        print()

        print(
            "❌ Some experience specs failed validation."
        )

        raise SystemExit(1)

    print()

    print(
        "✅ All experience specs passed."
    )


if __name__ == "__main__":
    main()