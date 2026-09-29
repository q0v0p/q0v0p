# Today 漢字

`kanji_date.py` は今日の日付を毛筆で書く SVG アニメーションを作る。
GitHub Actions (`.github/workflows/kanji-date.yml`) が毎日 0:05 (日本時間) に実行し、`output` ブランチへ置く。

```
python scripts/kanji_date.py out.svg 2026-12-29
```

## 素材とライセンス

- `glyphs.json`: 毛筆体 [Yuji Boku](https://github.com/Kinutafontfactory/Yuji) から、日付に使う字の輪郭だけを取り出したもの。SIL Open Font License 1.1 (`OFL-YujiBoku.txt`)
- `kanjivg/`: [KanjiVG](https://kanjivg.tagaini.net) の書き順データ。© Ulrich Apel, CC BY-SA 3.0。作った SVG もこれに従う

# サイバーバナー

`cyber_banner.py` はプロフィール下部のバナー (`assets/cyber.svg`) を作る。日付に依存しないので、変えたときだけ手で実行してコミットする。

```
python scripts/cyber_banner.py
```

「忍」の輪郭も `glyphs.json` (Yuji Boku) から使っている。
