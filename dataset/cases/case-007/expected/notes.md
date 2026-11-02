# case-007: acceptance notes

PDF layout: 1; number format: 1,234.56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(40 x 24.75, 2) = 990.00; round(990.00 x 0.20, 2) = 198.00.
- L02: round(8 x 29.95, 2) = 239.60; round(239.60 x 0.20, 2) = 47.92.

Calculated totals: 1229.60 + 245.92 = 1475.52 EUR.
Declared totals: 1229.60 + 245.92; total 1475.52 EUR.

## Intentional condition

Document IBAN is absent from the resolved supplier approved accounts. All other facts match.

## Step results

### Step 1: new / blocked

- BANK_ACCOUNT/DOC-007: fail, severity=blocked, depends_on=None.
- L01 -> OL-007-01 (deterministic): ordered 40, received 40, previously invoiced 0; available = 40 - 0 = 40; remaining = 40 - 0 = 40.
- L02 -> OL-007-02 (deterministic): ordered 8, received 8, previously invoiced 0; available = 8 - 0 = 8; remaining = 8 - 0 = 8.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
