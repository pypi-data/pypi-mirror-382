import json
import re
import string
from dataclasses import dataclass
from itertools import product
from typing import Callable, List, Optional, Sequence, Union

import jiwer
from sacrebleu.metrics import BLEU, CHRF


@dataclass(frozen=True)
class _MetricConfig:
    """
    Internal configuration for how we optimize a metric.

    Attributes:
        compute: Callable that maps (reference, hypothesis) to a float score.
        optimize: "min" for error rates, "max" for similarity metrics.
        formatter: Optional callable for verbose output formatting.
    """

    compute: Callable[[str, str], float]
    optimize: str


def _compute_wer(reference: str, hypothesis: str) -> float:
    """
    Compute word error rate while staying compatible with multiple jiwer versions.
    """
    if hasattr(jiwer, "compute_measures"):
        return jiwer.compute_measures(reference, hypothesis)["wer"]
    if hasattr(jiwer, "process_words"):
        return jiwer.process_words(reference, hypothesis).wer
    return jiwer.wer(reference, hypothesis)


def _compute_cer(reference: str, hypothesis: str) -> float:
    """
    Compute character error rate with graceful degradation across jiwer releases.
    """
    if hasattr(jiwer, "cer"):
        return jiwer.cer(reference, hypothesis)
    if hasattr(jiwer, "compute_measures"):
        measures = jiwer.compute_measures(reference, hypothesis)
        return measures.get("cer", measures["wer"])
    raise AttributeError("Installed jiwer version does not expose cer().")


def _make_bleu(metric: Optional[BLEU]) -> Callable[[str, str], float]:
    metric = metric or BLEU(effective_order=True)

    def _compute(reference: str, hypothesis: str) -> float:
        return metric.sentence_score(hypothesis, [reference]).score

    return _compute


def _make_chrf(metric: Optional[CHRF]) -> Callable[[str, str], float]:
    metric = metric or CHRF()

    def _compute(reference: str, hypothesis: str) -> float:
        return metric.sentence_score(hypothesis, [reference]).score

    return _compute


def _extract_options(part: str) -> List[str]:
    """
    Return the possible alternatives represented within a single bracket.
    Supports both the modern pipe-separated format and the legacy JSON array format.
    """
    if "|" in part:
        return [option.strip() for option in part.split("|")]

    try:
        parsed = json.loads(f"[{part}]")
        return [str(option) for option in parsed]
    except json.JSONDecodeError:
        return [part.strip()]


def _expand_reference(reference: str) -> List[str]:
    """
    Expand a reference string into all acceptable alternatives.
    """
    parts = re.findall(r"\[(.*?)\]", reference)
    if not parts:
        return [reference]

    eval_combinations: List[List[str]] = []
    for part in parts:
        options = _extract_options(part)
        eval_combinations.append(options)

    base_sentence = re.sub(r"\[.*?\]", "{}", reference)
    combinations = [
        base_sentence.format(*combo) for combo in product(*eval_combinations)
    ]
    return combinations


def _normalize_text(text: str, lowercase: bool, remove_punctuation: bool) -> str:
    """
    Apply optional normalization to a single string.
    """
    if lowercase:
        text = text.lower()
    if remove_punctuation:
        punctuation = str.maketrans("", "", string.punctuation)
        text = text.translate(punctuation)
    return text


def _coerce_to_list(values: Union[Sequence[str], str]) -> List[str]:
    """
    Convert user-provided references or hypotheses to a list of strings.
    Accepts both sequences of strings and single string inputs for convenience.
    """
    if isinstance(values, str):
        return [values]
    return list(values)


