file="control.txt"
if [ -f  $file ]; then
  rm $file
fi

echo -e "DUMP" >> $file
COUNTER=1030
COUNTER2=1031
for i in `seq 1 1000`;
do
  echo -e "ip3x..$i 1 $COUNTER 2 dump_x" >> $file
  #COUNTER=$[$COUNTER +1]
done  
for i in `seq 1 1000`;
do
  echo -e "ip3y..$i 1 $COUNTER2 2 dump_y" >> $file
  #COUNTER=$[$COUNTER +1]
done  
echo -e "NEXT">> $file
echo -e "ZIPF">> $file
echo -e "dump_x">> $file
echo -e "dump_y">> $file
echo -e "NEXT">> $file

