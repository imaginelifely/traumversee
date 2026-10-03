from pathlib import Path
import json
import sys


GRAPH_PATH = Path(
    "knowledge/concepts/cn/concept_graph.json"
)


def load_graph():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"Graph not found: {GRAPH_PATH}"
        )

    return json.loads(
        GRAPH_PATH.read_text(
            encoding="utf-8"
        )
    )


def find_concept(graph, concept_id):
    for concept in graph["concepts"]:
        if concept["id"] == concept_id:
            return concept

    return None


def find_concept_by_name(graph, name):
    name = name.strip().lower()

    for concept in graph["concepts"]:
        if concept["name"].lower() == name:
            return concept

    return None


def get_related_concepts(graph, concept_id):
    related = []

    for relationship in graph["relationships"]:

        if relationship["from"] == concept_id:
            related_concept = find_concept(
                graph,
                relationship["to"]
            )

            related.append({
                "name": (
                    related_concept["name"]
                    if related_concept
                    else relationship["to"]
                ),
                "relationship": relationship["type"],
                "direction": "outgoing",
                "basis": relationship["basis"],
                "source_section": relationship[
                    "source_section"
                ]
            })

        elif relationship["to"] == concept_id:
            related_concept = find_concept(
                graph,
                relationship["from"]
            )

            related.append({
                "name": (
                    related_concept["name"]
                    if related_concept
                    else relationship["from"]
                ),
                "relationship": relationship["type"],
                "direction": "incoming",
                "basis": relationship["basis"],
                "source_section": relationship[
                    "source_section"
                ]
            })

    return related


def build_query_result(graph, concept):
    related = get_related_concepts(
        graph,
        concept["id"]
    )

    return {
        "concept": concept["name"],
        "concept_id": concept["id"],
        "related_concepts": related
    }


def main():
    graph = load_graph()

    if len(sys.argv) < 2:
        print(
            "Usage: python scripts\\query_concept_graph.py <concept_name>"
        )
        print()
        print("Example:")
        print(
            'python scripts\\query_concept_graph.py "Packet Switching"'
        )
        return

    concept_name = " ".join(sys.argv[1:])

    concept = find_concept_by_name(
        graph,
        concept_name
    )

    if not concept:
        print(
            f"Concept not found: {concept_name}"
        )
        return

    result = build_query_result(
        graph,
        concept
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()