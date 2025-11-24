#!/usr/bin/env fish

# Colors for output
set -l GREEN '\033[0;32m'
set -l RED '\033[0;31m'
set -l YELLOW '\033[1;33m'
set -l NC '\033[0m' # No Color

printf "%b%s%b\n" "$YELLOW" "[*] Starting Django migrations..." "$NC"

# Run makemigrations
printf "%b%s%b\n" "$YELLOW" "[1] Running makemigrations..." "$NC"
python manage.py makemigrations
if test $status -ne 0
    printf "%b%s%b\n" "$RED" "[✗] makemigrations failed!" "$NC"
    exit 1
end

# Run migrate
printf "%b%s%b\n" "$YELLOW" "[2] Running migrate..." "$NC"
python manage.py migrate
if test $status -ne 0
    printf "%b%s%b\n" "$RED" "[✗] migrate failed!" "$NC"
    exit 1
end

printf "%b%s%b\n" "$GREEN" "[✓] Database migrations completed successfully!" "$NC"