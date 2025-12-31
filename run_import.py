#!/usr/bin/env python3
"""
Master import script
Runs all import operations in the correct order:
1. Add missing specialties
2. Import doctors from CSV
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from add_missing_specialties import add_all_specialties
from import_doctors_csv import import_doctors_from_csv

def main():
    """Run all import operations"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "RANKSEWA - BULK IMPORT" + " " * 26 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")

    # Step 1: Add missing specialties
    print("STEP 1: Adding missing specialties...")
    print("-" * 70)
    add_all_specialties()

    print("\n")

    # Step 2: Import doctors
    print("STEP 2: Importing doctors from CSV...")
    print("-" * 70)
    csv_file = 'doctors_combined.csv'

    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' not found!")
        print(f"   Make sure the file is in the current directory:")
        print(f"   {os.getcwd()}")
        return

    import_doctors_from_csv(csv_file)

    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 25 + "IMPORT COMPLETE" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")

if __name__ == '__main__':
    main()
