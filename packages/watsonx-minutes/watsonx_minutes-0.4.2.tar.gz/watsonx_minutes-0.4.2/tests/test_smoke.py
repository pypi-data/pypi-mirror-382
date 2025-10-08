from watsonx_minutes.prompt import build_prompt

def test_prompt_contains_language_and_minutes():
    minutes = "Discussed roadmap and assigned tasks to Alice and Bob."
    p = build_prompt(minutes, language="English")
    assert "<minutes>" in p and "</minutes>" in p
    assert "OUTPUT LANGUAGE: English" in p
