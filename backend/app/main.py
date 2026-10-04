import json
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scripts.learner_model import (
    determine_status,
    get_concept_mastery,
    load_model,
    save_model,
    update_model,
)

app = FastAPI(
    title="Traumverse API",
    description="Knowledge-to-experience learning platform",
    version="0.1.0",
)

ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "frontend"
EXPERIENCE_DIR = ROOT_DIR / "knowledge" / "concepts" / "cn" / "experience_specs"
GRAPH_PATH = ROOT_DIR / "knowledge" / "concepts" / "cn" / "concept_graph.json"
MODEL_PATH = ROOT_DIR / "knowledge" / "processed" / "learner_model.json"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


class AnswerSubmission(BaseModel):
    option_id: str


def read_json(path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def get_experiences():
    experiences = {}

    for path in sorted(EXPERIENCE_DIR.glob("*.json")):
        experience = read_json(path)
        experiences[experience["experience_id"]] = experience

    return experiences


def get_concept_name(concept_id, graph):
    for concept in graph.get("concepts", []):
        if concept["id"] == concept_id:
            return concept["name"]

    return concept_id.replace("_", " ").title()


def get_concept_summary(concept, model, experiences, graph):
    concept_id = concept["id"]
    state = model.get("concepts", {}).get(concept_id)
    concept_experiences = [
        experience
        for experience in experiences.values()
        if experience["concept_id"] == concept_id
    ]

    return {
        "id": concept_id,
        "name": concept["name"],
        "status": determine_status(state),
        "mastery": get_concept_mastery(state) if state else 0.0,
        "attempts": state.get("attempts", 0) if state else 0,
        "correct": state.get("correct", 0) if state else 0,
        "experience_count": len(concept_experiences),
        "experiences": [
            {
                "id": experience["experience_id"],
                "title": experience["experience"]["title"],
                "type": experience["experience"].get("type", "scenario"),
            }
            for experience in concept_experiences
        ],
    }


def build_dashboard():
    graph = read_json(GRAPH_PATH)
    experiences = get_experiences()
    model = load_model(MODEL_PATH)
    concepts = [
        get_concept_summary(concept, model, experiences, graph)
        for concept in graph.get("concepts", [])
    ]
    available_concepts = [
        concept
        for concept in concepts
        if concept["experience_count"]
    ]

    next_concept = next(
        (
            concept
            for concept in available_concepts
            if concept["status"] != "mastered"
        ),
        available_concepts[0] if available_concepts else None,
    )
    recent_evidence = []

    for concept_id, state in model.get("concepts", {}).items():
        for event in state.get("evidence", []):
            recent_evidence.append(
                {
                    **event,
                    "concept": get_concept_name(concept_id, graph),
                }
            )

    recent_evidence.sort(
        key=lambda event: event.get("timestamp", ""),
        reverse=True,
    )

    return {
        "learner_id": model.get("learner_id", "local_user"),
        "subject": "Computer Networks",
        "source": graph.get("source", {}),
        "concepts": concepts,
        "available_concepts": available_concepts,
        "relationships": graph.get("relationships", []),
        "next_concept": next_concept,
        "stats": {
            "concepts_in_graph": len(concepts),
            "concepts_explored": sum(
                concept["status"] != "new"
                for concept in concepts
            ),
            "concepts_in_progress": sum(
                concept["status"] in ("developing", "needs_reinforcement")
                for concept in concepts
            ),
            "experiences_available": len(experiences),
            "evidence_events": len(recent_evidence),
        },
        "recent_evidence": recent_evidence[-6:][::-1],
    }


def get_experience_or_404(experience_id):
    experience = get_experiences().get(experience_id)

    if not experience:
        raise HTTPException(
            status_code=404,
            detail="Experience not found.",
        )

    return experience


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health_check():
    return {
        "status": "alive",
        "project": "Traumverse",
        "version": "0.1.0",
    }


@app.get("/api/dashboard")
def dashboard():
    return build_dashboard()


@app.get("/api/experiences/{experience_id}")
def experience_details(experience_id: str):
    experience = get_experience_or_404(experience_id)
    assessment = experience["assessment"]

    return {
        "experience_id": experience["experience_id"],
        "concept_id": experience["concept_id"],
        "concept": experience["concept"],
        "learning_objective": experience["learning_objective"],
        "experience": experience["experience"],
        "assessment": {
            "type": assessment["type"],
            "question": assessment["question"],
            "options": assessment["options"],
        },
        "traceability": experience.get("traceability", {}),
        "mastery_evidence": experience.get("mastery_evidence", {}),
    }


@app.post("/api/experiences/{experience_id}/answer")
def submit_answer(experience_id: str, submission: AnswerSubmission):
    experience = get_experience_or_404(experience_id)
    options = experience["assessment"]["options"]
    selected_option = next(
        (
            option
            for option in options
            if option["id"] == submission.option_id
        ),
        None,
    )

    if not selected_option:
        raise HTTPException(
            status_code=422,
            detail="Choose one of the listed answers.",
        )

    correct = (
        selected_option["id"]
        == experience["assessment"]["correct_answer"]
    )
    learning_event = {
        "concept_id": experience["concept_id"],
        "experience_id": experience["experience_id"],
        "selected_answer": selected_option["id"],
        "correct": correct,
        "evidence_type": experience["mastery_evidence"]["evidence_type"],
        "mastery_signal": experience["mastery_evidence"]["mastery_signal"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    model = load_model(MODEL_PATH)
    update_model(model, learning_event)
    save_model(model, MODEL_PATH)
    state = model["concepts"][experience["concept_id"]]

    return {
        "correct": correct,
        "feedback": (
            experience["feedback"]["correct"]
            if correct
            else experience["feedback"]["explanation"]
        ),
        "explanation": experience["feedback"]["explanation"],
        "source": experience.get("traceability", {}).get("source", {}),
        "evidence_type": learning_event["evidence_type"],
        "mastery_signal": learning_event["mastery_signal"],
        "learner_state": {
            "mastery": get_concept_mastery(state),
            "status": determine_status(state),
            "attempts": state["attempts"],
            "correct": state["correct"],
            "incorrect": state["incorrect"],
        },
    }