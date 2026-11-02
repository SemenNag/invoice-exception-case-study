# case-002: acceptance notes

PDF layout: 2; number format: 1.234,56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(60 x 12.50, 2) = 750.00; round(750.00 x 0.20, 2) = 150.00.

Calculated totals: 750.00 + 150.00 = 900.00 EUR.
Declared totals: 750.00 + 150.00; total 900.00 EUR.

## Intentional condition

None: order 100, accepted receipts 30 + 30 on distinct dates, current invoice 60. Partial invoice is permitted.

## Step results

### Step 1: new / clear

- All applicable checks pass, or no checks for a duplicate.
- L01 -> OL-002-01 (deterministic): ordered 100, received 60, previously invoiced 0; available = 60 - 0 = 60; remaining = 100 - 0 = 100.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
