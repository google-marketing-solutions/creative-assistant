for question in \
  'Categorize the following keywords: "one" "two" "ferret" "weight loss"' \
  'What are the top 4 search trends?' \
  'What are the top 4 youtube trends?' ;
do
  echo "$question"
  creative-assistant "$question" \
    --llm gemini --llm.model='gemini-1.5-flash'
  echo "-----------------------------"
  echo
done
