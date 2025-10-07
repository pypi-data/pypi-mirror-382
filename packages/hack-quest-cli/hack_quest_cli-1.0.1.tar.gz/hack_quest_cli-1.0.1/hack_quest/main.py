from rich import print
from rich.console import Console
import time
import os
current_room = 'The HQ'
Coins = 0
vowel_var = ['a', 'e', 'i', 'o', 'u']
inventory = []
console = Console()
stolen_atm = False
hacked_camera = False
hacked_database = False
hacked_archive = False
hacked_office = False
hacked_value = 1
hacked_token = False
msg = ''
def hacking_screen(): ## Universal hack function
    global hacked_token, hacked_value
    if hacked_value == 1: ## Checks which hack it should deploy based on how many are already finished.
        console.print("[bold green]Hack this system by finding the repeating pattern in the passwords below: ")
        console.print("[yellow]If you intend on cheating... https://github.com/SamyIOoOI/Hack-Quest/blob/main/passwords_patterns.txt")
        correct_answer = password_patterns['First']['Answer'] ## Sets the answer in a variable for later comparison
        console.print(f"[bold yellow]{password_patterns['First']['1']}\n{password_patterns['First']['2']}\n{password_patterns['First']['3']}\n{password_patterns['First']['4']}")
        user_answer = input("Enter the repeating pattern: ").strip().lower() ## Receives user input
        if user_answer == correct_answer.lower(): ## Comapres user input and the answer
            console.print("[bold green]You have successfully breached this system.") ## Not much use. Informs the user of his success.
            hacked_token = True ## The token required by the hack command to give the player the reward.
        else:
            console.print("[bold red]Incorrect pattern. Hack failed.") ## Informs the user of his failure.
            hacked_token = False ## Not really necessary but just in case something goes wrong. Hacked token is already false by default.
    if hacked_value == 2:
        console.print("[bold green]Hack this system by finding the repeating pattern in the passwords below: ")
        console.print("[yellow]If you intend on cheating... https://github.com/SamyIOoOI/Hack-Quest/blob/main/passwords_patterns.txt")
        correct_answer = password_patterns['Second']['Answer']
        console.print(f"[bold yellow]{password_patterns['Second']['2']}\n{password_patterns['Second']['2']}\n{password_patterns['Second']['3']}\n{password_patterns['Second']['4']}")
        user_answer = input("Enter the repeating pattern: ").strip().lower()
        if user_answer == correct_answer.lower():
            console.print("[bold green]You have successfully breached this system.")
            hacked_token = True
        else:
            console.print("[bold red]Incorrect pattern. Hack failed.")
            hacked_token = False
    if hacked_value == 3:
        console.print("[bold green]Hack this system by finding the repeating pattern in the passwords below: ")
        console.print("[yellow]If you intend on cheating... https://github.com/SamyIOoOI/Hack-Quest/blob/main/passwords_patterns.txt")
        correct_answer = password_patterns['Third']['Answer']
        console.print(f"bold yellow{password_patterns['Third']['1']}\n{password_patterns['Third']['2']}\n{password_patterns['Third']['3']}\n{password_patterns['Third']['4']}")
        user_answer = input("Enter the repeating pattern: ").strip().lower()
        if user_answer == correct_answer.lower():
            console.print("[bold green]You have successfully breached this system.")
            hacked_token = True
        else:
            console.print("[bold red]Incorrect pattern. Hack failed.")
            hacked_token = False
    if hacked_value == 4:
        console.print("[bold green]Hack this system by finding the repeating patterns in the passwords below: ")
        console.print("[yellow]If you intend on cheating... https://github.com/SamyIOoOI/Hack-Quest/blob/main/passwords_patterns.txt")
        correct_answer = password_patterns['Fourth']['Answer']
        console.print(f"[bold yellow]{password_patterns['Fourth']['1']}\n{password_patterns['Fourth']['2']}\n{password_patterns['Fourth']['3']}\n{password_patterns['Fourth']['3']}\n{password_patterns['Fourth']['4']}")
        user_answer = input("Enter the repeating pattern: ").strip().lower()
        if user_answer == correct_answer.lower():
            console.print("[bold green]You have successfully breached this system.")
            hacked_token = True
        else:
            console.print("[bold red]Incorrect pattern. Hack failed.")
            hacked_token = False
    if hacked_value == 5:
        console.print("[bold green]Hack this system by finding repeating patterns in the passwords below: ")
        console.print("[yellow]If you intend on cheating... https://github.com/SamyIOoOI/Hack-Quest/blob/main/passwords_patterns.txt")
        correct_answer = password_patterns['Fifth']['Answer']
        console.print(f"[bold yellow]{password_patterns['Fifth']['1']}\n{password_patterns['Fifth']['2']}\n{password_patterns['Fifth']['3']}\n{password_patterns['Fifth']['3']}\n{password_patterns['Fifth']['4']}")
        user_answer = input("Enter the repeating pattern: ").strip().lower()
        if user_answer == correct_answer.lower():
            console.print("[bold green]You have successfully breached this system.")
            hacked_token = True
        else:
            console.print("[bold red]Incorrect pattern. Hack failed.")
            hacked_token = False
    if hacked_value == 6:
        console.print("[bold green]Hack this system by finding repeating patterns in the passwords below: ")
        console.print("[yellow]If you intend on cheating... https://github.com/SamyIOoOI/Hack-Quest/blob/main/passwords_patterns.txt")
        correct_answer = password_patterns['Sixth']['Answer']
        console.print(f"[bold yellow]{password_patterns['Sixth']['1']}\n{password_patterns['Sixth']['2']}\n{password_patterns['Sixth']['3']}\n{password_patterns['Sixth']['4']}")
        user_answer = input("Enter the repeating pattern: ").strip().lower()
        if user_answer == correct_answer.lower():
            console.print("[bold green]You have successfully breached this system.")
            hacked_token = True
        else:
            console.print("[bold red]Incorrect pattern. Hack failed.")
            hacked_token = False
