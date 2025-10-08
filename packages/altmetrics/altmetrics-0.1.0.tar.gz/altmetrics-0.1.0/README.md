# altmetrics

`altmetrics` is a Python toolkit for evaluating speech and text generation systems when multiple orthographically valid references exist. It extends classic metrics such as **WER**, **CER**, **BLEU**, and **chrF** by expanding bracketed reference alternatives and picking the combination that yields the best score for each hypothesis.

## Why altmetrics?

Traditional metrics assume a single canonical reference. In practice, many languages and transcription guidelines permit several spellings (`matta` vs `matten`), optional fillers, or regional variants. `altmetrics` lets you encode these choices in square brackets and automatically evaluates with the most favourable reference for each sentence.

```
[jenta|jenten] [jogga|jogget] på [broa|broen|brua|bruen]
```

## Installation

```bash
pip install altmetrics
```

## Usage

```python
from altmetrics import wer, cer, bleu, chrf

references = [
    "[jenta|jenten] [jogga|jogget] på [broa|broen|brua|bruen]",
    "[katten|katta] ligger på [matta|matten]",
    "Det var en fin dag."
]
hypotheses = [
    "jenta jogga på broa",
    "katten ligger på matta",
    "Det var en fin dag."
]

print("WER :", wer(references, hypotheses, lowercase=True))
print("CER :", cer(references, hypotheses))
print("BLEU:", bleu(references, hypotheses))
print("chrF:", chrf(references, hypotheses))
```

## Features

- Accepts both modern `[optionA|optionB]` and legacy `["optionA","optionB"]` reference syntax.
- Works with multiple metrics via a shared expansion and optimisation pipeline.
- Compatible with recent versions of `jiwer` and `sacrebleu`.
- Optional preprocessing: lowercase, punctuation removal, and placeholder control for empty hypotheses.

## License

MIT
