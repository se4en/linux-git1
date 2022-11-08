[greetings.py](greetings.py)

## Описание решения проекта

В проекте использовался предложенный набор данных `hotels.csv`, содержащий общую информацию и оценки некоторых характеристик для различных отелей в нескольких странах.

Весь код решения содержится в файле [process.sh](process.sh) и разделен на 4 логические части в соответствии с подзадачами:

1. Вычисление среднего рейтинга среди всех отелей. Для вычисления результата использовались значения последнего столбца файла `hotels.csv`, за исключением невалидных значений.

```awk -F, '
{
	if ($18 > 0) {
		sum += $18;
		cnt++;
	}
}
END {
	print "RATING_AVG", sum/cnt
}' $1;
```

2. Вычисление числа отелей в каждой стране. Для получения названия страны использовался 7-ой столбец файла `hotels.csv`.

```
awk -F, '
{
	cnt[tolower($7)]++
}
END {
	for (country in cnt) print "HOTELNUMBER", country, cnt[country]
}' $1;
```

3. Вычисление среднего балла оценки чистоты по стране. Для получения значения оценки чистоты использовался 12-ый столбец файла `hotels.csv`.

```
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
```

4. Рассчет коэффициентов линейной регрессии для оценки зависимости чистоты от общей оценки и отрисовка результата на графике.

```
gnuplot -e "
set datafile separator ',';
set terminal png size 1000,1000;
set output 'plot.png';
f(x) = a*x + b;
fit f(x) '$1' using ((column(12) > 0)?column(12):1/0):((column(18) > 0)?column(18):1/0) via a,b;
plot f(x), '$1' using ((column(12) > 0)?column(12):1/0):((column(18) > 0)?column(18):1/0) ls 7 ps 0.5;"
```
