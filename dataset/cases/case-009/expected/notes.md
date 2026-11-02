# case-009: acceptance notes

PDF layout: 3; number format: 1,234.56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(5 x 186.40, 2) = 932.00; round(932.00 x 0.20, 2) = 186.40.
- L02: round(10 x 24.50, 2) = 245.00; round(245.00 x 0.20, 2) = 49.00.

Calculated totals: 1177.00 + 235.40 = 1412.40 EUR.
Declared totals: 1177.00 + 235.40; total 1412.40 EUR.

## Intentional condition

Same business key, different normalized price/amount facts. Price delta remains inside the inclusive 0.01 tolerance; only DOCUMENT_CONFLICT fails. Both PDFs are internally arithmetic-correct.

## Step results

### Step 1: conflict / blocked

- DOCUMENT_CONFLICT/DOC-009: fail, severity=blocked, depends_on=None.
- L01 -> OL-009-01 (deterministic): ordered 5, received 5, previously invoiced 0; available = 5 - 0 = 5; remaining = 5 - 0 = 5.
- L02 -> OL-009-02 (deterministic): ordered 10, received 10, previously invoiced 0; available = 10 - 0 = 10; remaining = 10 - 0 = 10.

The price delta is exactly EUR 0.01, inclusive tolerance. Same-key history is excluded from quantities. Only DOCUMENT_CONFLICT fails.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
