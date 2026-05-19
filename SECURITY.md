# Security Policy

## Supported Use

This repository is a public template. It should contain fake examples only.

Do not commit:

- real `.env` files
- private hosts, IP addresses, or usernames
- API keys, OAuth files, cookies, or session files
- private assistant settings
- runtime logs, transcripts, or memory state

## Reporting

Open a private security advisory on GitHub if you find a real secret or a
dangerous default. If GitHub advisories are unavailable, open an issue that
describes the file and behavior without pasting the secret.

## Public-Template Boundary

Remote sync, process restart, memory injection, and unattended backup behavior
are intentionally represented as inert examples. Users must wire their own
local settings explicitly.
