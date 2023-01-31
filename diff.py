#!/usr/bin/env python3
# TC chair Python tools. Andreas Reinhardt, 2019

import csv, re
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate the diff between OU Analytics and ListServ members.')
    parser.add_argument('-i', '--ignore', type=argparse.FileType('r'), help='an (optional) file, listing email addresses (one per line) to ignore')
    parser.add_argument('-a', dest='added', default=False, action='store_true', help='prints the email addresses of members to add')
    parser.add_argument('-d', dest='deleted', default=False, action='store_true', help='prints the email addresses of members to delete')
    parser.add_argument('-u', dest='unchanged', default=False, action='store_true', help='prints the email addresses of unchanged members')
    parser.add_argument('-n', dest='noconsent', default=False, action='store_true', help='prints the email addresses of members without consent')
    parser.add_argument('oufile', type=argparse.FileType('r', encoding='UTF-16'), help='the CSV file exported from OU Analytics')
    parser.add_argument('lsfile', type=argparse.FileType('r'), help='the CSV file exported from ListServ')
    args = parser.parse_args()

    show = True
    if args.unchanged or args.deleted or args.added or args.noconsent:
        show = False

    if show:
        print("-"*60)

    # data structures from which to calculate the diff
    OUMAILS = []
    LSMAILS = []
    NAMES = {}
    NOCO = []
    IGNORE = []

    # Read addresses to ignore (if any)
    if args.ignore is not None:
        for line in args.ignore.readlines():
            addr = line.strip().split(' ')[0]
            if re.match(r"[^@]+@[^@]+\.[^@]+", addr):
                IGNORE.append(addr.lower())
        print("Ignoring {} manually unsubscribed email address(es)".format(len(IGNORE)))
        print("-"*60)

##########################################################################

    # Process OU analytics file
    if show:
        print("{:^60}".format("Analyzing OU Analytics Data"))
        print("-"*60)

    headers = [h.strip() for h in next(args.oufile, None).split("\t")]
    oFirst = headers.index("First Name")
    oMiddle = headers.index("Middle Name")
    oLast = headers.index("Last Name")
    oMail = headers.index("Email Address")
    oOkay = headers.index("OK to contact")
    badMail = 0
    noConsent = 0

    for line in csv.reader(args.oufile, delimiter='\t'):
        mail = line[oMail].strip().lower()
        name = line[oFirst].strip() + " " + ((line[oMiddle].strip() + " ") if line[oMiddle] != '' else "") + line[oLast].strip()
        contact = line[oOkay]

        if mail == '':
            if show:
                print("Skipping user {} with empty email address".format(name))
            badMail = badMail + 1
            continue
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
            if show:
                print("Skipping user {} with invalid email address '{}'".format(name, mail))
            badMail = badMail + 1
            continue

        if "Yes" in contact or "Y" in contact:
            OUMAILS.append(mail)
            NAMES[mail] = name
        else:
            noConsent = noConsent + 1
            if args.noconsent:
                if show:
                    print("No consent from {} ({})".format(name, mail))
                NOCO.append(mail)

    args.oufile.close()
    if show:
        print("Found {} members (+{} invalid email, +{} without consent)".format(len(OUMAILS), badMail, noConsent))
        print("-"*60)

##########################################################################

    # Process ListServ file
    if show:
        print("{:^60}".format("Analyzing ListServ Data"))
        print("-"*60)

    headers = [h.strip() for h in next(args.lsfile, None).split(',')]
    oName = headers.index("Name")
    oMail = headers.index("Email")
    for line in csv.reader(args.lsfile, delimiter=','):
        mail = line[oMail].strip().lower()
        name = line[oName].strip()

        if mail == '':
            #print("Skipping user {} with empty email address".format(name))
            continue
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
            #print("Skipping user {} with invalid email address '{}'".format(name, mail))
            continue

        LSMAILS.append(mail)
        if not "(No Name Available)" in name:
            NAMES[mail] = name
    args.lsfile.close()
    if show:
        print("Found {} addresses in the mailing list member dictionary".format(len(LSMAILS)))
        print("-"*60)
        print("{:^60}".format("Calculating the delta"))

##########################################################################

    # remove ignore mails
    OUMAILS = list(set(OUMAILS).difference(IGNORE))
    LSMAILS = list(set(LSMAILS).difference(IGNORE))

    inBoth = list(set(OUMAILS).intersection(LSMAILS))
    onlyOU = list(set(OUMAILS).difference(LSMAILS))
    onlyLS = list(set(LSMAILS).difference(OUMAILS))
    noCons = NOCO #list(set(LSMAILS).intersection(NOCO))

##########################################################################

    if show:
        print("-"*60)
        print("Found {} members to retain, +{} to add, -{} to remove".format(len(inBoth), len(onlyOU), len(onlyLS)))
        print("-"*60)

    if args.unchanged == True:
        print("="*60)
        print("No changes required to {} members:".format(len(inBoth)))
        print("="*60)
        for m in sorted(inBoth):
            print("{} ({})".format(m, NAMES[m]))

    if args.deleted == True:
        print("="*60)
        print("The following {} members must be deleted:".format(len(onlyLS)))
        print("="*60)
        for m in sorted(onlyLS):
            print("{}".format(m))

    if args.added == True:
        print("="*60)
        print("The following {} members must be added:".format(len(onlyOU)))
        print("="*60)
        for m in sorted(onlyOU):
            print("{}".format(m))
        print("="*60)

    if args.noconsent == True:
        print("="*60)
        print("The following {} ListServ members have not provided consent:".format(len(noCons)))
        print("="*60)
        for m in sorted(noCons):
            print("{}".format(m))
        print("="*60)
