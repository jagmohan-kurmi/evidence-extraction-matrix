# Evidence Extraction Matrix

Define extraction fields in JSON, capture researcher-entered values with page, citation, and source-quote provenance, validate required completeness, then export CSV or JSON. No automatic extraction is performed.

## Install and use

```console
python -m pip install .
evidence-extraction-matrix fixtures/sample.json --format csv --output extraction.csv
```

Input JSON contains a `schema.fields` array (`name`, optional `required`) and a `records` array. Each supplied non-empty field value is an object containing `value`, `page`, `citation`, and verbatim `quote`. JSON exports include validation findings; CSV includes evidence columns and a `validation_errors` column. Exit codes are `0` (complete), `1` (validation findings exported), and `2` (invalid/unreadable input or output). No network access is required.

## Limits

The tool organizes researcher-supplied records and does not replace scholarly judgment. Verify outputs against original sources.

## Tests

```console
python -m unittest discover -s tests -v
```
