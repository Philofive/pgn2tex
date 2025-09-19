#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fen2tex.py
converts a PGN file to a latex document. It is supposed to be used to create chess diagrams from PGN files with FEN-Keys only, as it is often used for training exercises.
6 diagrams per A4-page as a standard, but adjustable

Features:
- 2 Spalten (multicol), fixes Grid (R pro Spalte → 2R pro Seite)
- Option --inverse auto|on|off
            auto: inverts the board automatically for each position, when it is Black to move.
            off: always from the perspective of the white player
            on:  always from the perspective of the black player
            if no options selected, auto is used
- Option --with-text writes a title above the chessboard, consisting of the PGN-Headers White, Black, Result, Event, Site and Date.
- Option --cellheight cm (only usable --with-text)
- Option --hide-mover hides the move-indicator right of the chessboard
- Option --fontsize adjusts the size of the chessdiagrams
"""

import argparse, io, sys
from pathlib import Path
import chess, chess.pgn

TEX_PREAMBLE = r"""\documentclass[a4paper,11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}

\usepackage{xskak}
\usepackage{chessboard}
\usepackage{geometry}
\usepackage{multicol}
\geometry{margin=2.0cm}
\setlength{\columnsep}{14pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}

\newcommand{\diagramonly}[2]{%
  \noindent\begin{minipage}[t]{\linewidth}%
    \newchessgame
    \fenboard{#1}%
    \chessboard[#2]%
  \end{minipage}\par
}

\newcommand{\diagramtext}[5]{%
  \noindent\begin{minipage}[t][#5][t]{\linewidth}%
    \textbf{\small #1}\\%
    \if\relax\detokenize{#2}\relax\else\emph{\scriptsize #2}\\[0.3ex]\fi
    \newchessgame\fenboard{#3}\chessboard[#4]%
  \end{minipage}\par
}

\begin{document}
\begin{multicols}{2}
\raggedcolumns
"""

TEX_END = r"""
\end{multicols}
\end{document}
"""

def tex_escape(s: str) -> str:
    repl = {"&":r"\&","%":r"\%","$":r"\$","#":r"\#","_":r"\_",
            "{":r"\{","}":r"\}","~":r"\textasciitilde{}",
            "^":r"\textasciicircum{}","\\":r"\textbackslash{}"}
    return "".join(repl.get(c, c) for c in s)

def board_from_game(game: chess.pgn.Game) -> chess.Board:
    if game.headers.get("SetUp") == "1" and "FEN" in game.headers:
        try: board = chess.Board(game.headers["FEN"])
        except Exception: board = chess.Board()
    else:
        board = chess.Board()
    for mv in game.mainline_moves():
        board.push(mv)
    return board

def should_inverse(black_to_move: bool, mode: str) -> bool:
    if mode == "on": return True
    if mode == "off": return False
    return black_to_move  # auto

def make_opts(fontsize_pt: int, do_inverse: bool, hide_mover: bool) -> str:
    opts = [f"boardfontsize={fontsize_pt}pt"]
    if do_inverse:
        opts.append("inverse")
    if hide_mover:
        opts.append("showmover=false")
    return ",".join(opts)

def make_block_only(board: chess.Board, fontsize_pt: int, inverse_mode: str, hide_mover: bool) -> str:
    opts = make_opts(fontsize_pt, should_inverse(board.turn == chess.BLACK, inverse_mode), hide_mover)
    return "\\diagramonly{{{}}}{{{}}}\n".format(board.fen(), opts)

def make_block_text(game: chess.pgn.Game, board: chess.Board, fontsize_pt: int,
                    inverse_mode: str, cellheight_cm: float, hide_mover: bool) -> str:
    white = tex_escape(game.headers.get("White", "Weiß"))
    black = tex_escape(game.headers.get("Black", "Schwarz"))
    result = tex_escape(game.headers.get("Result", "*"))
    event  = tex_escape(game.headers.get("Event", ""))
    site   = tex_escape(game.headers.get("Site", ""))
    date   = tex_escape(game.headers.get("Date", ""))

    title = f"{white} — {black} ({result})"
    subtitle = " · ".join(x for x in [event, site, date] if x)

    opts = make_opts(fontsize_pt, should_inverse(board.turn == chess.BLACK, inverse_mode), hide_mover)
    return "\\diagramtext{{{}}}{{{}}}{{{}}}{{{}}}{{{:.2f}cm}}\n".format(
        title, subtitle, board.fen(), opts, cellheight_cm)

def parse_pgn_stream(stream: io.TextIOBase):
    while True:
        game = chess.pgn.read_game(stream)
        if game is None: break
        yield game

def main():
    ap = argparse.ArgumentParser(description="PGN/FEN → TeX with xskak+chessboard, grid, Optionen inverse/hide-mover/with-text.")
    ap.add_argument("input", nargs="?", help="PGN-file (dont use it with --fen)")
    ap.add_argument("-o","--output", help="target.tex")
    ap.add_argument("--fen", help="FEN-key instead of PGN")
    ap.add_argument("--fontsize", type=int, default=20, help="boardfontsize in pt (default: 20)")
    ap.add_argument("--rows-per-page", type=int, default=3, help="rows/diagrams per-page (default: 3 ⇒ 6 diagrams/page)")
    ap.add_argument("--inverse", choices=["auto","on","off"], default="auto", help="auto: inverts the board automatically for each position, when it is Black to move (default: auto)")
    ap.add_argument("--with-text", action="store_true", help="title above the chessboard, consisting of the PGN-Headers")
    ap.add_argument("--cellheight", type=float, default=8.2, help="(only with --with-text) fixed cell height in cm (default: 8.2)")
    ap.add_argument("--hide-mover", action="store_true", help="showmover=false (hides the move-indicator)")
    args = ap.parse_args()

    # Zielpfad
    if args.output:
        out_path = Path(args.output)
    else:
        if args.fen and not args.input:
            out_path = Path("position_output.tex")
        elif args.input:
            out_path = Path(Path(args.input).with_suffix("").name + ".tex")
        else:
            print("Fehler: Either use PGN-file or use --fen", file=sys.stderr)
            sys.exit(2)

    blocks = []

    if args.fen:
        try:
            board = chess.Board(args.fen)
        except Exception as e:
            print(f"not valid FEN: {e}", file=sys.stderr); sys.exit(1)
        if args.with_text:
            class Dummy: headers = {"White":"FEN-Position","Black":"","Result":"*","Event":"","Site":"","Date":""}
            blocks.append(make_block_text(Dummy, board, args.fontsize, args.inverse, args.cellheight, args.hide_mover))
        else:
            blocks.append(make_block_only(board, args.fontsize, args.inverse, args.hide_mover))
    else:
        try:
            with open(args.input, "r", encoding="utf-8", errors="replace") as pgn:
                for game in parse_pgn_stream(pgn):
                    board = board_from_game(game)
                    if args.with_text:
                        blocks.append(make_block_text(game, board, args.fontsize, args.inverse, args.cellheight, args.hide_mover))
                    else:
                        blocks.append(make_block_only(board, args.fontsize, args.inverse, args.hide_mover))
        except FileNotFoundError:
            print(f"file not found: {args.input}", file=sys.stderr); sys.exit(1)

    R = max(1, args.rows_per_page)

    with out_path.open("w", encoding="utf-8") as fh:
        fh.write(TEX_PREAMBLE)
        for i, b in enumerate(blocks, start=1):
            fh.write(b)
            if (i % R) == 0:
                filled_cols = i // R
                if (filled_cols % 2) == 1:
                    fh.write("\\columnbreak\n")
                else:
                    fh.write("\\newpage\n")
        fh.write(TEX_END)

    print(f"written: {out_path}")

if __name__ == "__main__":
    main()

"""
"""