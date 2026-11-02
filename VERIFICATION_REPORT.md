# Automated & Manual Verification Report

This document contains the evaluation results across all 6 test targets across 5 modules and 20 evaluation checkpoints.

## Executive Summary

| Platform | Domain | File | Total Passed (/20) | Score (%) | Exec Valid | Console Errors | Lines of Code (LOC) | Characters |
|---|---|---|---|---|---|---|---|---|
| AiPASS | ecom | `aipass/ecom.html` | **20/20** | **100.0%** | PASS | 0 | 319 | 15451 |
| AiPASS | book | `aipass/book.html` | **20/20** | **100.0%** | PASS | 0 | 288 | 13080 |
| AiPASS | food | `aipass/food.html` | **20/20** | **100.0%** | PASS | 0 | 319 | 12355 |
| Native_Gemini | ecom | `google/ecom.html` | **20/20** | **100.0%** | PASS | 0 | 266 | 12784 |
| Native_Gemini | book | `google/book.html` | **20/20** | **100.0%** | PASS | 0 | 362 | 16676 |
| Native_Gemini | food | `google/food.html` | **20/20** | **100.0%** | PASS | 0 | 300 | 13306 |


## Module-by-Module Performance

| Module Name | Total Points | AiPASS (ecom) | AiPASS (book) | AiPASS (food) | Native (ecom) | Native (book) | Native (food) |
|---|---|---|---|---|---|---|---|
| Module 1: Catalog Render | 4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Module 2: Filter & Search | 4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Module 3: Cart State | 4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Module 4: Financial Formulas | 4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Module 5: Persistence & Validation | 4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |


## 3. The 20-Point Manual Verification Checklist

Include this table in your report's Methodology / Appendix and use it to cross-check your manual walkthrough against the automated Playwright script. Every checkpoint is scored as 1 (Pass, worth 5%) or 0 (Fail, worth 0%).

| Code | Module | Verification Checkpoint Description | Weight | AiPASS (ecom / book / food) | Native (ecom / book / food) |
|---|---|---|---|---|---|
| M1.1 | 1. Catalog | #catalog-grid exists in the DOM and renders without layout collapse. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M1.2 | 1. Catalog | Exactly 6 .catalog-item cards render on initial page load. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M1.3 | 1. Catalog | Every .catalog-item card contains a clickable .add-btn element. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M1.4 | 1. Catalog | All 6 domain-specific item names and base prices match the prompt specification. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M2.1 | 2. Filter/Search | #search-input and #category-select exist in the DOM. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M2.2 | 2. Filter/Search | Typing a specific item keyword into #search-input dynamically reduces visible .catalog-item cards to 1. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M2.3 | 2. Filter/Search | Selecting a specific category in #category-select filters visible cards to exactly 2 items. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M2.4 | 2. Filter/Search | Resetting search to empty and category to "all" restores all 6 .catalog-item cards. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M3.1 | 3. Cart State | Clicking .add-btn on Item 1 and Item 6 adds both items into #cart-list. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M3.2 | 3. Cart State | Clicking .qty-inc on an item in #cart-list increments its quantity from 1 to 2. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M3.3 | 3. Cart State | Clicking .qty-dec on that item decrements its quantity back from 2 to 1. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M3.4 | 3. Cart State | Clicking .remove-btn removes the targeted item from #cart-list. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M4.1 | 4. Financials | #subtotal-val accurately displays the exact sum of (price * qty) across test states. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M4.2 | 4. Financials | #discount-val equals 0.00 below threshold and equals exact domain discount above threshold. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M4.3 | 4. Financials | #tax-val accurately computes 7% VAT (ecom), 50 THB shipping (book), or 10% Service Charge (food). | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M4.4 | 4. Financials | #grand-total-val equals exact net payable amount (S - D + T) in both low and high cart states. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M5.1 | 5. Persistence | Cart mutations write valid JSON data to localStorage.getItem("app_cart_state"). | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M5.2 | 5. Persistence | Reloading the page (page.reload()) preserves and re-renders the cart items and totals. | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M5.3 | 5. Persistence | Clicking #checkout-btn with an empty #customer-input blocks order creation (app_last_order remains null). | 5% | [x] / [x] / [x] | [x] / [x] / [x] |
| M5.4 | 5. Persistence | Filling #customer-input and clicking #checkout-btn saves order JSON to localStorage.getItem("app_last_order"). | 5% | [x] / [x] / [x] | [x] / [x] / [x] |