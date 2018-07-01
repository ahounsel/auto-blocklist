(TeX-add-style-hook
 "usenix"
 (lambda ()
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "url")
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

