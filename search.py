#!/usr/bin/env python3
# TC chair Python tools. Andreas Reinhardt, 2021

import csv, re
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Locate TCCC member details in OU Analytics data')
    parser.add_argument('-a', '--all', help='show more user details', dest='complete', action='store_true')
    parser.add_argument('oufile', type=argparse.FileType('r', encoding='UTF-16'), help='the CSV file exported from OU Analytics')
    parser.add_argument('query', type=str)
    args = parser.parse_args()

    print("-"*60)
    print("Searching TCCC membership database for '{}'".format(args.query))
    print("-"*60)


    searchfields = ["First Name" , "Middle Name", "Last Name", "Email Address", "Member/Customer Number"] # where to search
    headers = [h.strip() for h in next(args.oufile, None).split("\t")]

    printfields = ["First Name", "Last Name", "Email Address", "Member/Customer Number", "Asset End Date"] # what to print
    if args.complete is not None and args.complete is True:
        printfields = [
	        "Name Prefix", "First Name", "Middle Name", "Last Name", "Name Suffix", "Gender", 
    	    "Member/Customer Number", "Email Address",
        	"IEEE Status", "Asset Status", "Grade", "Grade History", 
	        "Renew Year", "Renewal Category", "Initial Join Date", "Join Date", 
    	    "Asset Start Date", "Asset End Date", "Cancel Date", 
			"Years of Service", 
	        "Active Society List", "Technical Community List", "Technical Council List", 
    	    "OK to contact"
#             "Company/Attention", "Address 1", "Address 2", "Address 3", "City", "State/Province", "Postal Code", "Country", "Work Number", "Home Number", 
# 				"Product Name", "Product Type", "Product Code", 
# 				"Asset Paid Date", 
#				"Region", "Section", "Subsection",       
#               "YP Eligible Y/N", 
# "HKN Code", "HKN Name", "HKN Induction Date",  
        ]
          

    for line in csv.reader(args.oufile, delimiter='\t'):
        printme = False
        for f in searchfields:
            value = line[headers.index(f)].strip()
            if args.query.casefold() in value.casefold():
                printme = True
        if printme:
            for f in printfields:
                value = line[headers.index(f)].strip()

                if f == "Technical Community List":
                    value = value.replace("CMYCC705", "TCCC")
                if f == "Active Society List":
                    value = value.replace("MEMC016", "Computer Society")
                    
                if value != "":
                    print("{:>24s} : {}".format(f, value))
            print("-"*60)

    args.oufile.close()
