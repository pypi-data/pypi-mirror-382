#!/bin/bash

ORGFILE=$1

emacs -Q --batch -l emacs-conf.el $ORGFILE --eval "(org-latex-export-to-pdf)"

rm "${ORGFILE/%.org}.tex"
