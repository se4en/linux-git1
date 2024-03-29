#!/usr/bin/env bash

awk -F, '
{
	if ($18 > 0) {
		sum += $18;
		cnt++;
	}
}
END {
	print "RATING_AVG", sum/cnt
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
	if (($2 ~ /holiday inn/) && ($12 > 0))
	{
		val_hinn[tolower($7)] += $12;
		cnt_hinn[tolower($7)]++;
	} else if (($2 ~ /hilton/) && ($12 > 0))
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
set ylabel 'Rating';
set xlabel 'Cleanliness';
f(x) = a*x + b;
fit f(x) '$1' using ((column(12) > 0)?column(12):1/0):((column(18) > 0)?column(18):1/0) via a,b;
plot f(x), '$1' using ((column(12) > 0)?column(12):1/0):((column(18) > 0)?column(18):1/0) ls 7 ps 0.5;"
