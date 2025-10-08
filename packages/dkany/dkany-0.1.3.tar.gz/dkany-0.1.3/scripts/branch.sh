#!/bin/bash
echo "Positional Parameters"
ticket_number_desc=$1;
branch_name="features/macscore-${ticket_number_desc}";
echo 'ticket_number_desc = '$ticket_number_desc
echo 'branch_name = ' $branch_name

git checkout main
git pull
git checkout -b $branch_name
git push --set-upstream origin $branch_name
