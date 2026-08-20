from app.rag.prompt import build_context, build_prompt, get_sources
from app.rag.retriever import build_search_query, is_relevant


def test_prompt_contains_grounded_context_and_question():
	results = [
		{
			"text": "Instagram: https://www.instagram.com/inquisitorssociety/",
			"source": "social_media.md",
			"distance": 0.2,
		}
	]

	prompt = build_prompt("What is the Instagram link?", results)

	assert "social_media.md" in prompt
	assert "https://www.instagram.com/inquisitorssociety/" in prompt
	assert "What is the Instagram link?" in prompt


def test_sources_are_unique_and_context_skips_empty_chunks():
	results = [
		{"text": "First", "source": "contact.md"},
		{"text": "", "source": "empty.md"},
		{"text": "Second", "source": "contact.md"},
	]

	assert get_sources(results) == ["contact.md"]
	assert "empty.md" not in build_context(results)


def test_relevance_uses_lower_distance_threshold():
	assert is_relevant([{"distance": 0.9}]) is True
	assert is_relevant([{"distance": 1.5}]) is False
	assert is_relevant([]) is False


def test_search_query_includes_recent_context_for_follow_up():
	query = build_search_query(
		"How do I apply?",
		[
			{"role": "user", "content": "What internships are available?"},
			{"role": "assistant", "content": "AI and web internships are available."},
		],
	)

	assert "How do I apply?" in query
	assert "internships are available" in query
