# Claude Code Upskilling — Learning Hub

A responsive, accessible, no-backend Learning Management System built around the **real, five-day Claude Code Upskilling course by Swapravo Sinha Roy**.

## Source and attribution

- Repository: https://github.com/swapravo/leave_and_shift_management_system
- **Course source branch:** `claude/bold-gauss-6bzbzk`
- Original files: `content/day-1.md` to `content/day-5.md`, `content/README.md`, and `content/build-plan.md`.
- All original lessons, explanations, answers, and supporting material remain authored by their original author. No synthetic lesson content is generated.

## IMPORTANT: First-time content synchronization

**This distribution contains the complete LMS application, but the five large original Markdown lessons were not embedded in the ZIP due to content-transfer restrictions in the authoring environment.** To obtain the full original material, run the source sync once before serving or publishing. This is **not** a ready-to-view offline content bundle until that step completes.

Prerequisites: Python 3.10 or later and an internet connection for the initial sync. No Node, database, Docker, account, or paid hosting is needed.

```bash
python -m pip install -r requirements.txt
python scripts/build.py --sync
python -m unittest discover -s tests -v
python -m http.server 8000
```

Open http://localhost:8000/ in your browser. Do **not** open `index.html` using `file://`; browser security restricts local JSON fetching.

The sync fetches the seven original Markdown files from the specified repository branch, preserves them verbatim under `content/`, builds a sanitized, searchable `data/course.json`, and automatically enables the entire site. Subsequent local builds:

```bash
python scripts/build.py
```

To intentionally refresh existing source files from the upstream branch:

```bash
python scripts/build.py --refresh
```

Do not run refresh after editing local original files unless you mean to replace those edits.

## Features

- Clean dark-navy sidebar, white cards, restrained purple accents; desktop/tablet/mobile responsive layout.
- Real learner statistics, Continue Learning, ordered five-day course catalog, curriculum roadmap, resume state, progress bars.
- Full lesson reader: original Markdown headings, tables, code, links, blockquotes, examples, navigation and source links.
- On-page heading navigation, bookmarks, mark complete/incomplete, completion-filtered curriculum.
- Search over full lesson content, including text, titles, and descriptions.
- Auto-scored quiz questions **only** where source Markdown explicitly marks an answer with ✅. Other exercises remain in the original lesson text. Quiz attempts persist.
- Light/dark theme, keyboard shortcuts (`/` to search), feedback notices, progress reset confirmation.
- Progress stored locally in the browser's `localStorage`, never synchronized to a server or other devices.
- Markdown HTML disabled by parser; HTML sanitized using Bleach during the build. Untrusted script markup cannot execute from course text.
- No backend or authentication. All runtime content is local after the one-time sync/build.

## Course organization and edits

- Each source `content/day-N.md` is a real day's lesson; ordering is numeric and stable.
- `content/build-plan.md` contains the original detailed demo project plan.
- `scripts/build.py` is the course index generator and Markdown sanitizer.
- Lesson progress uses `day-1`, `day-2`, etc., so edits to a lesson don't reset completion.
- To update or add a day, edit or add a Markdown file and adjust `FILES` and day iteration in `scripts/build.py`; regenerate the manifest.
- For auto-scored quizzes, retain the source's `**Q1.** ...?` and `- A. Answer ✅` notation. The importer supports single- and multiple-correct answers marked ✅. Other questions and explanations remain visible as original Markdown.
- Avoid adding executable HTML or JavaScript to course Markdown; raw source HTML is not executed.

## GitHub Pages deployment

1. Complete the source-sync/build commands above locally (recommended for preview).
2. Upload the entire extracted project to your GitHub repository (usually `main`).
3. In repository **Settings → Pages → Build and deployment**, choose **GitHub Actions**.
4. Push to `main`, or trigger **Actions → Deploy Learning Hub to GitHub Pages → Run workflow**.
5. The workflow installs Python dependencies, fetches the exact course branch, builds sanitized lesson data, runs validation tests, and deploys the static files.
6. A project site is available at `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/` when deployment succeeds.

All frontend paths are relative, so the project-site subdirectory is supported. The workflow deliberately syncs source content during CI; if GitHub is unreachable or a source file changes path, it fails rather than publishing invented or missing lessons.

## Validation

```bash
python -m unittest discover -s tests -v
python scripts/build.py
node --check assets/app.js  # optional when Node is installed
```

The test suite checks required files, content inclusion and ID ordering when content is present, and a basic JS progress contract. Run manual browser checks on a local HTTP server for desktop/mobile layouts, keyboard focus, lesson controls, search, quiz feedback, theme persistence, bookmark persistence, and reset confirmation.

## Security and privacy

Do not place credentials, confidential documents, or internal customer data into `content/`: the built site is publicly downloadable. Local progress is per browser/device; clearing browser storage resets it. The site has no user login or cloud sync.

## Known limitations

- The source repo may add or change files later. The importer tracks the original listed seven files as known during the repository audit; inspect new upstream material separately.
- Source Markdown may contain legacy `.html` references; links to those legacy pages are not rewritten. Other ordinary relative Markdown links are routed to `content/`.
- Quiz detection is conservative and requires a ✅ source marker. The original full practice quizzes remain visible even if a format is not recognized by the interactive parser.
- No browser automation was available during packaging; automated source-content tests must be rerun after syncing the original five days.
- Offline access after build still requires serving the generated files through an HTTP server, unless a separate service worker is added.
