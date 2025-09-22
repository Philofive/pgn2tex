#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pgn2tex_start_and_solution_grid.py
Zwei Modi mit identischer Zellhöhe (Raster bleibt ident):
  --mode start           : nur Anfangsdiagramm (feste Zellhöhe)
  --mode start+solution  : Anfangsdiagramm + Lösungstext (gleiches Raster)

Notation:
  --notation english|german|symbols   (Default: symbols)
    english: K,Q,R,B,N
    german : K,D,T,L,S
    symbols: \king{}, \queen{}, \rook{}, \bishop{}, \knight{} (LaTeX-Makros aus skak/xskak)

Weitere Optionen siehe argparse unten.
"""

import argparse, io, sys
from pathlib import Path
import chess, chess.pgn

# ---------- LaTeX Templates (einheitlich, feste Zellhöhe) ----------
TEX_PREAMBLE = r"""\documentclass[a4paper,11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}

\usepackage{xskak}
\usepackage{chessboard}
\usepackage{geometry}
\usepackage{multicol}
\usepackage{parskip}
\geometry{margin=2.0cm}
\setlength{\columnsep}{14pt}
\setlength{\parindent}{0pt}

% Zelle mit fixer Höhe: optional Titel, dann Diagramm (ohne Lösung)
\newcommand{\cellstartonly}[6]{%
  % args: 1=title 2=subtitle 3=FEN 4=opts 5=cellheight(cm) 6=withtext(flag)
  \noindent\begin{minipage}[t][#5][t]{\linewidth}%
    \ifx#6\empty\else
      \textbf{\small #1}\\%
      \if\relax\detokenize{#2}\relax\else\emph{\scriptsize #2}\\[0.3ex]\fi
    \fi
    \newchessgame\fenboard{#3}\chessboard[#4]%
  \end{minipage}\par
}

% Zelle mit fixer Höhe: optional Titel, Diagramm + Lösung
\newcommand{\cellstartsolution}[7]{%
  % args: 1=title 2=subtitle 3=FEN 4=opts 5=cellheight(cm) 6=withtext(flag) 7=solution text
  \noindent\begin{minipage}[t][#5][t]{\linewidth}%
    \ifx#6\empty\else
      \textbf{\small #1}\\%
      \if\relax\detokenize{#2}\relax\else\emph{\scriptsize #2}\\[0.3ex]\fi
    \fi
    \newchessgame\fenboard{#3}\chessboard[#4]%
    \par\vspace{0.4ex}%
    {\scriptsize #7}%
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

# ---------- Helpers ----------
def tex_escape(s: str) -> str:
    # nur wirklich problematische Zeichen escapen (Backslashes NICHT escapen – wir brauchen Makros!)
    return s.replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")

def start_fen_from_game(game: chess.pgn.Game) -> str:
    if game.headers.get("SetUp") == "1" and "FEN" in game.headers:
        fen = game.headers["FEN"]
        try:
            chess.Board(fen); return fen
        except Exception:
            return chess.STARTING_FEN
    return chess.STARTING_FEN

# --- Notation mapping ---
MAP_GERMAN = {"K":"K","Q":"D","R":"T","B":"L","N":"S"}
# Symbole als LaTeX-Makros (robust unter pdfLaTeX/XeLaTeX):
MAP_SYMBOL_TEX = {"K": r"\king{}", "Q": r"\queen{}", "R": r"\rook{}", "B": r"\bishop{}", "N": r"\knight{}"}

def convert_san_letters(san: str, notation: str) -> str:
    """
    english  -> unverändert
    german   -> K/D/T/L/S
    symbols  -> LaTeX-Makros aus skak/xskak (\king{}, \queen{} ...)
    Achtet auch auf Promotion (=Q, =N, ...).
    """
    if notation == "english":
        return san
    if notation == "german":
        for en, de in MAP_GERMAN.items():
            san = san.replace("="+en, "="+de)  # Promotion zuerst
            san = san.replace(en, de)
        return san
    # symbols: LaTeX-Makros (keine Unicode-Zeichen!)
    for en, macro in MAP_SYMBOL_TEX.items():
        san = san.replace("="+en, "="+macro)  # e8=\queen{}
        san = san.replace(en, macro)          # \knight{}f3
    return san

def san_mainline_with_numbers(game: chess.pgn.Game, notation: str) -> str:
    """SAN-Zugliste mit Zugnummern, aus Start-FEN; Notation umgestellt nach Option."""
    board = chess.Board(start_fen_from_game(game))
    parts = []
    for mv in game.mainline_moves():
        san = board.san(mv)
        san = convert_san_letters(san, notation)
        if board.turn == chess.WHITE:   # vor push: Weiß ist am Zug ⇒ mv ist ein Weiß-Zug
            parts.append(f"{board.fullmove_number}. {san}")
        else:
            parts.append(san)
        board.push(mv)
    res = game.headers.get("Result", "").strip()
    if res in {"1-0","0-1","1/2-1/2","*"} and res:
        parts.append(res)
    return tex_escape(" ".join(parts))

def should_inverse_from_fen(fen: str, mode: str) -> bool:
    if mode == "on": return True
    if mode == "off": return False
    try:
        return chess.Board(fen).turn == chess.BLACK
    except Exception:
        return False

def chessboard_opts(fontsize_pt: int, inverse: bool, hide_mover: bool) -> str:
    opts = [f"boardfontsize={fontsize_pt}pt"]
    if inverse: opts.append("inverse")
    if hide_mover: opts.append("showmover=false")
    return ",".join(opts)

def parse_pgn_stream(stream: io.TextIOBase):
    while True:
        game = chess.pgn.read_game(stream)
        if game is None: break
        yield game

# ---------- Writer ----------
def write_doc(pgn_path: Path, out_path: Path, mode: str, fontsize: int, inverse_mode: str,
              hide_mover: bool, with_text: bool, cellheight_cm: float, rows_per_col: int,
              notation: str, debug: bool):
    with pgn_path.open("r", encoding="utf-8", errors="replace") as pgn, \
         out_path.open("w", encoding="utf-8") as fh:

        fh.write(TEX_PREAMBLE)
        blocks = 0

        for idx, game in enumerate(parse_pgn_stream(pgn), start=1):
            fen = start_fen_from_game(game)
            if debug:
                w = game.headers.get("White","?"); b = game.headers.get("Black","?"); r = game.headers.get("Result","*")
                print(f"[{idx}] FEN: {fen}  {w} — {b} ({r})", file=sys.stderr)

            title = subtitle = ""
            if with_text:
                w = tex_escape(game.headers.get("White","Weiß"))
                b = tex_escape(game.headers.get("Black","Schwarz"))
                r = tex_escape(game.headers.get("Result","*"))
                event  = tex_escape(game.headers.get("Event",""))
                site   = tex_escape(game.headers.get("Site",""))
                date   = tex_escape(game.headers.get("Date",""))
                title = f"{w} — {b} ({r})"
                subtitle = " · ".join(x for x in [event, site, date] if x)

            opts = chessboard_opts(fontsize, should_inverse_from_fen(fen, inverse_mode), hide_mover)
            withtextflag = "1" if with_text else ""

            if mode == "start":
                fh.write("\\cellstartonly{{{}}}{{{}}}{{{}}}{{{}}}{{{:.2f}cm}}{{{}}}\n".format(
                    title, subtitle, fen, opts, cellheight_cm, withtextflag))
            else:  # start+solution
                moves = san_mainline_with_numbers(game, notation=notation)
                fh.write("\\cellstartsolution{{{}}}{{{}}}{{{}}}{{{}}}{{{:.2f}cm}}{{{}}}{{{}}}\n".format(
                    title, subtitle, fen, opts, cellheight_cm, withtextflag, moves))

            blocks += 1
            if (blocks % rows_per_col) == 0:
                filled_cols = blocks // rows_per_col
                fh.write("\\columnbreak\n" if (filled_cols % 2) == 1 else "\\newpage\n")

        fh.write(TEX_END)

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser(
        description="PGN → TeX: (1) nur Anfangsdiagramm, (2) Anfangsdiagramm + Lösung (Raster, gleiche Zellhöhe)."
    )
    ap.add_argument("input", help="PGN-Datei")
    ap.add_argument("--mode", choices=["start","start+solution"], default="start",
                    help="Ausgabemodus (Default: start)")
    ap.add_argument("-o","--output", help="Zieldatei .tex (Default abhängig vom Modus)")
    ap.add_argument("--fontsize", type=int, default=20, help="boardfontsize in pt (Default: 20)")
    ap.add_argument("--inverse", choices=["auto","on","off"], default="auto",
                    help="Brettdrehung: auto|on|off (Default: auto)")
    ap.add_argument("--hide-mover", action="store_true", help="chessboard: showmover=false")
    ap.add_argument("--with-text", action="store_true", help="Titel/Untertitel über dem Brett")
    ap.add_argument("--cellheight", type=float, default=8.2, help="Zellhöhe in cm (Default: 8.2)")
    ap.add_argument("--rows-per-page", type=int, default=3, help="Zeilen pro Spalte (Default: 3 ⇒ 6/Seite)")
    ap.add_argument("--notation", choices=["english","german","symbols"], default="symbols",
                    help="Figurennotation in der Lösung: english|german|symbols (Default: english)")
    ap.add_argument("--debug", action="store_true", help="Debug-Ausgaben (FEN je Partie) auf STDERR")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"Datei nicht gefunden: {in_path}", file=sys.stderr); sys.exit(1)

    if args.output:
        out_path = Path(args.output)
    else:
        suffix = "_start.tex" if args.mode == "start" else "_start_solution.tex"
        out_path = in_path.with_suffix(suffix)

    write_doc(
        pgn_path=in_path,
        out_path=out_path,
        mode=args.mode,
        fontsize=args.fontsize,
        inverse_mode=args.inverse,
        hide_mover=args.hide_mover,
        with_text=args.with_text,
        cellheight_cm=max(0.1, args.cellheight),
        rows_per_col=max(1, args.rows_per_page),
        notation=args.notation,
        debug=args.debug,
    )
    print(f"written: {out_path}")

if __name__ == "__main__":
    main()
