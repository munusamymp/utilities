#!/bin/bash
echo "This script requires bash 4+"

coproc GREP { grep --line-buffered "error"; }

# Write log lines
echo "info: started" >&"${GREP[1]}"
echo "error: something broke" >&"${GREP[1]}"
echo "error: another issue" >&"${GREP[1]}"
echo "done" >&"${GREP[1]}"

# Read and print only lines containing "error"
while read -r line <&"${GREP[0]}"; do
    echo "GREP matched: $line"
done

