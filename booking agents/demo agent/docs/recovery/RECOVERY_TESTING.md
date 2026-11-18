# Recovery Testing

Safe tests only:

1. Isolated `git clone` of parent remote into `/tmp` and verify workspace paths.
2. Emergency pack export to a temp `DR_EXPORT_DIR` and list contents.
3. Recreate QA venv from lock/manifests.

Do **not** delete production calendars or live agents to “test” recovery.
