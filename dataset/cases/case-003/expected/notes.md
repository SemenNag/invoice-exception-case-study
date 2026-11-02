# case-003: acceptance notes

PDF layout: 3; number format: 1,234.56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(70 x 12.50, 2) = 875.00; round(875.00 x 0.20, 2) = 175.00.

Calculated totals: 875.00 + 175.00 = 1050.00 EUR.
Declared totals: 875.00 + 175.00; total 1050.00 EUR.

## Intentional condition

Quantity overrun: order/received 100, earlier counted different-number invoice 40, current 70; available and remaining 60; excess 10. One business discrepancy yields QTY_RECEIVED and QTY_ORDER_REMAINING.

## Step results

### Step 1: new / blocked

- QTY_RECEIVED/L01: fail, severity=blocked, depends_on=None.
- QTY_ORDER_REMAINING/L01: fail, severity=blocked, depends_on=None.
- L01 -> OL-003-01 (deterministic): ordered 100, received 100, previously invoiced 40; available = 100 - 40 = 60; remaining = 100 - 40 = 60.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