def clear():  ## Clears the terminal before starting the game.
    os.system('cls' if os.name == 'nt' else 'clear') ## Checks the user's operating system and assigns the clear command based on that.
def prompt(): ## Option Menu or "Main Menu" of the game.
    clear()
    console.print("You can access the map here: [underline blue]https://github.com/SamyIOoOI/Hack-Quest/blob/main/Map.png[/underline blue]")
    a = input("Press Y to start, H to learn how to play or Q to quit: ").lower()
    if a == 'y':
        Game()
    elif a == 'h':
        clear()
        console.print("[bold green]Instructions\n[bold green]----------------------\n[green]Welcome to Hack Quest! Your objective is to hack into the bank's vault and steal the money without getting caught. You can move between rooms, collect items, and hack systems to progress. Be careful, as some actions may alert the authorities!\n\n[bold green]Commands:\n[green]- Move: Type the direction you want to go (North, South, East, West).\n- Get Item: Type 'get [item name]' to collect an item in the room.\n- Hack: Type 'hack [system name]' to attempt hacking a system.\n- Buy Item: Type 'buy [item name]' to purchase an item if you have enough coins.\n- Inventory: Type 'inventory' to check your collected items and coins.\n- Quit: Type 'q' to exit the game.\n\n[bold green]Good luck, hacker!")
        input("\nPress Enter to return to the main menu...")
        prompt()
    elif a == 'q':
        clear()
        console.print("[bold green]Thanks for playing Hack Quest! Goodbye!")
        exit()
