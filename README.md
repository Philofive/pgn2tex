# pgn2tex
Python Konverter(s) from pgn to tex 


### requirements
Any recent python installation suffices. The only library outside is the  python-library chess.

pip install -r requirements.txt

## Fen2Tex 
Input: PGN-files or valid FEN-keys

Output: .tex-file which should be compiled via XeLaTeX

First release of fen2tex.y was part of a "homework"-project for an austrian chess-trainer-course.

### Usage
```
> python pgn2tex/fen2tex.py --help

usage: fen2tex.py [-h] [-o OUTPUT] [--fen FEN] [--fontsize FONTSIZE] [--rows-per-page ROWS_PER_PAGE] [--inverse {auto,on,off}] [--with-text] [--cellheight CELLHEIGHT] [--hide-mover] [input]

PGN/FEN → TeX with xskak+chessboard, grid, Optionen inverse/hide-mover/with-text.

positional arguments:
  input                 PGN-file (dont use it with --fen)

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   target.tex
  --fen FEN             FEN-key instead of PGN
  --fontsize FONTSIZE   boardfontsize in pt (default: 20)
  --rows-per-page ROWS_PER_PAGE
                        rows/diagrams per-page (default: 3 ⇒ 6 diagrams/page)
  --inverse {auto,on,off}
                        auto: inverts the board automatically for each position, when it is Black to move (default: auto)
  --with-text           title above the chessboard, consisting of the PGN-Headers
  --cellheight CELLHEIGHT
                        (only with --with-text) fixed cell height in cm (default: 8.2)
  --hide-mover          showmover=false (hides the move-indicator)

```
Examples:

```
python fen2tex.py 2025_C_MattbilderGrecoSMS_AF.pgn -o 2025_C_MattbilderGrecoSMS_AF.tex --inverse off --hide-mover
xelatex 2025_C_MattbilderGrecoSMS_AF.tex


python fen2tex.py 2025_C_MattbilderGrecoSMS_AF.pgn -o 2025_C_MattbilderGrecoSMS_AF_anderes_Ausgabeformat.tex --with-text
xelatex 2025_C_MattbilderGrecoSMS_AF_anderes_Ausgabeformat.tex


```

## Pgn2Tex_start_sol.py 
Input: PGN-files or valid FEN-keys


### Usage
```
usage: pgn2tex_start_sol.py [-h] [--mode {start,start+solution}] [-o OUTPUT] [--fontsize FONTSIZE] [--inverse {auto,on,off}] [--hide-mover] [--with-text] [--cellheight CELLHEIGHT] [--rows-per-page ROWS_PER_PAGE]
                            [--notation {english,german,symbols}] [--debug]
                            input

positional arguments:
  input                 PGN-Datei

options:
  -h, --help            show this help message and exit
  --mode {start,start+solution}
                        Ausgabemodus (Default: start)
  -o, --output OUTPUT   Zieldatei .tex (Default abhängig vom Modus)
  --fontsize FONTSIZE   boardfontsize in pt (Default: 20)
  --inverse {auto,on,off}
                        Brettdrehung: auto|on|off (Default: auto)
  --hide-mover          chessboard: showmover=false
  --with-text           Titel/Untertitel über dem Brett
  --cellheight CELLHEIGHT
                        Zellhöhe in cm (Default: 8.2)
  --rows-per-page ROWS_PER_PAGE
                        Zeilen pro Spalte (Default: 3 ⇒ 6/Seite)
  --notation {english,german,symbols}
                        Figurennotation in der Lösung: english|german|symbols (Default: symbols)
  --debug               Debug-Ausgaben (FEN je Partie) auf STDERR

```

Examples:

```
python fen2tex_start_sol.py 2025_C_MattbilderGrecoSMS_AF.pgn  --mode start -o 025_C_MattbilderGrecoSMS_AF_start.tex

python pgn2tex_start_sol.py 2025_C_MattbilderGrecoSMS_AF.pgn  --mode start+solution --notation symbols -o 025_C_MattbilderGrecoSMS_AF_start+solution+symbols.tex

```



