(TeX-add-style-hook
 "paper"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("confpaper" "twocolumn" "10pt")))
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "abstract"
    "introduction"
    "related"
    "approach"
    "evaluation"
    "results"
    "conclusion"
    "acks"
    "confpaper"
    "confpaper10"
    "usenix"
    "epsfig"
    "url"
    "amssymb"
    "CJKutf8"
    "balance"
    "titling")
   (LaTeX-add-bibliographies
    "../common/bibliography"))
 :latex)

