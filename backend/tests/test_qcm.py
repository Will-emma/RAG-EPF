import json

import pytest

from app.agent import graph
from app.api.routes.agent import QcmResponse


def sample_question(correct_answer=0, options=None):
    return {
        "question": "Quelle option est correcte ?",
        "options": options or ["Option A", "Option B", "Option C", "Option D"],
        "correctAnswer": correct_answer,
    }


def test_qcm_prompt_describes_index_without_a_fixed_answer_example():
    assert '"correctAnswer": 0' not in graph.QCM_SYSTEM_PROMPT
    assert "index entier (0 à 3)" in graph.QCM_SYSTEM_PROMPT
    assert "exactement 4 propositions distinctes" in graph.QCM_SYSTEM_PROMPT


def test_shuffle_preserves_correct_option_and_recalculates_index(monkeypatch):
    def controlled_shuffle(options):
        options[:] = [options[2], options[0], options[3], options[1]]

    monkeypatch.setattr(graph.random, "shuffle", controlled_shuffle)

    result = graph.shuffle_question_options(sample_question(correct_answer=0))

    assert result["options"] == ["Option C", "Option A", "Option D", "Option B"]
    assert result["options"][result["correctAnswer"]] == "Option A"
    assert result["correctAnswer"] == 1
    assert set(result) == {"question", "options", "correctAnswer"}


def test_shuffle_can_place_correct_option_at_different_positions(monkeypatch):
    permutations = iter(
        [
            ["Option B", "Option A", "Option C", "Option D"],
            ["Option D", "Option C", "Option B", "Option A"],
        ]
    )

    def controlled_shuffle(options):
        shuffled = next(permutations)
        options[:] = shuffled

    monkeypatch.setattr(graph.random, "shuffle", controlled_shuffle)

    results = [graph.shuffle_question_options(sample_question()) for _ in range(2)]

    assert [result["correctAnswer"] for result in results] == [1, 3]
    assert all(
        result["options"][result["correctAnswer"]] == "Option A"
        for result in results
    )


@pytest.mark.parametrize(
    "question",
    [
        sample_question(correct_answer=4),
        sample_question(correct_answer=-1),
        sample_question(correct_answer=True),
        sample_question(options=["Option A", "Option B", "Option C"]),
        sample_question(options=["Option A", "Option B", "Option C", "Option C"]),
    ],
)
def test_qcm_question_validation_rejects_invalid_answer_or_options(question):
    with pytest.raises(ValueError):
        graph.shuffle_question_options(question)


@pytest.mark.asyncio
async def test_generate_questions_node_returns_frontend_contract(monkeypatch):
    raw_questions = [sample_question(correct_answer=0)]

    async def fake_call_llm(system_prompt, user_prompt, temperature):
        assert '"correctAnswer": 0' not in system_prompt
        assert "exactement 4 propositions distinctes" in system_prompt
        assert "Génère exactement 1 questions" in user_prompt
        return json.dumps(raw_questions)

    monkeypatch.setattr(graph, "call_llm", fake_call_llm)
    monkeypatch.setattr(
        graph.random,
        "shuffle",
        lambda options: options.__setitem__(slice(None), [options[1], options[0], options[2], options[3]]),
    )

    state = await graph.generate_questions_node(
        {"chunks": [{"content": "Extrait de cours."}], "num_questions": 1}
    )

    assert state["error"] is None
    assert state["questions"][0]["options"][state["questions"][0]["correctAnswer"]] == "Option A"
    assert set(state["questions"][0]) == {"question", "options", "correctAnswer"}

    api_response = QcmResponse(questions=state["questions"]).model_dump()
    assert set(api_response) == {"questions"}
    assert set(api_response["questions"][0]) == {"question", "options", "correctAnswer"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_question",
    [
        sample_question(correct_answer=4),
        sample_question(options=["Option A", "Option B", "Option C"]),
    ],
)
async def test_generate_questions_node_rejects_invalid_model_output(
    monkeypatch, invalid_question
):
    async def fake_call_llm(*_args, **_kwargs):
        return json.dumps([invalid_question])

    monkeypatch.setattr(graph, "call_llm", fake_call_llm)

    state = await graph.generate_questions_node(
        {"chunks": [{"content": "Extrait de cours."}], "num_questions": 1}
    )

    assert state["questions"] == []
    assert "Erreur de génération du QCM" in state["error"]
