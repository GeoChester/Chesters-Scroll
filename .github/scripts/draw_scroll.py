name: Draw Chester's scroll

on:
  push:
    paths:
      - finders.json
      - .github/scripts/draw_scroll.py
      - .github/workflows/draw-scroll.yml
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: draw-scroll
  cancel-in-progress: false

jobs:
  draw:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Pillow
        run: pip install pillow==11.0.0

      - name: Get the scroll fonts
        run: |
          mkdir -p .fonts
          base=https://raw.githubusercontent.com/google/fonts/main/ofl
          curl -sSLf -o .fonts/PirataOne.ttf "$base/pirataone/PirataOne-Regular.ttf" || echo "Could not download PirataOne.ttf, using a standard font instead."
          curl -sSLf -o .fonts/CrimsonPro.ttf "$base/crimsonpro/CrimsonPro%5Bwght%5D.ttf" || echo "Could not download CrimsonPro.ttf, using a standard font instead."
          curl -sSLf -o .fonts/CrimsonPro-Italic.ttf "$base/crimsonpro/CrimsonPro-Italic%5Bwght%5D.ttf" || echo "Could not download CrimsonPro-Italic.ttf, using a standard font instead."

      - name: Draw scroll.png
        run: python .github/scripts/draw_scroll.py

      - name: Save the new picture
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898283+github-actions[bot]@users.noreply.github.com"
          git add scroll.png
          if git diff --cached --quiet; then
            echo "The scroll picture is already up to date."
          else
            git commit -m "Redraw Chester's scroll"
            git push
          fi
