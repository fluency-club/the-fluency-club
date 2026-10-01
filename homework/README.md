Homework files for The Fluency Club

## Publishing homework

From the repository root, run:

```sh
python3 scripts/publish-homework.py "$HOME/Downloads/my-homework.html" future
```

This copies the source bytes unchanged into `homework/future.html`, commits only
that file with the message `Add future homework`, pushes `main`, and prints:

```text
https://fluency-club.github.io/the-fluency-club/homework/future.html
```

Use lowercase letters, numbers, and hyphens for names, without `.html`.
Existing homework files are never overwritten. The original file is left intact.
Python 3, Git, and working GitHub push credentials are required.

Before running, the working tree must be clean, the current branch must be `main`,
and local `main` must match GitHub `main`. Both origin URLs must point to
`fluency-club/the-fluency-club`. Commit the helper and these instructions before
first use. The helper fetches to check the remote, then commits and pushes as
part of the same command; run it only when ready to publish.

The helper bypasses Git content conversion when staging and verifies the committed
HTML bytes before pushing. If any step fails, it stops and keeps any new file or
local commit for inspection. If only the push fails, resolve the reported issue
and push the verified commit with `git push origin main`; do not rerun the helper
for the same name. Never force-push to recover.

GitHub Pages may take a few minutes to deploy after a successful push. The helper
prints the expected URL; it does not wait for the deployment.
