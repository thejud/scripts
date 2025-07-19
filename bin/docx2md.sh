#!/bin/bash

# docx2md.sh - Convert Microsoft Word .docx files to Markdown format
#
# Usage:
#   ./docx2md.sh <file.docx>
#
# Description:
#   This script converts a Microsoft Word document (.docx) to Markdown (.md)
#   format using pandoc. The output file will have the same name as the input
#   file but with a .md extension.
#
# Requirements:
#   - pandoc must be installed (https://pandoc.org/installing.html)
#
# Examples:
#   ./docx2md.sh report.docx      # Creates report.md
#   ./docx2md.sh ~/docs/memo.docx # Creates ~/docs/memo.md
#
# Exit codes:
#   0 - Success
#   1 - Error (missing pandoc, file not found, wrong extension, etc.)

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc is not installed. Please install it first."
    exit 1
fi

# Check if a file argument was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <file.docx>"
    exit 1
fi

# Get the input file
input_file="$1"

# Check if the file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found."
    exit 1
fi

# Check if the file has .docx extension
if [[ ! "$input_file" =~ \.docx$ ]]; then
    echo "Error: File must have .docx extension."
    exit 1
fi

# Create output filename by replacing .docx with .md
output_file="${input_file%.docx}.md"

# Convert the file
echo "Converting '$input_file' to '$output_file'..."
pandoc -f docx -t markdown -o "$output_file" "$input_file"

# Check if conversion was successful
if [ $? -eq 0 ]; then
    echo "Successfully converted to '$output_file'"
else
    echo "Error: Conversion failed."
    exit 1
fi