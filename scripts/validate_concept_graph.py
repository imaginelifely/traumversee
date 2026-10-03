from pathlib import Path
import json


GRAPH_PATH = Path("knowledge/concepts/cn/concept_graph.json")

ALLOWED_BASES = {
    "source",
    "inferred"
}


def load_graph():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"Graph file not found: {GRAPH_PATH}"
        )

    return json.loads(
        GRAPH_PATH.read_text(encoding="utf-8")
    )


def validate_graph(graph):
    errors = []

    concepts = graph.get("concepts", [])
    relationships = graph.get("relationships", [])

    # Collect concept IDs
    concept_ids = [concept["id"] for concept in concepts]

    # Check duplicate concept IDs
    if len(concept_ids) != len(set(concept_ids)):
        errors.append("Duplicate concept ID found.")

    concept_id_set = set(concept_ids)

    # Validate relationships
    seen_relationships = set()

    for relationship in relationships:
        from_id = relationship.get("from")
        to_id = relationship.get("to")
        relationship_type = relationship.get("type")
        basis = relationship.get("basis")

        # Check referenced concepts exist
        if from_id not in concept_id_set:
            errors.append(
                f"Unknown source concept: {from_id}"
            )

        if to_id not in concept_id_set:
            errors.append(
                f"Unknown target concept: {to_id}"
            )

        # Check relationship type exists
        if not relationship_type:
            errors.append(
                f"Missing relationship type: "
                f"{from_id} -> {to_id}"
            )

        # Check relationship basis
        if basis not in ALLOWED_BASES:
            errors.append(
                f"Invalid relationship basis: "
                f"{basis} "
                f"for {from_id} -> {to_id}"
            )

        # Check source traceability
        if not relationship.get("source_section"):
            errors.append(
                f"Missing source section for relationship: "
                f"{from_id} -> {to_id}"
            )

        # Check duplicate relationships
        relationship_key = (
            from_id,
            to_id,
            relationship_type
        )

        if relationship_key in seen_relationships:
            errors.append(
                f"Duplicate relationship: "
                f"{from_id} -> {to_id} "
                f"({relationship_type})"
            )

        seen_relationships.add(relationship_key)

    return errors


def main():
    graph = load_graph()

    errors = validate_graph(graph)

    if errors:
        print("❌ Graph validation failed.")
        print()

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("✅ Graph validation passed.")
    print()
    print(f"Concepts: {len(graph['concepts'])}")
    print(f"Relationships: {len(graph['relationships'])}")
    print(f"Allowed relationship bases: {', '.join(sorted(ALLOWED_BASES))}")


if __name__ == "__main__":
    main()