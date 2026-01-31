from config import Config

INPUT_FILE = "profile_maker/data/chat_clean.txt"
OUTPUT_FILE = "profile_maker/data/chat_user.txt"

TARGET_USER = Config.USERNAME

def filter_by_user():
    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for line in infile:
            line = line.rstrip()

            # Skip empty lines
            if not line:
                continue

            # Check if this line is from the target user
            try:
                _, rest = line.split(" | ", 1)
                user, message = rest.split(":", 1)
            except ValueError:
                continue  # malformed line, ignore

            if user == TARGET_USER:
                # Optional cleanup filters
                if "Joined the server" in message:
                    continue
                if "{Stickers}" in message or "{Reactions}" in message:
                    continue
                if "..." in message:  # <-- skip messages containing "..."
                    continue

                outfile.write(line + "\n")

    print(f"Filtered messages written to {OUTPUT_FILE}")

if __name__ == "__main__":
    filter_by_user()