#!/usr/bin/env python3
#-*-coding:utf-8-*-
# Usage: ./plantuml2mysql <dbsource.plu> <dbname>
# Author: Alexander I.Grafov <grafov@gmail.com>
# The code is public domain.

CHARSET="utf8_unicode_ci"

import sys

def main():
    print("CREATE DATABASE %s CHARACTER SET = utf8 COLLATE = %s;" % (sys.argv[2], CHARSET))
    print("USE %s;\n" % sys.argv[2])
    uml = False; table = False; field = False
    pk = False; idx = False
    primary = []; index = ""
    with open(sys.argv[1]) as src:
        data = src.readlines()
    for l in data:
        l = l.strip()
        if not l:
            continue
        if l == "@startuml":
            uml = True
            continue
        if not uml:
            continue
        if l == "--":
            continue        
        comment = ""
        i = l.split()
        fname = i[0]        
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
            print("CREATE TABLE IF NOT EXISTS", i[1], "(")
            continue
        if table and not field and l == "==":
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
                print(" COMMENT '%s'" % comment.strip(), end="")
            print(",")
        if field and pk:
            primary.append(fname)
        if field and idx:
            index += "  INDEX (%s),\n" % fname


if __name__ == "__main__":
    main()