def _evaluate_metric(
    references: Sequence[str],
    hypotheses: Sequence[str],
    config: _MetricConfig,
    *,
    verbose: bool,
    empty_text: str,
    lowercase: bool,
    remove_punctuation: bool,
) -> float:
    """
    Generic evaluator that expands references and optimizes per-utterance scores.
    """
    if len(references) != len(hypotheses):
        raise ValueError("Length of references and hypotheses must be the same.")

    total_score = 0.0
    count = 0

    for idx, (reference, hypothesis) in enumerate(zip(references, hypotheses), start=1):
        hypothesis = hypothesis.strip() or empty_text
        reference = reference.strip()

        try:
            reference_combinations = _expand_reference(reference)
        except Exception as exc:
            raise ValueError(f"Error processing reference: {reference}") from exc

        normalized_hypothesis = _normalize_text(
            hypothesis, lowercase=lowercase, remove_punctuation=remove_punctuation
        )
        normalized_references = [
            _normalize_text(
                ref_option,
                lowercase=lowercase,
                remove_punctuation=remove_punctuation,
            )
            for ref_option in reference_combinations
        ]

        best_score: Optional[float]
        best_match: Optional[str]

        if config.optimize == "min":
            best_score = float("inf")
            comparator = lambda candidate, current: candidate < current  # type: ignore
        else:
            best_score = float("-inf")
            comparator = lambda candidate, current: candidate > current  # type: ignore

        best_match = None

        if verbose:
            print(f"\nEntry {idx}:")
            print(f"Hypothesis: '{normalized_hypothesis}'")
            print("Reference combinations and their scores:")

        for ref_option, normalized_ref in zip(
            reference_combinations, normalized_references
        ):
            score = config.compute(normalized_ref, normalized_hypothesis)

            if verbose:
                print(f"  - '{normalized_ref}': score = {score:.4f}")

            if best_match is None or comparator(score, best_score):  # type: ignore[arg-type]
                best_score = score
                best_match = normalized_ref

        if best_score in (float("inf"), float("-inf")) or best_match is None:
            raise RuntimeError("Failed to determine an optimal score for entry "
                               f"{idx}.")

        if verbose:
            print(f"Best match: '{best_match}' with score = {best_score:.4f}")

        total_score += best_score
        count += 1

    return total_score / count if count else 0.0


def wer(
    references: Union[Sequence[str], str],
    hypotheses: Union[Sequence[str], str],
    *,
    verbose: bool = False,
    empty_text: str = "<|nospeech|>",
    lowercase: bool = False,
    remove_punctuation: bool = False,
) -> float:
    """
    Compute alternative-aware word error rate (WER).
    """
    ref_list = _coerce_to_list(references)
    hyp_list = _coerce_to_list(hypotheses)
    config = _MetricConfig(compute=_compute_wer, optimize="min")
    return _evaluate_metric(
        ref_list,
        hyp_list,
        config,
        verbose=verbose,
        empty_text=empty_text,
        lowercase=lowercase,
        remove_punctuation=remove_punctuation,
    )


def cer(
    references: Union[Sequence[str], str],
    hypotheses: Union[Sequence[str], str],
    *,
    verbose: bool = False,
    empty_text: str = "<|nospeech|>",
    lowercase: bool = False,
    remove_punctuation: bool = False,
) -> float:
    """
    Compute alternative-aware character error rate (CER).
    """
    ref_list = _coerce_to_list(references)
    hyp_list = _coerce_to_list(hypotheses)
    config = _MetricConfig(compute=_compute_cer, optimize="min")
    return _evaluate_metric(
        ref_list,
        hyp_list,
        config,
        verbose=verbose,
        empty_text=empty_text,
        lowercase=lowercase,
        remove_punctuation=remove_punctuation,
    )


def bleu(
    references: Union[Sequence[str], str],
    hypotheses: Union[Sequence[str], str],
    *,
    verbose: bool = False,
    empty_text: str = "<|nospeech|>",
    lowercase: bool = False,
    remove_punctuation: bool = False,
    metric: Optional[BLEU] = None,
) -> float:
    """
    Compute BLEU scores while selecting the best-matching reference alternative.
    """
    ref_list = _coerce_to_list(references)
    hyp_list = _coerce_to_list(hypotheses)
    config = _MetricConfig(compute=_make_bleu(metric), optimize="max")
    return _evaluate_metric(
        ref_list,
        hyp_list,
        config,
        verbose=verbose,
        empty_text=empty_text,
        lowercase=lowercase,
        remove_punctuation=remove_punctuation,
    )


def chrf(
    references: Union[Sequence[str], str],
    hypotheses: Union[Sequence[str], str],
    *,
    verbose: bool = False,
    empty_text: str = "<|nospeech|>",
    lowercase: bool = False,
    remove_punctuation: bool = False,
    metric: Optional[CHRF] = None,
) -> float:
    """
    Compute chrF scores while selecting the best-matching reference alternative.
    """
    ref_list = _coerce_to_list(references)
    hyp_list = _coerce_to_list(hypotheses)
    config = _MetricConfig(compute=_make_chrf(metric), optimize="max")
    return _evaluate_metric(
        ref_list,
        hyp_list,
        config,
        verbose=verbose,
        empty_text=empty_text,
        lowercase=lowercase,
        remove_punctuation=remove_punctuation,
    )


__all__ = ["wer", "cer", "bleu", "chrf"]
