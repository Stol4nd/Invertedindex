rm -rf d1

python3 ./searcher.py --root d1 init
cat d1/.searcher ; echo
python3 ./searcher.py --root d1 init  --drop-existing
cat d1/.searcher ; echo
ls d1
ls d1/files
cat d1/files/.splits
