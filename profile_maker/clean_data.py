import re
import json
from datetime import datetime
from pathlib import Path

INPUT_FILE = "profile_maker/data/chat_history.txt"
OUTPUT_JSON = "profile_maker/data/chat_clean.json"
OUTPUT_TXT = "profile_maker/data/chat_clean.txt"

# [27/01/2026 18:50] username
HEADER_RE = re.compile(r"\[(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\]\s+(.*)")

# Anything that looks like a URL
URL_RE = re.compile(r"https?://\S+")

# Lines that indicate attachments / stickers / embeds
ATTACHMENT_TOKENS = {
    "{Embed}",
    "{Attachments}",
    "{Stickers}",
    "{Reactions}"
}

# System / non-message noise
SYSTEM_PHRASES = {
    "Joined the server.",
    "Left the server.",
}

def is_text_line(line: str) -> bool:
    """Return True if line is human-typed text (not an attachment or embed)."""
    line = line.strip()
    if not line:
        return False
    if line in ATTACHMENT_TOKENS:
        return False
    if URL_RE.search(line):
        return False
    return True


def parse_chat(file_path: str):
    messages = []
    current = None

    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip()

            # Skip export footer / separators
            if line.startswith("=") or line.startswith("Exported"):
                continue

            header_match = HEADER_RE.match(line)
            if header_match:
                # Save previous message
                if current:
                    content = current["content"].strip()
                    if content and content not in SYSTEM_PHRASES:
                        current["content"] = content
                        messages.append(current)

                timestamp_str, user = header_match.groups()
                timestamp = datetime.strptime(
                    timestamp_str, "%d/%m/%Y %H:%M"
                ).isoformat()

                current = {
                    "timestamp": timestamp,
                    "user": user,
                    "content": ""
                }
                continue

            # Only keep human-typed text lines
            if current is not None and is_text_line(line):
                if current["content"]:
                    current["content"] += " "
                current["content"] += line

        # Append last message
        if current:
            content = current["content"].strip()
            if content and content not in SYSTEM_PHRASES:
                current["content"] = content
                messages.append(current)

    return messages


def write_outputs(messages):
    # JSON output
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    # Clean text output
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        for msg in messages:
            ts = msg["timestamp"].replace("T", " ")[:16]
            line = f"{ts} | {msg['user']}: {msg['content']}"
            f.write(line + "\n")


def main():
    if not Path(INPUT_FILE).exists():
        print(f"Input file '{INPUT_FILE}' not found.")
        return

    messages = parse_chat(INPUT_FILE)
    write_outputs(messages)

    print(f"Processed {len(messages)} clean text messages.")
    print("Output written to:")
    print(f" - {OUTPUT_JSON}")
    print(f" - {OUTPUT_TXT}")


if __name__ == "__main__":
    main()