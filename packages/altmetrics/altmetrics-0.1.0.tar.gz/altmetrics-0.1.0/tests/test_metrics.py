import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from altmetrics import bleu, cer, chrf, wer


def _common_references_pipe():
    return [
        "[jenta|jenten] [jogga|jogget] på [broa|broen|brua|bruen]",
        "[katten|katta] ligger på [matta|matten]",
        "Det var en fin dag.",
    ]


def _common_references_json():
    return [
        '["jenta","jenten"] ["jogga","jogget"] på ["broa","broen","brua","bruen"]',
        '["katten","katta"] ligger på ["matta","matten"]',
        "Det var en fin dag.",
    ]


def _common_hypotheses():
    return [
        "jenta jogga på broa",
        "katten ligger på matta",
        "Det var en fin dag.",
    ]


def test_wer_pipe_syntax_matches_best_reference():
    score = wer(_common_references_pipe(), _common_hypotheses())
    assert pytest.approx(score, 0.001) == 0.0


def test_wer_json_syntax_matches_best_reference():
    score = wer(_common_references_json(), _common_hypotheses())
    assert pytest.approx(score, 0.001) == 0.0


def test_cer_matches_best_reference():
    score = cer(_common_references_pipe(), _common_hypotheses())
    assert pytest.approx(score, 0.001) == 0.0


def test_cer_json_syntax_matches_best_reference():
    score = cer(_common_references_json(), _common_hypotheses())
    assert pytest.approx(score, 0.001) == 0.0


def test_bleu_prefers_highest_scoring_reference():
    references = [
        "[The|A] cat sat on [the|a] mat.",
        "[Hello|Hi] there!",
    ]
    hypotheses = ["The cat sat on the mat.", "Hello there!"]
    score = bleu(references, hypotheses)
    assert pytest.approx(score, 0.001) == 100.0


def test_bleu_prefers_highest_scoring_reference_json():
    references = [
        '["The","A"] cat sat on ["the","a"] mat.',
        '["Hello","Hi"] there!',
    ]
    hypotheses = ["The cat sat on the mat.", "Hello there!"]
    score = bleu(references, hypotheses)
    assert pytest.approx(score, 0.001) == 100.0


def test_chrf_prefers_highest_scoring_reference():
    references = [
        "[Fast|Quick] brown [fox|foxes] [jump|jumps] over the lazy dog.",
        "[Greetings|Hello] world!",
    ]
    hypotheses = ["Quick brown fox jumps over the lazy dog.", "Hello world!"]
    score = chrf(references, hypotheses)
    assert pytest.approx(score, 0.001) == 100.0


def test_chrf_prefers_highest_scoring_reference_json():
    references = [
        '["Fast","Quick"] brown ["fox","foxes"] ["jump","jumps"] over the lazy dog.',
        '["Greetings","Hello"] world!',
    ]
    hypotheses = ["Quick brown fox jumps over the lazy dog.", "Hello world!"]
    score = chrf(references, hypotheses)
    assert pytest.approx(score, 0.001) == 100.0


def test_remove_punctuation_option():
    references = ["[cat|cat,] sat.", "dog!"]
    hypotheses = ["cat sat", "dog"]
    score = wer(references, hypotheses, remove_punctuation=True)
    assert pytest.approx(score, 0.001) == 0.0


def test_single_string_inputs_are_coerced():
    assert pytest.approx(wer("[hello|hi]", "hello"), 0.001) == 0.0
    assert pytest.approx(cer("[hello|hi]", "hello"), 0.001) == 0.0
    assert pytest.approx(bleu("[hello|hi]", "hello"), 0.001) == 100.0
    assert pytest.approx(chrf("[hello|hi]", "hello"), 0.001) == 100.0


def test_empty_hypothesis_uses_placeholder():
    references = ["[silence| ]"]
    hypotheses = [""]
    score = wer(references, hypotheses, empty_text="silence")
    assert pytest.approx(score, 0.001) == 0.0
