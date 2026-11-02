import os
import re
import csv
from pathlib import Path
from playwright.sync_api import sync_playwright

# Domain-specific test configurations matching the 3 Thai prompts
DOMAIN_CONFIG = {
    "ecom": {
        "search_keyword": "Mouse",
        "category_value": "Audio",
        "expected_prices": ["400", "600", "1200", "1500", "2200", "3000"],
        # Low state: 1x Item 0 (400 THB) -> S=400, D=0, T=28.00, G=428.00
        "low_state": {"subtotal": 400.0, "discount": 0.0, "tax": 28.0, "grand": 428.0},
        # High state: 1x Item 0 (400) + 1x Item 5 (3000) -> S=3400 (>=2000), D=510.00, T=202.30, G=3092.30
        "high_state": {"subtotal": 3400.0, "discount": 510.0, "tax": 202.3, "grand": 3092.3},
    },
    "book": {
        "search_keyword": "Python",
        "category_value": "Fiction",
        "expected_prices": ["180", "220", "280", "320", "450", "550"],
        # Low state: 1x Item 0 (180 THB, qty=1 < 3) -> S=180, D=0, T=50.00, G=230.00
        "low_state": {"subtotal": 180.0, "discount": 0.0, "tax": 50.0, "grand": 230.0},
        # High state: 2x Item 0 (360) + 1x Item 5 (550) (qty=3 >= 3) -> S=910, D=80.00, T=50.00, G=880.00
        "high_state": {"subtotal": 910.0, "discount": 80.0, "tax": 50.0, "grand": 880.0},
    },
    "food": {
        "search_keyword": "Matcha",
        "category_value": "Drink",
        "expected_prices": ["60", "70", "90", "110", "120", "180"],
        # Low state: 1x Item 0 (60 THB < 300) -> S=60, D=0, T=6.00, G=66.00
        "low_state": {"subtotal": 60.0, "discount": 0.0, "tax": 6.0, "grand": 66.0},
        # High state: 2x Item 0 (120) + 1x Item 5 (180) -> S=300 (>=300), D=40.00, T=26.00, G=286.00
        "high_state": {"subtotal": 300.0, "discount": 40.0, "tax": 26.0, "grand": 286.0},
    },
}

FILES_TO_TEST = [
    ("AiPASS", "ecom", "aipass/ecom.html"),
    ("AiPASS", "book", "aipass/book.html"),
    ("AiPASS", "food", "aipass/food.html"),
    ("Native_Gemini", "ecom", "google/ecom.html"),
    ("Native_Gemini", "book", "google/book.html"),
    ("Native_Gemini", "food", "google/food.html"),
]

