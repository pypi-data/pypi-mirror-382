(require 'org)

(setq org-export-backends (quote (ascii latex)))         

(setq org-latex-pdf-process (list "latexmk -pdf %f"))

(add-to-list 'org-latex-packages-alist '("" "listings"))
(setq org-latex-listings 'listings)

(defun update-all-dblocks-before-exporting (arg)
  (org-update-all-dblocks ))

(org-babel-do-load-languages
 'org-babel-load-languages
 '((C . t)))
