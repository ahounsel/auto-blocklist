(TeX-add-style-hook
 "foci"
 (lambda ()
   (TeX-run-style-hooks
    "twocolumn"
    "mathptmx")
   (TeX-add-symbols
    "maketitle"
    "thanks"
    "section")
   (LaTeX-add-environments
    "abstract"))
 :latex)

