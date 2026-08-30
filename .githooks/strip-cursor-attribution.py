"""Remove Cursor attribution lines from git commit messages."""
import sys

BLOCKLIST = (
    'cursoragent@cursor.com',
    'Co-authored-by: Cursor',
    'Made-with: Cursor',
)


def main():
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as handle:
        lines = handle.readlines()
    filtered = [line for line in lines if not any(token in line for token in BLOCKLIST)]
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        handle.writelines(filtered)


if __name__ == '__main__':
    main()
