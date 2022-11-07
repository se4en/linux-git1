#!/usr/bin/env bash

awk -F, '
{
	if ($18 > 0)
		 sum += $18;
}
END {
	print "RATING_AVG", sum/NR
}' $1;

awk -F, '
{
	cnt[tolower($7)]++
}
END {
	for (country in cnt) print "HOTELNUMBER", country, cnt[country]
}' $1;

awk -F, '
{
	if (tolower(substr($2, 1, 11))  == "holiday inn")
	{
		# print($1);
		val_hinn[tolower($7)] += $12;
		cnt_hinn[tolower($7)]++;
	} else if (tolower(substr($2, 1, 6)) == "hilton")
	{
		val_hilton[tolower($7)] += $12;
		cnt_hilton[tolower($7)]++;
	}
}
END {
	for (country in val_hinn) print "CLEANLINESS" , country, val_hinn[country]/cnt_hinn[country], val_hilton[country]/cnt_hilton[country]
}
' $1;

gnuplot -e "
set datafile separator ',';
set terminal png size 1000,1000;
set output 'plot.png';
f(x) = a*x + b;
fit f(x) '$1' using 12:18 via a,b;
plot f(x)"