def Game(): ## Main game function
    global current_room, Coins, inventory, stolen_atm, hacked_camera, hacked_office, hacked_database, hacked_archive, msg, hacked_token, hacked_value
    msg = ''
    while True: ## Game Loop
        clear()
        if not inventory: ## Displays the stats, when the inventory is empty
            console.print(f"[bold green]Hack Quest\n[bold green]----------------------\n[green][italic]Cracking codes like 1998.[/italic]\n[bold green]----------------------\nYou are currently in {current_room}.\n[bold green]----------------------\n[bold yellow]Inventory: Empty │ Coins: {Coins}\n[bold green]----------------------\n{msg}")
        else: ## Displays the stats, when the inventory isn't empty
            console.print(f"[bold green]Hack Quest\n[bold green]----------------------\n[green][italic]Cracking codes like 1998.[/italic]\n[bold green]----------------------\nYou are currently in {current_room}.\n[bold green]----------------------\n[bold yellow]Inventory: {inventory} │ coins: {Coins}\n[bold green]----------------------\n{msg}") 
        if 'Item' in map_rooms[current_room].keys(): ## Nearby Item Detection
            nearby_item = map_rooms[current_room]["Item"]
            if nearby_item not in inventory:
                if nearby_item[0].lower() in vowel_var:
                    console.print(f"[bold green]You see an[bold yellow] {nearby_item} [bold green]here. Type 'get' to pick it up.")
                else:
                    console.print(f"[bold green]You see a [bold yellow] {nearby_item} [bold green]here. Type 'get' to pick it up.")
        if 'Buy Item' in map_rooms[current_room]: ## Purchase finder
            shop_item = map_rooms[current_room]['Buy Item']
            console.print(f"[bold cyan]You can buy [bold yellow]{shop_item.title()}[bold cyan] here. Type 'buy {shop_item}' to purchase it.")
        if 'Hackable' in map_rooms[current_room]: ## Hackable finder
            hackable_device = map_rooms[current_room]['Hackable']
            console.print(f"[bold magenta]You can attempt to hack the [bold yellow]{hackable_device.title()}[bold magenta] here. Type 'hack {hackable_device}' to try.")
        user_input = input("What will you do?\n")
        split_user_input = user_input.split(' ')
        action = split_user_input[0].title()
        item = None
        direction = None
        if len(split_user_input) > 1:
            item = split_user_input[1:]
            direction = split_user_input[1].title()
            item = ' '.join(item).title()
        if action == 'Go': ## Move function
            if direction:
                try:
                    current_room = map_rooms[current_room][direction]
                    msg = f"You moved to the {current_room}."
                except:
                    msg = "You can't go that way."
            else:
                msg = "Please specify a direction to go."
        if action == 'Get': ## Snatch function
            room_data = map_rooms[current_room]
            room_item = room_data.get('Item', None)
            if not item:
                msg = "Please specify what item you want to get."
            elif room_item and item.lower() == room_item.lower() and room_item not in inventory:
                inventory.append(room_item)
                msg = f"You snatched the {room_item}."
                del map_rooms[current_room]['Item']
                if {room_item} == {'Lost Wallet'}:
                    Coins = Coins + 500
                    msg += " You found $500 in the wallet!"
                elif {room_item} == {'Tip Jar'}:
                    Coins = Coins + 350
                    msg += " You found $350 in the tip jar!"
            elif not room_item:
                msg = "There is no item to pick up here."
            elif room_item in inventory:
                msg = f"You already picked up the {room_item}."
            else:
                msg = "There is no such item here."
        if action == 'Buy': ## Buy function
            if 'Buy Item' in map_rooms[current_room]:
                shop_item = map_rooms[current_room]['Buy Item']
                shop_item_title = shop_item.title()
                if item.lower() == shop_item.lower():
                    if shop_item_title == 'New Laptop':
                        price = 1000
                    else:
                        price = 500
                    if Coins >= price:
                        if shop_item_title not in inventory:
                            inventory.append(shop_item_title)
                            Coins -= price
                            msg = f"You bought the {shop_item_title} for ${price}."
                            map_rooms['Shopping Center'].pop('Buy Item')
                        else:
                            msg = f"You already own the {shop_item_title}."
                    else:
                        msg = f"You don't have enough coins to buy the {shop_item_title}."
                else:
                    msg = f"You can't buy that here."
            else:
                msg = "There is nothing to buy here."
        if action == 'Hack': ## Hack function
            if 'Hackable' in map_rooms[current_room]:
                hackable_device = map_rooms[current_room]['Hackable']
                device = hackable_device.strip().lower()
                if device == 'atm cash' and not stolen_atm:
                    if any(lap in [item.lower() for item in inventory] for lap in ['old laptop', 'new laptop']):
                        hacking_screen()
                        if hacked_token == True:
                             Coins += 250
                             msg = "You have successfully hacked the ATM and withdrawn $250!"
                             stolen_atm = True
                             map_rooms['ATM'].pop('Hackable')
                             hacked_token = False
                             hacked_value = hacked_value + 1
                    else:
                        msg = "You need a laptop to hack the ATM. Try searching the HQ for an old laptop or buy a new one from the Shopping Center!"
                else:
                    if current_room not in ['ATM', 'The HQ', 'Main Street', 'Internet Cafe', 'Shopping Center', 'Apartment', 'East Street']:
                        if 'Hacking USB' not in inventory:
                            msg = "You need the Hacking USB to hack anything in the bank!"
                            continue
                    if device == 'camera system' and not hacked_camera:
                        if 'Bank Disguise' in inventory:
                            hacking_screen()
                            if hacked_token == True:
                                msg = "You have successfully hacked the bank's camera system. You can now move freely without being caught."
                                hacked_camera = True
                                map_rooms['Bank Entrance'].pop('Hackable')
                                hacked_value = hacked_value + 1
                        else:
                            msg = "You need the bank disguise from the apartment to do actions inside the bank."
                    elif device == 'archive database' and not hacked_archive:
                        if hacked_camera:
                            if any(lap in [item.lower() for item in inventory] for lap in ['new laptop']):
                                hacking_screen()
                                if hacked_token == True:
                                    msg = 'You have successfully hacked into the bank archives and found the codes. You now need to hack the bank servers.'
                                    hacked_archive = True
                                    map_rooms['Bank Archives Room'].pop('Hackable')
                                    hacked_token = False
                                    hacked_value = hacked_value + 1
                            else:
                                msg = "You need a better laptop to hack the bank systems. Try buying one from the shopping center."
                        else:
                            msg = "You need to hack the cameras first."
                    elif device == 'bank servers' and not hacked_database:
                        if hacked_archive:
                            hacking_screen()
                            if hacked_token == True:
                                msg = "You have successfully hacked into the bank servers and found the manager's PC digits. Proceed to the office area and hack the vault's security system blueprint and passcode."
                                hacked_database = True
                                map_rooms['Bank Server Room'].pop('Hackable')
                                hacked_token = False
                                hacked_value = hacked_value + 1
                        else:
                            msg = "You need to hack the bank archives first."
                    elif device == "manager's pc" and hacked_database and not hacked_office:
                        hacking_screen()
                        if hacked_token == True:
                            msg = "You have successfully hacked into the manager's PC and found the vault's security system blueprint and passcode. Proceed to the vault and hack the protection system."
                            hacked_office = True
                            map_rooms['Bank Office Room'].pop('Hackable')
                            hacked_token = False
                            hacked_value = hacked_value + 1
                    elif device == 'vault protection system' and hacked_office:
                        hacking_screen()
                        if hacked_token == True:
                            msg = "You have successfully hacked into the bank's vault protection system. The cash is yours!\nThank you for playing Hack Quest!"
                            Coins += 1000000
                    else:
                        msg = "You can't hack this system right now."
                    if Coins >= 1000000:
                        console.print("[bold purple] You have successfully hacked into the bank's vault protection system. The cash is yours!\n[bold magenta] Congratulations, you have completed Hack Quest and earned $1,000,000!\n[bold green]Thank you for playing Hack Quest!")
                        break
            else:
                msg = "There is nothing to hack here."
