set PATH=%PATH%;C:\Python32

python parse.py src.txt rank.txt list.txt
python dl.py list.txt > log.txt
