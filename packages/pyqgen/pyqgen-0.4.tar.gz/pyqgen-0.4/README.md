# PyQGen

- Author: Giuseppe Lipari
- Email : giuseppe.lipari@univ-lille.fr

PyQGen is a command line script to generate a randomized list of
questions taken from a orgmode file. It can be used to prepare exams
for large classes. 

What you need in addition to PyQGen : 
- Emacs with org-mode;
- A LaTeX environment.

## Overview 

The original list of questions must be redacted according to the
[org-mode](https://orgmode.org/) format. The first level heading in
this file represent *groups of questions*; the second level headings
represent the questions ; deeper level headings represent solutions. 

An example of database of questions is available [here](examples/basic/db.org).

PyQGen produces an org-mode file which contains the exams. This can
later be transformed into a PDF file via LaTeX.

PyGen also produces an excel sheet for correction and grading. 

## Installing 

I recommend installing PyQGen using a virtual environnement and pip. 
For example : 
```sh
virtualenv pyqgenenv
source ./pyqgenenv/bin/activate
pip install pyqgen
```

PyQGen depends on
- [orgparse](https://orgparse.readthedocs.io/en/latest/) to parse the
org-mode file, 
- [openpyxl](https://openpyxl.readthedocs.io/en/stable/) to produce the excel file for grading.

Pip automatically takes care of the dependencies.

## Command line options 

The command is : 
```sh
pyqgen output [OPTIONS] 
```

where `output` the generated file that contains the exams. The
following options are possible :

- `-h`, `--help`  shows the help message
- `-d DB`, `--db DB` specifies an input file. By default, this is
  equal to file `db.org`.
- `-t TITLE`, `--title TITLE` Specifies the title of each exam sheet
  (default: "Examen")
- `-i IFILE`, `--ifile IFILE` Text file containing the instructions to be 
  printed on each exam (default: none)
- `-n NCOPIES`, `--ncopies NCOPIES` Number of exams to generate (default: 1)
- `-g [NG ...]`, `--ng [NG ...]` Number of questions per group
  (default: [1, 1, 1]). Therefore, the default assumes that the input
  file defines 3 question groupes, and for each exam it will randomly
  select one question per group.  Make sure that you specify at least
  one number per each group (see example below).
- `-e HEADER`, `--header HEADER` Org-mode file header. This is used to
  personnalize the output style. Typically, you can specify the size
  of the sheet (using the latex package geometry), the font, the font
  size, etc.


## Examples

Go in directory `examples/basic`. The database of questions is in file
`db.org`. Please open the file to familiarize with the way it is
structured. In this example, there are 3 question groups (first
heading) each one containing questions, exercises and solutions. 

Solutions are third level heading tagged with the `:solution:` tag. 

For each question, we can optionally specify three properties: 
- `CATEGORY` is a comma-separated list of categories, each one
  represents a set of questions. The program never generates
  questionnaires with two questions belonging the same category. This
  can be useful to avoid having two similar questions in the same
  exam.
  
- `NUM_RESP` and `NUM_CORRECT` are used for feedback: the first one is
  the number of time the question has been answered in a
  questionnaire; the second one is the number of correct answers to
  this question. The rate `NUM_CORRECT/NUM_RESP` represents an
  indication of how easy is the question. THIS IS AN EXPERIMENTAL
  FEATURE, not yet fully implemented.

To compile the database file into a pdf, run 

```
./compile.sh db.org
```

To generate the questionnaire, you can run one of the following commands : 

- `pyqgen out.org -n 30` 

  This generates two files: `out.org` contains 30 copies of the
  questionnaire, and `out.xls` contains the grading sheet.  
  To compile the questionnaire into a PDF file, run `compile.sh
  out.org`. Every instance of the questionnaire contains 3 questions,
  one per question group.
  
- `pyqgen out.org -n 30 --ng 2 1 1`

  This command generates questionnaires consisting of 4 questions
  each: 2 taken from the first group, 1 from the second group, and 1
  from the third group.
    
After generating the questionnaire, you can run 
```
./compile.sh
``` 
to get the `out.pdf` file in output. 


	
