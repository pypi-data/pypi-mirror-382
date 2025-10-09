import re

def check_strength(password):
    score = 0
    remarks = []

    if len(password) >= 8:
        score += 1
    else:
        remarks.append("Password too short (min 8 chars).")
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        remarks.append("Add uppercase letters.")
    if re.search(r"[a-z]", password):
        score += 1
    else:
        remarks.append("Add lowercase letters.")
    if re.search(r"[0-9]", password):
        score += 1
    else:
        remarks.append("Add digits.")
    if re.search(r"[^A-Za-z0-9]", password):
        score += 1
    else:
        remarks.append("Add symbols.")

    levels = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"]
    strength = levels[min(score, 5) - 1]

    return {"score": score, "strength": strength, "remarks": remarks}
