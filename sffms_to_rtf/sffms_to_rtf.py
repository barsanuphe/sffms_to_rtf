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

    def insert_included(self, start_lines):
        complete_lines = []
        for line in start_lines:
            matches = re.match(r'(\\include|\\input){(?P<filename>.*?)}', line)
            if matches:
                sub_path = Path(matches.groupdict()["filename"])
                # add .tex if necessary
                if sub_path.suffix == "":
                    sub_path = sub_path.with_suffix(".tex")
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
        # loop in case included files include other files
        while complete_lines != start_lines and compt < 10:
            start_lines = complete_lines
            complete_lines = self.insert_included(start_lines)
            compt += 1

        if compt == 10:
            raise Exception("More than 10 levels of inclusions, stopping.")
        else:
            self.lines = complete_lines

        # parse and join multiline tags
        joined_lines = []
        join_next_line = False
        for line in self.lines:
            newline = line.strip()
            if join_next_line:
                join_next_line = False
                joined_lines[-1] += "\n" + newline
            else:
                joined_lines.append(newline)

            if newline.endswith(r"\\"):
                join_next_line = True
                joined_lines[-1] = joined_lines[-1][:-2]

        self.lines = joined_lines

    def extract_parts(self):
        start_document = 0
        end_document = 0
        expr = re.compile(r'(\\runningtitle){(?P<running_title>.*?)}|'
                          r'(\\title){(?P<title>.*?)}|'
                          r'(\\author){(?P<author>.*?)}|'
                          r'(\\authorname){(?P<author_name>.*?)}|'
                          r'(\\surname){(?P<surname>.*?)}|'
                          r'(\\address){(?P<address>.*?)}|'
                          r'(\\wordcount){(?P<wordcount>.*?)}',
                          re.DOTALL
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
        rtf = RtfFile(self.output_path)
        rtf.add_file_header()
        rtf.add_metadata_header(self.author, self.author_name, self.surname,
                                self.address, self.title, self.running_title,
                                self.wordcount)
        rtf.add_document(self.document)
        rtf.write()

    def __str__(self):
        return "\n".join([self.author, self.address, str(self.disposable),
                          self.author_name, self.surname,
                          self.running_title, self.title, self.wordcount,
                          "\n".join(self.document)])


class Rtf(object):
    CENTER = "\\qc "
    PAGE_BREAK = "\\page "
    LINE_BREAK = "\\line "
    START_PAR = "\\pard "
    INDENT = "\\fi720 "
    END_PAR = "\\par "
    DOUBLE_SPACE = "\\sl480\\slmult1 "
    SIZE_12 = "\\f0\\fs24 "
    HALF_PAGE_VERTICAL_SPACE = "\\sb3600"
    BOLD = '{\\b %s }'

    P_CENTER = START_PAR + DOUBLE_SPACE + CENTER + SIZE_12 + "%s" + END_PAR
    P_CENTER_B = P_CENTER % BOLD
    P_INDENT = START_PAR + INDENT + DOUBLE_SPACE + SIZE_12 + "%s" + END_PAR
    P = START_PAR + DOUBLE_SPACE + SIZE_12 + "%s" + END_PAR
    P_SINGLE = START_PAR + SIZE_12 + "%s" + END_PAR
    BLANK = P % ""

    HEADER = "{\\rtf1\\ansi\\deff1\\ansicpg10000{\\fonttbl\\f0\\fmodern" \
             "\\fcharset77 Courier;\\f1\\froman\\fcharset77 Times New Roman;}" \
             "\\margl1440\\margr1440\\vieww12240\\viewh15840\\viewkind1" \
             "\\viewscale100\\titlepg"


class RtfFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.lines = []

    def add_file_header(self):
        self.lines.append(Rtf.HEADER)

    def add_metadata_header(self, author, author_name, surname, address, title,
                            running_title, wordcount="100"):
        self.lines.extend([
            "{\\info",
            "{\\title %s}" % title,
            "{\\doccomm Generated from latex! }",
            "{\\author %s}}" % author,
            "{\\headerf}",
            "{\\header" + Rtf.P_SINGLE % ("\\qr\\f0{" + surname + " / " +
                                          running_title.upper() +
                                          " / {\\field{\\*\\fldinst PAGE }}}") +
            "}",
            "{\\i0\\scaps0\\b0",
            Rtf.P_SINGLE % ("\\tqr\\tx10000" + author_name +
                            "\\tab " + wordcount + " words"),
            Rtf.LINE_BREAK,
            Rtf.P_SINGLE % (address.replace("\n", Rtf.LINE_BREAK)),
            Rtf.P % Rtf.HALF_PAGE_VERTICAL_SPACE,
            Rtf.P_CENTER % title.upper(),
            Rtf.P_CENTER % ("by " + author),
            Rtf.BLANK,
            Rtf.BLANK,
        ])

    def add_document(self, document_lines):
        expr = re.compile(r'(\\chapter){(?P<numbered_chapter>.*?)}|'
                          r'(\\chapter\*){(?P<chapter>.*?)}')
        chapter_number = 1
        # generating rtf lines
        for line in document_lines:
            matches = re.match(expr, line)
            if matches:
                # new chapter
                if matches.groupdict()["chapter"]:
                    self.lines.append(Rtf.P_CENTER_B % matches.groupdict()["chapter"])
                if matches.groupdict()["numbered_chapter"]:
                    self.lines.append(Rtf.P_CENTER_B % ('Chapter %s' % chapter_number))
                    self.lines.append(Rtf.P_CENTER_B % matches.groupdict()["numbered_chapter"])
                    chapter_number += 1
            elif re.search(r'\\scenebreak|\\newscene', line):
                # scene separation
                self.lines.append(Rtf.P_CENTER % "#")
            else:
                # normal paragraphes
                line = line.replace(r"\emph{", '{\\ul ')
                line = line.replace(r"\thought{", '{\\ul ')
                self.lines.append(Rtf.P_INDENT % line)
        self.lines.append(Rtf.P_CENTER % "# # # # #")
        self.lines.append('}}')

    def write(self):
        with self.filename.open("w") as f:
            f.writelines(self.lines)


def main():
    parser = argparse.ArgumentParser(description='sffms_to_rtf.')
    parser.add_argument('-i',
                        '--input',
                        dest='input',
                        action='store',
                        nargs=1,
                        metavar="FILE",
                        help='Main tex file.')
    args = parser.parse_args()

    try:
        input_file = Path(args.input[0])
        assert input_file.exists()
    except Exception as err:
        print("Incorrect input!")
        sys.exit(-1)

    p = Project(input_file)
    p.read_all_lines()
    p.extract_parts()
    p.join_paragraphs()
    p.generate_output()


if __name__ == "__main__":
    main()
