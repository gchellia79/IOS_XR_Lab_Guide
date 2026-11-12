# IOS_XR_Lab_Guide

English-language MkDocs Material lab guide covering preparation, IOS XR commit configuration, operations and monitoring, and BGP. There is no standalone ISIS/segment-routing chapter.

## Run locally

```text
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Open the address printed by MkDocs, normally http://127.0.0.1:8000.

```text
mkdocs build --strict
```

## Extract a Word update

Install the extraction-only dependency in the virtual environment:

```text
pip install python-docx
python tools/docx_extract.py IOS_XR_Lab_Guide_0.1.docx --output _import
```

Review the extracted Markdown before integrating changes. The extractor masks credential values in text, but screenshots require a separate visual review.

## Add screenshots

1. Review screenshots for passwords, tokens, API keys, and other credentials. Redact them before publishing.
2. Add each screenshot to its chapter's `images/` directory, using `image01.png`, `image02.png`, and so on in order of appearance.
3. Use a relative Markdown reference:

   ```markdown
   ![Description of the command output](images/image01.png)
   ```

4. If a necessary screenshot is missing, use a comment rather than a broken link:

   ```html
   <!-- SCREENSHOT: images/imageNN.png | what it should show -->
   ```

5. Run `mkdocs build --strict` before pushing.

Never commit the source Word document, `_import/`, `.venv/`, `site/`, or credentials. Use placeholders such as `<password>`.

## Publish

GitHub Pages is built by `.github/workflows/deploy.yml` on pushes to `main` or a manual workflow run. Set the repository's Pages source to **GitHub Actions**.

Published site: https://gchellia79.github.io/IOS_XR_Lab_Guide/

## Conversion record

Source: `IOS_XR_Lab_Guide_0.1.docx`. Extraction produced 50 images and one table, with nine credential values or pairs masked. The four major topics are preparation, commit configuration, operations and monitoring, and BGP.

Image ranges map one-to-one in document order:

| Original extracted image | Published chapter image |
| --- | --- |
| `image01.png` through `image12.png` | `docs/01-preparation/images/image01.png` through `image12.png` |
| `image13.png` through `image14.png` | `docs/02-commit-configuration/images/image01.png` through `image02.png` |
| `image15.png` through `image35.png` | `docs/03-operations-and-monitoring/images/image01.png` through `image21.png` |
| `image36.png` through `image50.png` | `docs/04-bgp/images/image01.png` through `image15.png` |

The chapter pages retain TODO warnings for these source ambiguities or missing outputs:

- Commit sample: missing `#` in the prompt before `exit`.
- Best-effort commit: failed-commit output is not supplied.
- Rollback: command output is not supplied.
- Process inspection: `show process` versus `show processes`, with no post-restart capture.
- Describe exercise: source spelling `vpn4` and missing spawned-process output.
- User groups: inconsistent `LEVEL_1` / `level_1` spelling and angle-bracket command notation.
- CE-2: `51.1.1.1/32` versus the later `Lo100` reference, with no complete PE-2/CE-2 configuration.
- Policy editor: the source title says Vim while the narration says Emacs.

The text masking covers `password`, `passwd`, `secret`, `token`, and login-related username/password pairs. All 50 images were screened with local OCR; flagged login-related captures were visually checked and contained no visible password or token values. No additional CLI output was invented.