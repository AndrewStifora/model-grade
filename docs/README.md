# docs

- `eval-report.md`: how well the grader does on the labeled evals, per prompt, with caveats and how to reproduce.
- `social-preview.png`: the repository's social preview and README banner (1280x640, GitHub's recommended size). The gauge variant.
- `social-preview-alt-blocks.png`: the alternate composition (four rising blocks with the chosen tier lit), kept as a backup.
- `hero-gauge.png`, `hero-blocks.png`: the illustrations the two previews were composed from (generated with an image model, no text).
- `social-preview.py`: composes a preview from a hero image: fits it to 1280x640, fades the left half for the text, and sets the title, tagline, and meta line in Inter and JetBrains Mono (downloaded on first run). Requires Pillow.

To regenerate or switch:

```
python docs/social-preview.py --hero docs/hero-gauge.png  --out docs/social-preview.png
python docs/social-preview.py --hero docs/hero-blocks.png --out docs/social-preview.png
```

GitHub has no API for the social preview, so after changing the file upload it by hand: repository Settings, General, Social preview, Upload an image. The Social preview section exists only on public repositories; a private repository has no such setting, so the upload waits until the repository is public.
