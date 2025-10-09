import sys
from .generator import generate_password
from .checker import check_strength

def main():
    if len(sys.argv) < 2:
        print("Usage: passgenius <command> [args]")
        print("Commands: generate <length>, check <password>")
        return

    command = sys.argv[1].lower()
    if command == "generate":
        length = int(sys.argv[2]) if len(sys.argv) > 2 else 12
        password = generate_password(length)
        print(f"🔑 Generated Password: {password}")
    elif command == "check":
        if len(sys.argv) < 3:
            print("Please provide a password to check.")
            return
        password = sys.argv[2]
        result = check_strength(password)
        print(f"🧠 Password Strength: {result['strength']} ({result['score']}/5)")
        if result['remarks']:
            print("💡 Tips:", "; ".join(result['remarks']))
    else:
        print("Unknown command. Use 'generate' or 'check'.")

if __name__ == "__main__":
    main()
