from .business_engine import calculate_recipe_cost

def production_capacity(db, recipe):
    cost = calculate_recipe_cost(db, recipe)
    return {
        "possible_batches": cost["possible_batches"],
        "possible_liters": cost["possible_liters"],
        "limiting_material": cost["limiting_material"],
    }
