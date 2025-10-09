# 📝 mynotes — jednoduché poznámky v terminálu

> Barevné poznámky, tagy, exporty do TXT/MD/PDF a doplňování po stisku `TAB`.

---

## 🚀 Instalace

### 1️⃣ Naklonuj nebo rozbal projekt
```bash
git clone https://github.com/uzivatel/mynotes.git
cd mynotes
```

Nebo pokud máš ZIP:
```bash
unzip mynotes_project_autocomplete.zip
cd mynotes_project
```

---

### 2️⃣ Nainstaluj lokálně
```bash
pip install -e .
```

To přidá příkaz `mynotes` do tvého Python prostředí.

> 💡 Volitelně pro export do PDF:
> ```bash
> pip install reportlab
> ```

---

## ⚙️ Aktivace doplňování (autocomplete)

`mynotes` používá knihovnu **argcomplete**, která umožňuje doplňování příkazů a argumentů po stisku `TAB`.

---

### 🐚 Bash
Spusť:
```bash
python -m argcomplete.global
```
To jednou provždy zapne doplňování pro všechny Python CLI nástroje (včetně `mynotes`).

Pro jistotu obnov shell:
```bash
source ~/.bashrc
```

---

### 🌀 Zsh
```bash
autoload -U bashcompinit && bashcompinit
eval "$(register-python-argcomplete --shell zsh mynotes)"
```
Pro trvalé nastavení přidej poslední řádek do `~/.zshrc`.

---

### 🐟 Fish
```bash
register-python-argcomplete --shell fish mynotes | source
```
Trvale:
```bash
register-python-argcomplete --shell fish mynotes > ~/.config/fish/completions/mynotes.fish
```

---

## ⚡ Zkratka `my`

Chceš psát jen `my` místo `mynotes`?
```bash
alias my="mynotes"
```
Trvale:
```bash
echo 'alias my="mynotes"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🧠 Základní použití

### Přidání poznámky
```bash
mynotes add "Koupit mléko"
mynotes add "Dokončit prezentaci" --tags skola fll
```

### Výpis poznámek
```bash
mynotes list
mynotes list --tag skola
```
> `list` zobrazuje přehlednou tabulku s barevnými tagy (přes **Rich**).  
> Použij `--plain` pro obyčejný textový výstup.

### Úprava poznámky
```bash
mynotes edit 2 --text "Koupit mléko a vejce"
mynotes edit 2 --add-tags ftc --remove-tags skola
```

### Smazání
```bash
mynotes delete 1
```

---

## 🏷️ Tagy

### Seznam všech tagů
```bash
mynotes tag list
```

### Přidání nového tagu
```bash
mynotes tag add skola --color bright_blue
```

### Úprava tagu
```bash
mynotes tag edit skola --new-name škola --color yellow
```

### Smazání tagu
```bash
mynotes tag delete fll
```

> Barvy:  
> `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`  
> + všechny varianty `bright_*`  
> Např. `bright_blue`, `bright_yellow`.

Tagy jsou kontrastní:  
- světlé barvy → černý text  
- tmavé barvy → bílý text

---

## 📤 Export

### Do textu
```bash
mynotes export --format txt --out notes.txt
```
### Do Markdownu
```bash
mynotes export --format md --out notes.md --tag ftc
```
### Do PDF
```bash
mynotes export --format pdf --out notes.pdf
```

> PDF export používá `reportlab` (pokud je nainstalován), jinak se vytvoří jednoduchý PDF soubor bez závislostí.

---

## 📦 Kam se ukládají data
- Poznámky: `~/.mynotes.json`  
- Tagy a barvy: `~/.mynotes_tags.json`

Chceš uložit jinam?
```bash
MYNOTES_PATH=/cesta/notes.json MYNOTES_TAGS_PATH=/cesta/tags.json mynotes list
```

---

## 🧩 Autocomplete v akci
Zkus psát a mačkej `TAB`:
```bash
mynotes [TAB]          # → add, list, edit, delete, tag, export
mynotes tag [TAB]      # → list, add, edit, delete
mynotes list --tag [TAB]  # → nabídne existující tagy
mynotes edit [TAB]        # → nabídne ID existujících poznámek
```

---

## 💡 Tipy
- `mynotes --l` je zkratka pro `mynotes list`
- `mynotes --a "text"` přidá poznámku
- `mynotes --d 3` smaže poznámku s ID 3

---

## 🧰 Řešení problémů

### ❌ `mynotes: command not found`
- Ujisti se, že máš aktivní Python prostředí (např. `venv`)
- Zkus `pip install -e .` znovu  
- Nebo spusť ručně:  
  ```bash
  python -m mynotes.cli
  ```

### ❌ Autocompletion nefunguje
- Spusť:
  ```bash
  python -m argcomplete.global
  ```
- Restartuj terminál nebo proveď `source ~/.bashrc`

---

## 🎨 Ukázka výpisu

```
📒 mynotes
┏━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID┃ Poznámka           ┃ Tagy       ┃ Vytvořeno    ┃ Upraveno     ┃
┣━━━╋━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━╋━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━┫
┃ 1 ┃ Koupit mléko       ┃ skola fll  ┃ před 5 min   ┃ -            ┃
┃ 2 ┃ Dokončit prezentaci┃ ftc        ┃ před 1 h     ┃ před 10 min  ┃
┗━━━┻━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━┻━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━┛
```

---

## Autor
**Antonín Šiška**  
CLI utilita vytvořená v Pythonu pomocí knihoven `argparse`, `rich`, `argcomplete` a `reportlab`.  
Verze: 0.3.0


#### © 2025 Antonín Šiška  
Released under the [MIT License](./LICENSE)
