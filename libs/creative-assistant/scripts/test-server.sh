interact() {
  local question="$1"
	http POST localhost:8000 \
    data[question]="$question"
}

interact "$1"
