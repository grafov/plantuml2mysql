#!/usr/bin/env python3
#-*-coding:utf-8-*-
# Usage: ./plantuml2mysql <dbsource.plu> <dbname>
# Author: Alexander I.Grafov <grafov@gmail.com>
# See https://github.com/grafov/plantuml2mysql
# The code is public domain.

CHARSET="utf8_unicode_ci"

import sys
import re
import time

# PlantUML allows some HTML tags in comments.
# We don't want them anymore here...
TAG_RE = re.compile(r'<[^>]+>')
def strip_html_tags(t):
    return TAG_RE.sub('', t)

# A minimal help
def print_usage():
  print("Convert PlantUML classes schema into mySQL database creation script")
  print("Usage:\n", sys.argv[0], "<dbsource.plu> <dbname>")
  print("\nSee https://github.com/grafov/plantuml2mysql for details\n")

def main():
    # Check arguments (exactly 1 + 2):
    if len(sys.argv) != 3:
        print_usage()
        sys.exit()
    try: # Avoid exception on STDOUT
        with open(sys.argv[1]) as src:
            data = src.readlines()
    except:
        print("Cannot open file: '" + sys.argv[1] + "'")
        sys.exit()
    # Add information for future self ;-)
    print("# Database created on", time.strftime('%d/%m/%y %H:%M',time.localtime()), "from", sys.argv[1])
    print("CREATE DATABASE %s CHARACTER SET = utf8 COLLATE = %s;" % (sys.argv[2], CHARSET))
    print("USE %s;\n" % sys.argv[2])
    uml = False; table = False; field = False
    pk = False; idx = False
    primary = []; index = ""
    for l in data:
        l = l.strip()
        if not l:
            continue
        if l == "@startuml":
            uml = True
            continue
        if not uml:
            continue
        if l == "--": # Separator
            continue
        comment = ""
        i = l.split()
        fname = i[0]
        if fname == ".." or fname == "__": # Separators in table definition
            continue
        if field and ("--" in l):
            i, comment = l.split("--", 2)
            i = i.split()
        pk = False; idx = False
        if fname[0] in ("+", "#"):
            if fname[0] == "#":
                pk = True
            else:
                idx = True
            fname = fname[1:]
        if l == "@enduml":
            uml = False
            continue
        if not uml:
             continue
        if l.startswith("class"):
            table = True; field = False
            primary = []; index = ""
            # Table names are quoted and lower cased to avoid conflict with a mySQL reserved word
            print("CREATE TABLE IF NOT EXISTS `" + i[1].lower() + "` (")
            continue
        if table and not field and l == "==": # Seperator after table description
            field = True
            continue
        if field and l == "}":
            table = False; field = False
            print("  PRIMARY KEY (%s)" % ", ".join(primary), end="")
            if index:
                print(",\n%s" % index[:-2],)
                index = ""
            print(");\n")
            continue
        if field and l == "#id":
            print("  %-16s SERIAL," % "id")
        if field and l != "#id":
            print("  %-16s %s" % (fname, " ".join(i[2:]).upper()), end="")
            if comment:
                # Avoid conflict with apostrophes (use double quotation marks)
                print(" COMMENT \"%s\"" % strip_html_tags(comment.strip()), end="")
            print(",")
        if field and pk:
            primary.append(fname)
        if field and idx:
            index += "  INDEX (%s),\n" % fname


if __name__ == "__main__":
    main()
