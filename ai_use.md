# AI Use

Generative AI used: Yes

This record describes two project uses and the resulting materials in the
current game.

## Entry 1

- Member and date: Jain Shaurya Dileep; 5 November 2026.
- Tool and model/version: Codex.
- Purpose: Create ASCII art for the game.
- Substantial parts affected (files/materials): ASCII art in `art.py`.
- What was kept, changed, or rejected, and how results were checked (tests or
  corrections): The AI-created ASCII art in `art.py` is used in the game. The
  course-container terminal smoke check displayed the title artwork.

## Entry 2

- Member and date: SOU Cheng Hei; 22 October 2026.
- Tool and model/version: ChatGPT.
- Purpose: Generate Klotski piece configurations.
- Substantial parts affected (files/materials): The `pieceArrangements` data in
  `klotski.py`.
- What was kept, changed, or rejected, and how results were checked (tests or
  corrections): The AI-generated layouts in `klotski.py` are used in the game.
  Automated tests verify each board's geometry and search legal one-cell moves
  to confirm that all twelve layouts can reach the goal.
