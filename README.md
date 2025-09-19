# pgn2tex
Python Konverter(s) from pgn to tex via python-library chess. First release of fen2tex.y was part of a "homework"-project for an austrian chess-trainer-course.

### requirements
Any recent python installation suffices.

pip install -r requirements.txt

### Usage

#### Fen2Tex 
```
> python pgn2tex/fen2tex.py --help

converts a PGN file to a latex document. It is supposed to be used to create chess diagrams from PGN files with FEN-Keys only, as it is often used for training exercises.
6 diagrams per A4-page as a standard, but adjustable

positional arguments:
  file                  PGN File to parse

options:
  -h, --help            show this help message and exit
  
  --inverse {auto, on, off}
                        auto: inverts the board automatically for each position, when it is Black to move.
                        off: always from the perspective of the white player
                        on:  always from the perspective of the black player
                        if no options selected, auto is used

--hide-mover            hides the move-indicator right of the chessboard

--with-text            Writes a Title above the Chessboard, consisting of the PGN-Headers White, Black, Result, Event, Site and Date.

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
