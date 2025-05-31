[[ -x "/usr/bin/git" ]] && loop() || echo "Git not installed"

loop() {
    while true
    do
        sleep 1 && git pull
    done
}