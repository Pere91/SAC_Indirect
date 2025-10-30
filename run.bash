# UNCOMMENT YOUR SYSTEM'S VERSION

### WINDOWS ###
cmd.exe /c start cmd.exe /k "echo board && docker exec -it board sh"
cmd.exe /c start cmd.exe /k "echo player1 && docker exec -it player1 sh"
cmd.exe /c start cmd.exe /k "echo player2 && docker exec -it player2 sh"

### macOS ###
# osascript -e 'tell application "Terminal" to do script "echo board && docker exec -it board sh"'
# osascript -e 'tell application "Terminal" to do script "echo player1 && docker exec -it player1 sh"'
# osascript -e 'tell application "Terminal" to do script "echo player2 && docker exec -it player2 sh"'

### LINUX ###
# gnome-terminal -- bash -c "echo board && docker exec -it board sh"
# gnome-terminal -- bash -c "echo player1 && docker exec -it player1 sh"
# gnome-terminal -- bash -c "echo player2 && docker exec -it player2 sh"

