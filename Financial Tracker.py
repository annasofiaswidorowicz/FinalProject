#Our idea for this final project was to create a useful project that can be used by everyone.
#Because of this, we decided to do a financial tracker, which allows you to input daily spending and
#see where you're at and the spending you've done this month.

"""
Personal Finance Tracker (CSV-based)

Features implemented (from the idea #3 bullets):
1) Add transaction: amount, category, date, note
2) Store transactions in a list of dictionaries
3) Summaries:
   - total spending
   - totals per category
   - biggest expense
4) try/except for amount parsing and input validation
5) Monthly budget warnings (if category exceeds limit)
6) Export summary report to a text file
7) Simple charts (optional, uses matplotlib if installed)

CSV format used:
date,amount,category,note
2026-03-03,12.50,Food,Arepa lunch
"""

import csv
import os
from datetime import datetime


# -----------------------------
# Helpers: validation & parsing
# -----------------------------

def parse_amount(amount_str):
    """
    Convert user input to a float amount.
    Raises ValueError if invalid.
    """
    try:
        amount = float(amount_str)
    except ValueError:
        raise ValueError("Amount must be a number (example: 12.50).")

    # You can decide whether to allow negative amounts (refunds).
    # Here we allow negative for refunds, but not zero.
    if amount == 0:
        raise ValueError("Amount cannot be 0.")
    return amount


