#!/bin/bash
cd ..

trap "exit" INT

echo "############################################"
echo "##   JentuBot: interactive fiction game   ##"
echo "############################################"

while true
do
sudo /usr/local/bin/python3 main.py
echo "JentuBot is crashed!"
echo "Rebooting in:"
for i in {3..1}
do
echo "$i..."
done
echo "###########################################"
echo "#       JentuBot is restarting now        #"
echo "###########################################"
done