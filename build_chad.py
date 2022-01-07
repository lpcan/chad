#!/usr/bin/python
# Build CHAD database using RACS as base
# L. Canepa, adapted from V.A. Moss

__author__= "L. Canepa"
__version__ = 0.2

from argparse import ArgumentParser, RawTextHelpFormatter
import time
from modules import crossmatch, addsurveys
from modules.functions import *

def main():
    
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    
    parser.add_argument("-r", "--rebuild",
            default = False,
            action = "store_true",
            help = "Specify whether to delete and rebuild CHAD database (default %(default)s)")
            
    parser.add_argument("-c", "--crossmatch",
    		default = False,
    		action = "store_true",
    		help = "Specify whether to re-perform crossmatch of surveys (default %(default)s")
            
    parser.add_argument("-a", "--addsurveys",
    		default = False,
    		action = "store_true",
    		help = "Specify whether to add new surveys to CHAD (default %(default)s)")
            
    args = parser.parse_args()
    
    # Download parameters from sheet
    param_sheet_id = "1-ePYYFph6GHohn5KKZi24rw_vAdcMltg0lRu8FfSaPg"
    download_csv(param_sheet_id)
    
    # Check arguments
    if args.rebuild == True:
    	print("Rebuilding CHAD...")
    	rebuild()
    	
   	if args.crossmatch == True:
   		print("Crossmatching surveys...")
    	
    if args.addsurveys == True:
    	print("Importing surveys into CHAD...")

if __name__ == "__main__":
    main()
    
    

