from textwrap import dedent

TEMPLATE = dedent(
    """

    You are an expert project coordinator.

    TASK: Read the Minutes of Meeting (MoM) between <minutes> and </minutes> and produce a concise summary and actionable TODOs.

    OUTPUT LANGUAGE: {language}

    STRICT OUTPUT FORMAT (Markdown):

    Summarization:
    - 1–3 sentences summarizing what the meeting was about.

    TODOs:

    | what to do | who is in charge | deadline | others |
    |---|---|---|---|
    # Add 1–15 rows. One task per row. If the MoM lacks a field, use "TBD".

    RULES:
    - Use the OUTPUT LANGUAGE for all text, including headings and column names.
    - Deadlines must be ISO dates (YYYY-MM-DD) where possible; otherwise "TBD".
    - Be specific and concise; do not invent details not supported by the minutes.
    - If only roles are given (e.g., PM, Eng), you may keep the role when no name is given.
    - No extra commentary outside this format.

    <minutes>
    {minutes}
    </minutes>
    """

)

def build_prompt(minutes: str, language: str) -> str:
    return TEMPLATE.format(minutes=minutes.strip(), language=language.strip())
