#!/usr/bin/env bash

#GITHUB_TOKEN=$( cat ".github_token")
GITHUB_TOKEN="FOOBUF"

result='[]'
i=1
cur_page=$( curl -H "Authorization: Bearer $GITHUB_TOKEN" "https://api.github.com/repos/datamove/linux-git2/pulls?state=all&per_page=100&page=$i")
cur_length=$(echo $cur_page | jq "length")

while [ $cur_length -gt 0 ]
do
	result=$(jq --slurp 'add' <(echo "$result") <(echo "$cur_page"))
	#result=$(jq -n --argjson a "$result" --argjson b "$cur_page" '$a + $b')
	#result=$(jq '$result + $cur_page')
	((i++))
	cur_page=$( curl -H "Authorization: Bearer $GITHUB_TOKEN" "https://api.github.com/repos/datamove/linux-git2/pulls?state=all&per_page=100&page=$i")
	cur_length=$(echo $cur_page | jq "length")
done

user_pulls=$(echo $result | jq "map(select(.user.login==\"$1\")) | sort_by(.created_at)")
user_length=$(echo $user_pulls | jq "length")
first_date=$(echo $user_pulls | jq ".[0] | .number")
first_merge=$(echo $user_pulls | jq ".[0] | .merged_at")

echo "PULLS $user_length"
echo "EARLIEST $first_date"
if [ "$first_merge" = "null" ]
then
	echo "MERGED 0"
else
	echo "MERGED 1"
fi

