# case-005: acceptance notes

PDF layout: 2; number format: 1,234.56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(20 x 38.40, 2) = 768.00; round(768.00 x 0.20, 2) = 153.60.
- L02: round(40 x 11.25, 2) = 450.00; round(450.00 x 0.20, 2) = 90.00.
- L03: round(10 x 16.80, 2) = 168.00; round(168.00 x 0.20, 2) = 33.60.

Calculated totals: 1386.00 + 277.20 = 1663.20 EUR.
Declared totals: 1386.00 + 277.20; total 1673.20 EUR.

## Intentional condition

Only declared_total is inflated by EUR 10.00; subtotal, line net and VAT remain correct.

## Step results

### Step 1: new / blocked

- TOTALS_ARITHMETIC/DOC-005: fail, severity=blocked, depends_on=None.
- L01 -> OL-005-01 (deterministic): ordered 20, received 20, previously invoiced 0; available = 20 - 0 = 20; remaining = 20 - 0 = 20.
- L02 -> OL-005-02 (deterministic): ordered 40, received 40, previously invoiced 0; available = 40 - 0 = 40; remaining = 40 - 0 = 40.
- L03 -> OL-005-03 (deterministic): ordered 10, received 10, previously invoiced 0; available = 10 - 0 = 10; remaining = 10 - 0 = 10.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
