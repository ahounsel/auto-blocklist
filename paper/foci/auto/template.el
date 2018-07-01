(TeX-add-style-hook
 "template"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "letterpaper" "twocolumn" "10pt")))
   (TeX-run-style-hooks
    "latex2e"
    "article"
    "art10"
    "usenix"
    "epsfig"
    "endnotes")
   (LaTeX-add-bibliographies
    "../common/bibliography"))
 :latex)