def parse_date(date_str):
    """
    Parse a date in YYYY-MM-DD format.
    Returns a datetime.date.
    Raises ValueError if invalid.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format (example: 2026-03-03).")


def clean_category(cat):
    """
    Basic category cleaning (trim + title case).
    """
    cat = cat.strip()
    if not cat:
        raise ValueError("Category cannot be empty.")
    return cat.title()


def safe_input(prompt):
    """
    Input wrapper to avoid accidental None / weird whitespace.
    """
    return input(prompt).strip()


# -----------------------------
# Core data loading/saving
# -----------------------------

def load_transactions(csv_filename):
    """
    Load transactions from a CSV file.
    Returns a list of dictionaries.
    If the file doesn't exist, returns an empty list.
    """
    transactions = []
    if not os.path.exists(csv_filename):
        return transactions

    try:
        with open(csv_filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Defensive parsing (in case file was edited manually)
                try:
                    d = parse_date(row["date"])
                    amt = float(row["amount"])
                    cat = row["category"].strip()
                    note = row.get("note", "").strip()
                except Exception:
                    # Skip corrupted rows rather than crashing
                    continue

                transactions.append({
                    "date": d,
                    "amount": amt,
                    "category": cat,
                    "note": note
                })
    except Exception as e:
        print(f"⚠️ Could not read file: {e}")

    return transactions


def save_transactions(csv_filename, transactions):
    """
    Save transactions (list of dicts) to CSV.
    Overwrites file.
    """
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["date", "amount", "category", "note"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in transactions:
                writer.writerow({
                    "date": t["date"].isoformat(),
                    "amount": f"{t['amount']:.2f}",
                    "category": t["category"],
                    "note": t["note"]
                })
    except Exception as e:
        print(f"⚠️ Could not save file: {e}")


# -----------------------------
# Feature 1: Add transaction
# -----------------------------

def add_transaction(transactions):
    """
    Ask user for transaction info and append to transactions list.
    Implements input validation + try/except parsing.
    """
    print("\nAdd a transaction")
    while True:
        date_str = safe_input("Date (YYYY-MM-DD): ")
        try:
            d = parse_date(date_str)
            break
        except ValueError as e:
            print(f"❌ {e}")

    while True:
        amount_str = safe_input("Amount (example 12.50, negative allowed for refunds): ")
        try:
            amt = parse_amount(amount_str)
            break
        except ValueError as e:
            print(f"❌ {e}")

    while True:
        cat_str = safe_input("Category (Food, Transport, Rent, etc.): ")
        try:
            cat = clean_category(cat_str)
            break
        except ValueError as e:
            print(f"❌ {e}")

    note = safe_input("Note (optional): ")

    transactions.append({
        "date": d,
        "amount": amt,
        "category": cat,
        "note": note
    })

    print("✅ Added.")


# -----------------------------
# Feature 3: Summaries
# -----------------------------

def total_spending(transactions, month=None):
    """
    Total spending (only counts positive amounts as spending).
    If month is provided (YYYY-MM), filters to that month.
    """
    total = 0.0
    for t in filter_by_month(transactions, month):
        if t["amount"] > 0:
            total += t["amount"]
    return total


def totals_by_category(transactions, month=None):
    """
    Returns a dict category -> total spending (positive amounts only).
    Optional month filter (YYYY-MM).
    """
    totals = {}
    for t in filter_by_month(transactions, month):
        if t["amount"] > 0:
            cat = t["category"]
            totals[cat] = totals.get(cat, 0.0) + t["amount"]
    return totals


def biggest_expense(transactions, month=None):
    """
    Returns the biggest single expense transaction (positive amount).
    If none found, returns None.
    """
    biggest = None
    for t in filter_by_month(transactions, month):
        if t["amount"] > 0:
            if biggest is None or t["amount"] > biggest["amount"]:
                biggest = t
    return biggest


def filter_by_month(transactions, month):
    """
    month format: 'YYYY-MM' or None.
    Yields transactions in that month.
    """
    if month is None:
        for t in transactions:
            yield t
        return

    try:
        dt = datetime.strptime(month, "%Y-%m")
        y, m = dt.year, dt.month
    except ValueError:
        # If invalid month, treat as no filter (or you can raise)
        for t in transactions:
            yield t
        return

    for t in transactions:
        if t["date"].year == y and t["date"].month == m:
            yield t


def print_summary(transactions, month=None):
    """
    Nicely prints summary metrics.
    """
    if month:
        print(f"\n📊 Summary for {month}")
    else:
        print("\n📊 Summary (all time)")

    total = total_spending(transactions, month)
    print(f"Total spending: €{total:.2f}")

    by_cat = totals_by_category(transactions, month)
    if not by_cat:
        print("No spending transactions found.")
    else:
        print("\nSpending by category:")
        for cat in sorted(by_cat.keys()):
            print(f"  - {cat}: €{by_cat[cat]:.2f}")

    big = biggest_expense(transactions, month)
    if big:
        print("\nBiggest expense:")
        print(f"  - €{big['amount']:.2f} | {big['category']} | {big['date'].isoformat()} | {big['note']}")
    else:
        print("\nBiggest expense: (none)")


# -----------------------------
# Feature 5: Monthly budget warnings
# -----------------------------

def set_budgets():
    """
    Lets user define budgets per category for a month.
    Returns dict category -> budget amount.
    """
    budgets = {}
    print("\nSet monthly budgets (enter blank category to stop).")
    while True:
        cat = safe_input("Category (blank to finish): ")
        if cat == "":
            break
        try:
            cat = clean_category(cat)
        except ValueError as e:
            print(f"❌ {e}")
            continue

        amount_str = safe_input(f"Monthly budget for {cat} (€): ")
        try:
            amt = parse_amount(amount_str)
            if amt < 0:
                print("❌ Budget must be positive.")
                continue
            budgets[cat] = amt
        except ValueError as e:
            print(f"❌ {e}")

    if budgets:
        print("✅ Budgets set.")
    else:
        print("No budgets set.")
    return budgets


def budget_warnings(transactions, budgets, month):
    """
    Prints warnings if spending exceeds budget for the given month.
    month format: YYYY-MM
    """
    if not budgets:
        print("\nNo budgets set.")
        return

    by_cat = totals_by_category(transactions, month)
    print(f"\n💸 Budget check for {month}")
    any_warning = False

    for cat, limit in budgets.items():
        spent = by_cat.get(cat, 0.0)
        if spent > limit:
            any_warning = True
            over = spent - limit
            print(f"⚠️ {cat}: spent €{spent:.2f} (budget €{limit:.2f}) → over by €{over:.2f}")
        else:
            print(f"✅ {cat}: spent €{spent:.2f} / €{limit:.2f}")

    if not any_warning:
        print("🎉 No categories are over budget.")


# -----------------------------
# Feature 6: Export summary report
# -----------------------------

def export_summary_report(transactions, filename, month=None):
    """
    Exports a summary report to a .txt file.
    """
    total = total_spending(transactions, month)
    by_cat = totals_by_category(transactions, month)
    big = biggest_expense(transactions, month)

    lines = []
    header = f"Summary Report - {month}" if month else "Summary Report - All time"
    lines.append(header)
    lines.append("=" * len(header))
    lines.append(f"Total spending: €{total:.2f}")
    lines.append("")

    lines.append("Spending by category:")
    if not by_cat:
        lines.append("  (no spending transactions)")
    else:
        for cat in sorted(by_cat.keys()):
            lines.append(f"  - {cat}: €{by_cat[cat]:.2f}")

    lines.append("")
    lines.append("Biggest expense:")
    if big:
        lines.append(f"  - €{big['amount']:.2f} | {big['category']} | {big['date'].isoformat()} | {big['note']}")
    else:
        lines.append("  (none)")

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"✅ Exported report to: {filename}")
    except Exception as e:
        print(f"⚠️ Could not export report: {e}")


# -----------------------------
# Feature 7: Charts (optional)
# -----------------------------

def plot_category_spending(transactions, month=None):
    """
    Plots spending by category as a simple bar chart.
    Requires matplotlib. If not installed, prints a message.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️ matplotlib is not installed, so charts are unavailable.")
        return

    data = totals_by_category(transactions, month)
    if not data:
        print("No spending to plot.")
        return

    categories = sorted(data.keys())
    values = [data[c] for c in categories]

    plt.figure()
    plt.bar(categories, values)
    title = f"Spending by Category ({month})" if month else "Spending by Category (All time)"
    plt.title(title)
    plt.xlabel("Category")
    plt.ylabel("Spending (€)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()


# -----------------------------
# Extra: list + delete + menu UI
# -----------------------------

def list_transactions(transactions, month=None):
    """
    Prints transactions (optionally filtered by month).
    """
    tx = list(filter_by_month(transactions, month))
    if not tx:
        print("\n(no transactions)")
        return

    tx.sort(key=lambda t: (t["date"], t["category"]))
    print("\nTransactions:")
    for i, t in enumerate(tx, start=1):
        sign = "-" if t["amount"] < 0 else ""
        print(f"{i:>3}. {t['date'].isoformat()} | {sign}€{abs(t['amount']):.2f} | {t['category']} | {t['note']}")


def delete_transaction(transactions):
    """
    Deletes a transaction by index (based on the current ordering).
    """
    if not transactions:
        print("No transactions to delete.")
        return

    # Show all transactions with indices
    sorted_tx = sorted(transactions, key=lambda t: (t["date"], t["category"]))
    for i, t in enumerate(sorted_tx, start=1):
        sign = "-" if t["amount"] < 0 else ""
        print(f"{i:>3}. {t['date'].isoformat()} | {sign}€{abs(t['amount']):.2f} | {t['category']} | {t['note']}")

    choice = safe_input("Enter the number to delete (or blank to cancel): ")
    if choice == "":
        return

    try:
        idx = int(choice)
        if idx < 1 or idx > len(sorted_tx):
            print("❌ Invalid number.")
            return
    except ValueError:
        print("❌ Please type a valid integer.")
        return

    # Remove the chosen transaction from the original list
    to_remove = sorted_tx[idx - 1]
    transactions.remove(to_remove)
    print("✅ Deleted.")


def ask_month_optional():
    """
    Ask user for a month in YYYY-MM or blank for all time.
    """
    month = safe_input("Month (YYYY-MM) or press Enter for all time: ")
    return month if month else None


def main():
    csv_file = "transactions.csv"
    report_file = "summary_report.txt"

    transactions = load_transactions(csv_file)
    budgets = {}  # category -> monthly budget

    while True:
        print("\n" + "-" * 40)
        print("Personal Finance Tracker")
        print("-" * 40)
        print("1) Add transaction")
        print("2) List transactions")
        print("3) Show summary")
        print("4) Delete transaction")
        print("5) Set monthly budgets")
        print("6) Check budget warnings")
        print("7) Export summary report")
        print("8) Plot spending by category (optional)")
        print("9) Save & Exit")

        choice = safe_input("Choose an option (1-9): ")

        if choice == "1":
            add_transaction(transactions)

        elif choice == "2":
            month = ask_month_optional()
            list_transactions(transactions, month)

        elif choice == "3":
            month = ask_month_optional()
            print_summary(transactions, month)

        elif choice == "4":
            delete_transaction(transactions)

        elif choice == "5":
            budgets = set_budgets()

        elif choice == "6":
            month = safe_input("Month for budget check (YYYY-MM): ")
            budget_warnings(transactions, budgets, month)

        elif choice == "7":
            month = ask_month_optional()
            export_summary_report(transactions, report_file, month)

        elif choice == "8":
            month = ask_month_optional()
            plot_category_spending(transactions, month)

        elif choice == "9":
            save_transactions(csv_file, transactions)
            print(f"✅ Saved to {csv_file}. Bye!")
            break

        else:
            print("❌ Invalid choice. Please pick 1-9.")


if __name__ == "__main__":
    main()