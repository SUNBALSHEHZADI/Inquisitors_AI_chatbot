import pytest

from app.api import routes


def test_chat_request_validates_message_length():
	request = routes.ChatRequest(message="What is Inquisitors?", session_id="test-session")

	assert request.message == "What is Inquisitors?"
	assert request.session_id == "test-session"

	with pytest.raises(ValueError):
		routes.ChatRequest(message="x" * 4001, session_id="test-session")


def test_chat_returns_grounded_response_with_sources(monkeypatch):
	fake_results = [
		{"text": "Official Instagram link", "source": "social_media.md", "distance": 0.2}
	]

	monkeypatch.setattr(routes, "index", object())
	monkeypatch.setattr(routes, "chunks", [{"text": "chunk"}])
	monkeypatch.setattr(routes, "model", object())
	monkeypatch.setattr(routes, "client", object())
	monkeypatch.setattr(routes, "retrieve", lambda *args, **kwargs: fake_results)
	monkeypatch.setattr(routes, "is_relevant", lambda results: True)
	monkeypatch.setattr(routes, "build_prompt", lambda question, results: "grounded prompt")
	monkeypatch.setattr(
		routes,
		"generate_response",
		lambda **kwargs: "**Official Instagram:** https://www.instagram.com/inquisitorssociety/",
	)

	response = routes.chat(
		routes.ChatRequest(
			message="What is the official Instagram link?",
			session_id="test-session",
		)
	)

	assert response.session_id == "test-session"
	assert response.sources == ["social_media.md"]
	assert "instagram.com/inquisitorssociety" in response.answer


def test_chat_returns_fallback_when_retrieval_is_irrelevant(monkeypatch):
	monkeypatch.setattr(routes, "index", object())
	monkeypatch.setattr(routes, "chunks", [{"text": "chunk"}])
	monkeypatch.setattr(routes, "model", object())
	monkeypatch.setattr(routes, "client", object())
	monkeypatch.setattr(routes, "retrieve", lambda *args, **kwargs: [{"distance": 2.0}])
	monkeypatch.setattr(routes, "is_relevant", lambda results: False)

	response = routes.chat(
		routes.ChatRequest(message="What is the weather?", session_id="fallback-session")
	)

	assert response.sources == []
	assert "couldn't find reliable information" in response.answer
