#!/usr/bin/env bash
set -euo pipefail

rm -f *.csv super.pptx;

PYTHON="/opt/homebrew/opt/python@3.12/bin/python3.12"
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

SORT_COLUMN=7

echo "Indexing PPTX files into CSVs..."
shopt -s nullglob
csvs=()
for deck in *.pptx; do
	if [ ! -f "$deck" ]; then
		continue
	fi
	echo "Indexing $deck"
	"$PYTHON" index_slide_deck.py -i "$deck"
	csvs+=("${deck%.pptx}.csv")
done

if [ "${#csvs[@]}" -eq 0 ]; then
	echo "No PPTX files found to index."
	exit 1
fi

echo "Merging CSVs into merged.csv"
rm -f merged.csv
header="$(head -n 1 "${csvs[0]}")"
echo "Sorting by column $SORT_COLUMN"
{
	echo "$header"
	for csv_path in "${csvs[@]}"; do
		tail -n +2 "$csv_path"
	done | grep -v "^[[:space:]]*$" | sort -t, -k"${SORT_COLUMN},${SORT_COLUMN}"
} > merged.csv

master_col="$(printf '%s\n' "$header" | awk -F, '{for (i=1;i<=NF;i++) if ($i=="master_name") {print i; exit}}')"
if [ -z "$master_col" ]; then
	echo "master_name column not found in CSV header."
	exit 1
fi

master_name="${MASTER_NAME:-}"
if [ -z "$master_name" ]; then
	echo "Normalizing master_name to the first data row value."
else
	echo "Normalizing master_name to ${master_name}."
fi
awk -F, -v OFS="," -v col="$master_col" -v master="$master_name" '
	NR==1 { print; next }
	{
		if (master == "") {
			master = $col
		}
		$col = master
		print
	}
' merged.csv > merged.csv.tmp

cat merged.csv.tmp | grep -v 'image,,,' > merged.csv

echo "Rebuilding super.pptx from merged.csv"
"$PYTHON" rebuild_slides.py -i merged.csv -o super.pptx
echo "Done."
