# Today 漢字

プロフィールの「今日の漢字」は [fude](https://github.com/q0v0p/fude) の Action で作っている
(`.github/workflows/kanji-date.yml`)。毎日 0:05 (日本時間) に実行し、`output` ブランチの `date-kanji.svg` を置き換える。

# サイバーバナー

`cyber_banner.py` はプロフィール上部のバナー (`assets/cyber.svg`) を作る。日付に依存しないので、変えたときだけ手で実行してコミットする。

```
python scripts/cyber_banner.py
```

「忍」の輪郭は毛筆体 [Yuji Boku](https://github.com/Kinutafontfactory/Yuji) から取り出したもの (`glyphs.json`)。SIL Open Font License 1.1 (`OFL-YujiBoku.txt`)。
