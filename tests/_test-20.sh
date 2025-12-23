rm -rf d1

python3 ./searcher.py --root d1 init
python3 ./searcher.py --root d1 add not-existing-file.txt

