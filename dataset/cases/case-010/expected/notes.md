# case-010: acceptance notes

PDF layout: 3; number format: 1.234,56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(100 x 0.35, 2) = 35.00; round(35.00 x 0.20, 2) = 7.00.
- L02: round(20 x 18.75, 2) = 375.00; round(375.00 x 0.20, 2) = 75.00.

Calculated totals: 410.00 + 82.00 = 492.00 EUR.
Declared totals: 410.00 + 82.00; total 492.00 EUR.

## Intentional condition

Missing order reference and SKUs, one non-exact line description. Agent proposes the correct order and non-deterministic line on step 2; human confirms that existing proposal on step 3.

## Step results

### Step 1: new / needs_information

- SUPPLIER_IDENTITY/DOC-010: unknown, severity=None, depends_on=ORDER_MATCH.
- BUYER_IDENTITY/DOC-010: unknown, severity=None, depends_on=ORDER_MATCH.
- ORDER_MATCH/DOC-010: unknown, severity=None, depends_on=None.
- CURRENCY_MATCH/DOC-010: unknown, severity=None, depends_on=ORDER_MATCH.
- LINE_MATCH/L01: unknown, severity=None, depends_on=ORDER_MATCH.
- LINE_MATCH/L02: unknown, severity=None, depends_on=ORDER_MATCH.
- QTY_RECEIVED/L01: unknown, severity=None, depends_on=ORDER_MATCH.
- QTY_RECEIVED/L02: unknown, severity=None, depends_on=ORDER_MATCH.
- QTY_ORDER_REMAINING/L01: unknown, severity=None, depends_on=ORDER_MATCH.
- QTY_ORDER_REMAINING/L02: unknown, severity=None, depends_on=ORDER_MATCH.
- UNIT_PRICE/L01: unknown, severity=None, depends_on=ORDER_MATCH.
- UNIT_PRICE/L02: unknown, severity=None, depends_on=ORDER_MATCH.

### Step 2: new / needs_review

- ORDER_MATCH/DOC-010: fail, severity=needs_review, depends_on=None.
- LINE_MATCH/L01: fail, severity=needs_review, depends_on=None.
- L01 -> OL-010-01 (agent_proposal): ordered 100, received 100, previously invoiced 0; available = 100 - 0 = 100; remaining = 100 - 0 = 100.
- L02 -> OL-010-02 (deterministic): ordered 20, received 20, previously invoiced 0; available = 20 - 0 = 20; remaining = 20 - 0 = 20.

### Step 3: new / clear

- All applicable checks pass, or no checks for a duplicate.
- L01 -> OL-010-01 (human_confirmation): ordered 100, received 100, previously invoiced 0; available = 100 - 0 = 100; remaining = 100 - 0 = 100.
- L02 -> OL-010-02 (deterministic): ordered 20, received 20, previously invoiced 0; available = 20 - 0 = 20; remaining = 20 - 0 = 20.

Both orders have the same descriptions and prices; the first PDF description is not an exact description/alias/SKU match. Therefore there are zero fully deterministic order candidates, not a fabricated automatic choice. The second document line matches deterministically within either order. The proposal supplies the missing order/first-line link. Only that proposal is confirmed by the human on step 3.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
