# pgn2tex
Python Konverter(s) from pgn to tex via python-library chess. First release of fen2tex.y was part of a "homework"-project for an austrian chess-trainer-course.

### requirements
Any recent python installation suffices.

pip install -r requirements.txt

## Fen2Tex 

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


  
  -o OUTPUT, --output OUTPUT
```