map_rooms = { 'The HQ' : {'East' : 'Main Street', 'Item': 'Old Laptop'}, ## Map Database
             'Main Street' : {'West' : 'The HQ', 'North' : 'Internet Cafe', 'South' : 'ATM', 'East' : 'East Street', 'Item': 'Lost Wallet'},
             'Internet Cafe' : {'South' : 'Main Street', 'Item' : 'Tip Jar'},
             'ATM' : {'North' : 'Main Street', 'Hackable' : 'ATM Cash'},
             'East Street' : {'West' : 'Main Street', 'East' : 'Bank Entrance', 'North' : 'Apartment', 'South' : 'Shopping Center', 'Item' : 'Hacking USB'},
             'Apartment' : {'South' : 'East Street', 'Item' : 'Bank Disguise'},
             'Shopping Center' : {'North' : 'East Street', 'Buy Item' : 'new Laptop'},
             'Bank Entrance' : {'West' : 'East Street', 'East' : 'Bank Office Room', 'North' : 'Bank Server Room', 'South' : 'Bank Archives Room', 'Hackable' : 'camera System'},
             'Bank Archives Room' : {'North' : 'Bank Entrance', 'Hackable' : 'archive Database'},
             'Bank Server Room' : {'South' : 'Bank Entrance', 'Hackable' : 'bank Servers'},
             'Bank Office Room' : {'West' : 'Bank Entrance', 'East' : 'Vault', 'Hackable' : "manager's pc"},
             'Vault' : {'West' : 'Bank Office Room', 'Hackable' : 'vault Protection System'} } ## Passwords Database
password_patterns = {'First' : {'1': '7x9kQwTz8pLk3Jv', '2':'4mN2bXcV9kQwTz', '3' : '9kQwTz5rTgH8sQw', '4' : 'QwTz7uYhLk9kQwTz3', 'Answer' : '9kQwTz'},
                     'Second' : {'1':'2pL8rXy7mNqL', '2':'5tGhLpL8rXy', '3':'8pL8rXy6vBnMp', '4':'3kLpL8rXy9', 'Answer':'pL8rXy'},
                      'Third' : {'1':'1Zx7LmN2b', '2':'3nMZx7LmN', '3':'4Zx7LmN5t', '4':'6p7Zx7LmNN', 'Answer':'Zx7LmN'},
                       'Fourth' : {'1':'tR5qLp8nM', '2':'2tR5qLp3bN', '3':'4tR5qL5vGtR5qLp', '4':'6tR5qLp7kL', 'Answer':'tR5qLp'},
                        'Fifth' : {'1':'1Qp8zLm2b3', '2':'4nMQp8zLm', '3':'5Qp8zLm6t7', '4':'8pQp8zLm9N', 'Answer':'Qp8zLm'},
                         'Sixth' : {'1':'vT3kXy1a2b', '2':'3c4vT3kXy5d', '3':'6e7f8vT3kXy', '4':'9g0h1vT3kXy2', 'Answer':'vT3kXy'} }
def main():
    clear()
    prompt()

if __name__ == "__main__":
    main()