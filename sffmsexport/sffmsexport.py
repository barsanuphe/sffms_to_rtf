import argparse
import sys
import re
from pathlib import Path


class Project(object):
    def __init__(self, path):
        self.path = path
        self.output_path = path.with_suffix(".rtf")
        self.lines = []
        self.author = ""
        self.address = ""
        self.disposable = False
        self.author_name = ""
        self.surname = ""
        self.running_title = ""
        self.title = ""
        self.wordcount = ""
        self.document = []

    def manage_includes(self, start_lines):
        complete_lines = []
        for line in start_lines:
            matches = re.match(r'(\\include|\\input){(?P<filename>.*?)}', line)
            if matches:
                sub_path = Path(matches.groupdict()["filename"])
                # TODO add .tex if necessary
                # check if absolute and deal with relative
                if not sub_path.is_absolute():
                    sub_path = Path(self.path.parent, sub_path)
                assert sub_path.exists()
                # add lines
                with sub_path.open() as s:
                    complete_lines.extend(s.readlines())
            else:
                complete_lines.append(line)
        return complete_lines

    def read_all_lines(self):
        # open main file
        with self.path.open() as f:
            self.lines = f.readlines()

        # look for \input / \include
        start_lines = []
        complete_lines = self.lines
        compt = 0
        while complete_lines != start_lines and compt < 10:
            start_lines = complete_lines
            complete_lines = self.manage_includes(start_lines)
            compt += 1

        if compt == 10:
            raise Exception("More than 10 levels of inclusions, probably circular.")
        else:
            self.lines = complete_lines

    def clean_all_lines(self):
        for (i, line) in enumerate(self.lines):
            self.lines[i] = line.strip()
            # TODO clean everything

    def extract_parts(self):
        start_document = 0
        end_document = 0
        expr = re.compile(r'(\\runningtitle){(?P<running_title>.*?)}|'
                          r'(\\title){(?P<title>.*?)}|'
                          r'(\\author){(?P<author>.*?)}|'
                          r'(\\authorname){(?P<author_name>.*?)}|'
                          r'(\\surname){(?P<surname>.*?)}|'
                          r'(\\address){(?P<address>.*?)}|'
                          r'(\\wordcount){(?P<wordcount>.*?)}|'
                          )
        for (i, line) in enumerate(self.lines):
            # extract metadata
            matches = re.match(expr, line)
            if matches:
                results = matches.groupdict()
                if results["title"]:
                    self.title = results["title"]
                if results["running_title"]:
                    self.running_title = results["running_title"]
                if results["author"]:
                    self.author = results["author"]
                if results["author_name"]:
                    self.author_name = results["author_name"]
                if results["surname"]:
                    self.surname = results["surname"]
                if results["address"]:
                    self.address = results["address"]
                if results["wordcount"]:
                    self.wordcount = results["wordcount"]
            # isolate document lines
            if re.search(r'\\begin\{document\}', line):
                start_document = i + 1
            if re.search(r'\\end\{document\}', line):
                end_document = i - 1

        if self.running_title == "":
            self.running_title = self.title
        if self.author_name == "":
            self.author_name = self.author
        if self.surname == "":
            self.surname = self.author
        self.document = self.lines[start_document:end_document]

    def join_paragraphs(self):
        # replace empty lines with \n for easier splitting later
        self.document = [x if x != "" else "\n" for x in self.document]
        # joining all lines and splitting the paragraphs
        self.document = " ".join(self.document).split("\n")
        # cleanup paragraphs
        self.document = [el.strip() for el in self.document if el != ""]

    def generate_output(self):
        # make rtf
        rtf = RTF(self.output_path)
        rtf.add_file_header()
        rtf.add_metadata_header(self.author, self.author_name, self.surname, self.address,
                                self.title, self.running_title, self.wordcount)
        rtf.add_document(self.document)
        rtf.write()

    def __str__(self):
        return "\n".join([self.author, self.address, str(self.disposable), self.author_name, self.surname,
                          self.running_title, self.title, self.wordcount, "\n".join(self.document)])


class RTF(object):
    def __init__(self, filename):
        self.filename = filename
        self.lines = []

    def add_file_header(self):
        self.lines = ["{\\rtf1\\ansi\\deff1\\ansicpg10000\n",
                      "{\\fonttbl\\f0\\fmodern\\fcharset77 Courier;\\f1\\froman\\fcharset77 Times New Roman;}\n",
                      "{\\colortbl;\\red255\\green255\\blue255;\\red255\\green0\\blue0;}\n",
                      "\\margl1440\\margr1440\\vieww12240\\viewh15840\\viewkind1\\viewscale100\\titlepg\n"]

    def add_metadata_header(self, author, author_name, surname, address, title, running_title, wordcount="100"):
        self.lines.extend([
            "{\\info\n",
            "{\\title %s}\n" % title,
            "{\\doccomm Generated from latex! }",
            "{\\author %s}}" % author,
            "{\\headerf}\n",
            "{\\header\\pard\\qr\\f0{" + surname + " / " + running_title.upper() + " / " + "{\\field{\\*\\fldinst PAGE }}}\\par}\n",
            "{\\i0\\scaps0\\b0\n",
            "\\deftab360\n",
            "\\pard\\tx7500\\pardeftab360\\ql\\qnatural\n",
            "\\f0\\fs24 \\cf0\n",
            author_name,
            "\\tab " + wordcount + " words",
            "\\line\n",
            address + "\\par\n",
            "\\pard\\pardeftab720\\ql\\qnatural\\sb4000\\par\n",
            "\\pard\\sl510 \\qc\\f0\\fs24\n",
            title.upper() + "\\\n",
            "by " + author + "\\par\n",
            "\\pard\\sl510\\f0\\fs24\n",
            "\\cf0 \\\n"
        ])

    def add_document(self, document_lines):
        for line in document_lines:
            # TODO \chapter \chapter{xx}, \part{xx}
            # => '\\pard\\sl510\\qc\\cf0 {\\b <TITRE> } \\par\n'
            if re.search(r'\\scenebreak|\\newscene', line):
                self.lines.append('\\pard\\sl510\\qc\\cf0 # \\par\n')
            else:
                self.lines.append('\\pard\\sl510\\f0\\fs24\\cf0 ' + line + '\\par\n')
        self.lines.append('\\pard\\par\\pard\\sl510 \\qc\\f0\\fs24 # # # # #\\par')
        self.lines.append('}}\n')

    def write(self):
        with self.filename.open("w") as f:
            f.writelines(self.lines)


def main():
    parser = argparse.ArgumentParser(description='sffmsexport.')
    parser.add_argument('-i',
                        '--input',
                        dest='input',
                        action='store',
                        nargs=1,
                        metavar="FILE",
                        help='Main tex file.')

    parser.add_argument('-o',
                        '--output',
                        dest='output',
                        action='store',
                        nargs=1,
                        metavar="OUTPUT",
                        help='Output file, if necessary.')

    args = parser.parse_args()

    try:
        input_file = Path(args.input[0])
        assert input_file.exists()
    except Exception as err:
        print("Incorrect input!")
        sys.exit(-1)

    # TODO deal with outputfile

    p = Project(input_file)
    p.read_all_lines()
    p.clean_all_lines()
    p.extract_parts()
    p.join_paragraphs()
    p.generate_output()

if __name__ == "__main__":
    main()