CHECKPOINTS_SPEC = [
    ("M1.1", "1. Catalog", "#catalog-grid exists in the DOM and renders without layout collapse.", "5%"),
    ("M1.2", "1. Catalog", "Exactly 6 .catalog-item cards render on initial page load.", "5%"),
    ("M1.3", "1. Catalog", "Every .catalog-item card contains a clickable .add-btn element.", "5%"),
    ("M1.4", "1. Catalog", "All 6 domain-specific item names and base prices match the prompt specification.", "5%"),
    ("M2.1", "2. Filter/Search", "#search-input and #category-select exist in the DOM.", "5%"),
    ("M2.2", "2. Filter/Search", "Typing a specific item keyword into #search-input dynamically reduces visible .catalog-item cards to 1.", "5%"),
    ("M2.3", "2. Filter/Search", "Selecting a specific category in #category-select filters visible cards to exactly 2 items.", "5%"),
    ("M2.4", "2. Filter/Search", "Resetting search to empty and category to \"all\" restores all 6 .catalog-item cards.", "5%"),
    ("M3.1", "3. Cart State", "Clicking .add-btn on Item 1 and Item 6 adds both items into #cart-list.", "5%"),
    ("M3.2", "3. Cart State", "Clicking .qty-inc on an item in #cart-list increments its quantity from 1 to 2.", "5%"),
    ("M3.3", "3. Cart State", "Clicking .qty-dec on that item decrements its quantity back from 2 to 1.", "5%"),
    ("M3.4", "3. Cart State", "Clicking .remove-btn removes the targeted item from #cart-list.", "5%"),
    ("M4.1", "4. Financials", "#subtotal-val accurately displays the exact sum of (price * qty) across test states.", "5%"),
    ("M4.2", "4. Financials", "#discount-val equals 0.00 below threshold and equals exact domain discount above threshold.", "5%"),
    ("M4.3", "4. Financials", "#tax-val accurately computes 7% VAT (ecom), 50 THB shipping (book), or 10% Service Charge (food).", "5%"),
    ("M4.4", "4. Financials", "#grand-total-val equals exact net payable amount (S - D + T) in both low and high cart states.", "5%"),
    ("M5.1", "5. Persistence", "Cart mutations write valid JSON data to localStorage.getItem(\"app_cart_state\").", "5%"),
    ("M5.2", "5. Persistence", "Reloading the page (page.reload()) preserves and re-renders the cart items and totals.", "5%"),
    ("M5.3", "5. Persistence", "Clicking #checkout-btn with an empty #customer-input blocks order creation (app_last_order remains null).", "5%"),
    ("M5.4", "5. Persistence", "Filling #customer-input and clicking #checkout-btn saves order JSON to localStorage.getItem(\"app_last_order\").", "5%"),
]


def parse_num(text):
    # Extract float value from text string safely
    if not text:
        return -999999.0
    cleaned = re.sub(r"[^0-9.-]", "", text.replace(",", ""))
    try:
        return float(cleaned)
    except ValueError:
        return -999999.0


def approx_eq(val1, val2, tol=0.1):
    # Check float equality within tolerance
    return abs(val1 - val2) <= tol


def count_visible_items(page):
    # Count how many .catalog-item elements are currently visible in the DOM
    items = page.locator("#catalog-grid .catalog-item")
    count = items.count()
    visible = 0
    for i in range(count):
        if items.nth(i).is_visible():
            visible += 1
    return visible


