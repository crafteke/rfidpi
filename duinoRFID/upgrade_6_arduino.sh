#!/bin/sh
make compile

for index in 0 1 2 3 4 5
do
  # cp ./duinoRFID.ino ./duinoRFID.ino.COPY
  # sed -i "s/04242/$index/g" duinoRFID.ino
  # make compile
  # cp ./duinoRFID.ino.COPY duinoRFID.ino
  # rm ./duinoRFID.ino.COPY
  make upload PORT="/dev/ttyUSB$index"

done
