rm -rf d1

python3 ./searcher.py --root d1 init
python3 ./searcher.py --root d1 add testdata/file1.txt
echo index:
ls d1/index
cat d1/index/*