def grade_html_file(playwright, platform, domain, filepath):
    # Initialize all 20 binary checkpoints to 0
    scores = {f"M{m}.{c}": 0 for m in range(1, 6) for c in range(1, 5)}
    cfg = DOMAIN_CONFIG[domain]
    runtime_errors = []

    resolved_path = (Path(__file__).parent / filepath).resolve()
    if not resolved_path.exists():
        print(f"[SKIP] File not found: {resolved_path}")
        return None

    # Read file lines and character size for code volume metrics
    with open(resolved_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        loc = len(content.splitlines())
        char_len = len(content)

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Capture uncaught runtime errors and console.error messages
    page.on("pageerror", lambda err: runtime_errors.append(str(err)))
    page.on(
        "console",
        lambda msg: runtime_errors.append(msg.text) if msg.type == "error" else None,
    )

    # Automatically accept any alert/confirm dialogs triggered on checkout
    page.on("dialog", lambda dialog: dialog.accept())

    file_url = resolved_path.as_uri()
    try:
        page.goto(file_url, wait_until="networkidle", timeout=8000)
    except Exception as e:
        runtime_errors.append(f"Load timeout: {e}")

    # Clear localStorage first and reload to ensure a clean initial state
    try:
        page.evaluate("localStorage.clear()")
        page.reload(wait_until="domcontentloaded")
    except Exception:
        pass

    # ---------------- MODULE 1: CATALOG RENDER ----------------
    try:
        if page.locator("#catalog-grid").count() > 0:
            scores["M1.1"] = 1
        vis_count = count_visible_items(page)
        if vis_count == 6:
            scores["M1.2"] = 1
        add_btns = page.locator("#catalog-grid .catalog-item .add-btn").count()
        if add_btns == 6:
            scores["M1.3"] = 1
        grid_text = page.locator("#catalog-grid").inner_text()
        if all(p in grid_text for p in cfg["expected_prices"]):
            scores["M1.4"] = 1
    except Exception:
        pass

    # ---------------- MODULE 2: FILTER & SEARCH ----------------
    try:
        has_search = page.locator("#search-input").count() > 0
        has_cat = page.locator("#category-select").count() > 0
        if has_search and has_cat:
            scores["M2.1"] = 1

            # Test keyword search
            page.locator("#search-input").fill(cfg["search_keyword"])
            page.wait_for_timeout(150)
            if count_visible_items(page) == 1:
                scores["M2.2"] = 1

            # Clear search and test category dropdown
            page.locator("#search-input").fill("")
            page.wait_for_timeout(100)
            page.locator("#category-select").select_option(cfg["category_value"])
            page.wait_for_timeout(150)
            if count_visible_items(page) == 2:
                scores["M2.3"] = 1

            # Reset filter back to "all"
            page.locator("#category-select").select_option("all")
            page.wait_for_timeout(150)
            if count_visible_items(page) == 6:
                scores["M2.4"] = 1
    except Exception:
        pass

    # ---------------- MODULE 3 & 4: CART STATE & FINANCIALS ----------------
    try:
        add_buttons = page.locator("#catalog-grid .catalog-item .add-btn")
        if add_buttons.count() >= 6:
            # Click first item (Item 0) -> enters LOW state (1 item in cart)
            add_buttons.nth(0).click()
            page.wait_for_timeout(150)

            sub_low = parse_num(page.locator("#subtotal-val").inner_text())
            disc_low = parse_num(page.locator("#discount-val").inner_text())
            tax_low = parse_num(page.locator("#tax-val").inner_text())
            grand_low = parse_num(page.locator("#grand-total-val").inner_text())

            low_sub_ok = approx_eq(sub_low, cfg["low_state"]["subtotal"])
            low_disc_ok = approx_eq(disc_low, cfg["low_state"]["discount"])
            low_tax_ok = approx_eq(tax_low, cfg["low_state"]["tax"])
            low_grand_ok = approx_eq(grand_low, cfg["low_state"]["grand"])

            # Add 6th item (Item 5) -> 2 distinct items in cart
            add_buttons.nth(5).click()
            page.wait_for_timeout(150)
            if (
                page.locator("#cart-list .qty-inc").count() >= 2
                and page.locator("#cart-list .remove-btn").count() >= 2
            ):
                scores["M3.1"] = 1

            # Increment Item 0 quantity from 1 to 2
            page.locator("#cart-list .qty-inc").first.click()
            page.wait_for_timeout(150)
            sub_after_inc = parse_num(page.locator("#subtotal-val").inner_text())
            if sub_after_inc > sub_low:
                scores["M3.2"] = 1

            # Check HIGH state financials:
            # For book & food, High State expects 2x Item 0 + 1x Item 5 (current state)
            # For ecom, High State expects 1x Item 0 + 1x Item 5 (we will check after decrement)
            if domain in ["book", "food"]:
                sub_high = parse_num(page.locator("#subtotal-val").inner_text())
                disc_high = parse_num(page.locator("#discount-val").inner_text())
                tax_high = parse_num(page.locator("#tax-val").inner_text())
                grand_high = parse_num(page.locator("#grand-total-val").inner_text())

            # Decrement Item 0 quantity back from 2 to 1
            page.locator("#cart-list .qty-dec").first.click()
            page.wait_for_timeout(150)
            sub_after_dec = parse_num(page.locator("#subtotal-val").inner_text())
            if sub_after_dec < sub_after_inc:
                scores["M3.3"] = 1

            if domain == "ecom":
                sub_high = parse_num(page.locator("#subtotal-val").inner_text())
                disc_high = parse_num(page.locator("#discount-val").inner_text())
                tax_high = parse_num(page.locator("#tax-val").inner_text())
                grand_high = parse_num(page.locator("#grand-total-val").inner_text())

            # Grade Module 4 checks (must pass both low and high states)
            if low_sub_ok and approx_eq(sub_high, cfg["high_state"]["subtotal"]):
                scores["M4.1"] = 1
            if low_disc_ok and approx_eq(disc_high, cfg["high_state"]["discount"]):
                scores["M4.2"] = 1
            if low_tax_ok and approx_eq(tax_high, cfg["high_state"]["tax"]):
                scores["M4.3"] = 1
            if low_grand_ok and approx_eq(grand_high, cfg["high_state"]["grand"]):
                scores["M4.4"] = 1

            # Test Remove button on second item
            rem_count_before = page.locator("#cart-list .remove-btn").count()
            page.locator("#cart-list .remove-btn").last.click()
            page.wait_for_timeout(150)
            rem_count_after = page.locator("#cart-list .remove-btn").count()
            if rem_count_after == rem_count_before - 1:
                scores["M3.4"] = 1
    except Exception:
        pass

    # ---------------- MODULE 5: PERSISTENCE & VALIDATION ----------------
    try:
        # Check M5.1: localStorage key "app_cart_state" is written
        saved_cart = page.evaluate("localStorage.getItem('app_cart_state')")
        if saved_cart and len(saved_cart) > 2:
            scores["M5.1"] = 1

        # Check M5.2: Reload page and verify cart still has item and subtotal > 0
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(200)
        sub_reloaded = parse_num(page.locator("#subtotal-val").inner_text())
        if sub_reloaded > 0:
            scores["M5.2"] = 1

        # Check M5.3: Checkout validation blocks empty #customer-input
        page.locator("#customer-input").fill("")
        page.locator("#checkout-btn").click()
        page.wait_for_timeout(150)
        order_empty = page.evaluate("localStorage.getItem('app_last_order')")
        if not order_empty:
            scores["M5.3"] = 1

        # Check M5.4: Valid customer input writes "app_last_order"
        page.locator("#customer-input").fill("Taiyo KMUTT Test")
        page.locator("#checkout-btn").click()
        page.wait_for_timeout(150)
        order_saved = page.evaluate("localStorage.getItem('app_last_order')")
        if order_saved and len(order_saved) > 2:
            scores["M5.4"] = 1
    except Exception:
        pass

    browser.close()

    total_passed = sum(scores.values())
    percentage = (total_passed / 20.0) * 100.0
    exec_valid = 1 if len(runtime_errors) == 0 else 0

    return {
        "Platform": platform,
        "Domain": domain,
        "File": filepath,
        "Total_Passed_20": total_passed,
        "Score_Pct": round(percentage, 2),
        "Exec_Valid": exec_valid,
        "Console_Errors": len(runtime_errors),
        "Runtime_Error_Msgs": runtime_errors,
        "LOC": loc,
        "Chars": char_len,
        **scores,
    }


def generate_markdown_report(results, output_md_path="VERIFICATION_REPORT.md"):
    # Lookup dict: (platform, domain) -> result dict
    lookup = {(r["Platform"], r["Domain"]): r for r in results}

    md = []
    md.append("# Automated & Manual Verification Report\n")
    md.append("This document contains the evaluation results across all 6 test targets across 5 modules and 20 evaluation checkpoints.\n")

    md.append("## Executive Summary\n")
    md.append("| Platform | Domain | File | Total Passed (/20) | Score (%) | Exec Valid | Console Errors | Lines of Code (LOC) | Characters |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        status_icon = "PASS" if r["Exec_Valid"] == 1 else "FAIL"
        md.append(f"| {r['Platform']} | {r['Domain']} | `{r['File']}` | **{r['Total_Passed_20']}/20** | **{r['Score_Pct']}%** | {status_icon} | {r['Console_Errors']} | {r['LOC']} | {r['Chars']} |")
    md.append("\n")

    # Module aggregated score breakdown
    md.append("## Module-by-Module Performance\n")
    md.append("| Module Name | Total Points | AiPASS (ecom) | AiPASS (book) | AiPASS (food) | Native (ecom) | Native (book) | Native (food) |")
    md.append("|---|---|---|---|---|---|---|---|")
    modules = [
        ("Module 1: Catalog Render", ["M1.1", "M1.2", "M1.3", "M1.4"]),
        ("Module 2: Filter & Search", ["M2.1", "M2.2", "M2.3", "M2.4"]),
        ("Module 3: Cart State", ["M3.1", "M3.2", "M3.3", "M3.4"]),
        ("Module 4: Financial Formulas", ["M4.1", "M4.2", "M4.3", "M4.4"]),
        ("Module 5: Persistence & Validation", ["M5.1", "M5.2", "M5.3", "M5.4"]),
    ]

    for mod_title, cp_list in modules:
        row = [mod_title, str(len(cp_list))]
        for platform in ["AiPASS", "Native_Gemini"]:
            for domain in ["ecom", "book", "food"]:
                res = lookup.get((platform, domain))
                if res:
                    m_score = sum(res.get(cp, 0) for cp in cp_list)
                    row.append(f"{m_score}/{len(cp_list)}")
                else:
                    row.append("N/A")
        md.append("| " + " | ".join(row) + " |")
    md.append("\n")

    # 20-Point Verification Checklist Table matching prompt
    md.append("## 3. The 20-Point Manual Verification Checklist\n")
    md.append("Include this table in your report's Methodology / Appendix and use it to cross-check your manual walkthrough against the automated Playwright script. Every checkpoint is scored as 1 (Pass, worth 5%) or 0 (Fail, worth 0%).\n")
    md.append("| Code | Module | Verification Checkpoint Description | Weight | AiPASS (ecom / book / food) | Native (ecom / book / food) |")
    md.append("|---|---|---|---|---|---|")

    for cp_code, cp_module, cp_desc, cp_weight in CHECKPOINTS_SPEC:
        # AiPASS checks
        aipass_marks = []
        for domain in ["ecom", "book", "food"]:
            res = lookup.get(("AiPASS", domain))
            if res and res.get(cp_code, 0) == 1:
                aipass_marks.append("[x]")
            else:
                aipass_marks.append("[ ]")
        aipass_cell = " / ".join(aipass_marks)

        # Native checks
        native_marks = []
        for domain in ["ecom", "book", "food"]:
            res = lookup.get(("Native_Gemini", domain))
            if res and res.get(cp_code, 0) == 1:
                native_marks.append("[x]")
            else:
                native_marks.append("[ ]")
        native_cell = " / ".join(native_marks)

        md.append(f"| {cp_code} | {cp_module} | {cp_desc} | {cp_weight} | {aipass_cell} | {native_cell} |")

    # Console errors or warnings section if any
    has_errors = any(len(r.get("Runtime_Error_Msgs", [])) > 0 for r in results)
    if has_errors:
        md.append("\n## Runtime Console / Page Errors Recorded\n")
        for r in results:
            if r.get("Runtime_Error_Msgs"):
                md.append(f"### `{r['File']}` ({r['Platform']} - {r['Domain']})")
                for err in r["Runtime_Error_Msgs"]:
                    md.append(f"- `{err}`")
                md.append("")

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Saved populated verification report to {output_md_path}")


def main():
    results = []
    with sync_playwright() as p:
        for platform, domain, filepath in FILES_TO_TEST:
            res = grade_html_file(p, platform, domain, filepath)
            if res:
                results.append(res)
                print(
                    f"[{res['Platform']} - {res['Domain']}] Score: {res['Total_Passed_20']}/20 ({res['Score_Pct']}%) | Valid: {res['Exec_Valid']} | LOC: {res['LOC']}"
                )

    if results:
        csv_file = "evaluation_results.csv"
        # Omit list of error messages from raw csv or stringify
        csv_results = []
        for r in results:
            item = dict(r)
            item.pop("Runtime_Error_Msgs", None)
            csv_results.append(item)

        keys = list(csv_results[0].keys())
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(csv_results)
        print(f"\nSaved full rubric matrix to {csv_file}")

        # Generate markdown report
        generate_markdown_report(results, "VERIFICATION_REPORT.md")


if __name__ == "__main__":
    main()

