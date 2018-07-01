(TeX-add-style-hook
 "final"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("IEEEtran" "conference" "compsoc")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("cite" "nocompress") ("graphicx" "pdftex") ("subfig" "caption=false" "font=footnotesize" "labelfont=sf" "textfont=sf")))
   (TeX-run-style-hooks
    "latex2e"
    "IEEEtran"
    "IEEEtran10"
    "cite"
    "graphicx"
    "subfig"
    "stfloats"
    "amssymb")
   (LaTeX-add-labels
    "lang"
    "arch"
    "breakdown"
    "all-domains"
    "subset-domains"
    "alexa"
    "top-domains"
    "sensitive-bigrams"
    "sensitive-trigrams")
   (LaTeX-add-bibliographies
    "IEEEabrv"
    "censor"
    "ml"))
 :latex)

