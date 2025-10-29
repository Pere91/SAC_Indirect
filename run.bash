### WINDOWS ###
#docker compose up -d --build
cmd.exe /c start cmd.exe /k "echo board && docker exec -it board sh"
cmd.exe /c start cmd.exe /k "echo player1 && docker exec -it player1 sh"
cmd.exe /c start cmd.exe /k "echo player2 && docker exec -it player2 sh"

### macOS ###
# open -a Terminal .