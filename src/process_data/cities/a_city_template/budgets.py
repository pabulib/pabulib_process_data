budgets = {
    # Replace this with the source link or relevant documentation URL
    # "source": "URL-to-official-budget-documentation",
    # Example year data (replace with actual city-specific data)
    2025: {
        "CITYWIDE": 0,  # citywide budget allocation
        "DISTRICT_1": 0,  # Placeholder for district 1 budget
        "DISTRICT_2": 0,  # Placeholder for district 2 budget
        "DISTRICT_3": 0,  # Placeholder for district 3 budget
        # Add more districts as needed
    },
    2024: {
        "CITYWIDE": 0,
        "DISTRICT_1": 0,
        "DISTRICT_2": 0,
        "DISTRICT_3": 0,
        # Add more districts as needed
    },
}

# Sum check logic (reuse for validation)
year = 2025
sum = 0
year_budget = budgets[year]
for budget in year_budget.values():
    sum += budget

print(sum)
