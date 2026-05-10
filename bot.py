from rich import print
from rich.panel import Panel
from rich.table import Table
import random
import os
import json
from collections import defaultdict, deque
#

class NGramBot:
    def __init__(self, n=3, filename="bot_brain.json"):
        self.n = n
        self.filename = filename
        self.model = self._load_model()
        self.player_history = deque(maxlen=n-1)

    def _load_model(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                model = defaultdict(lambda: {"R": 0, "P": 0, "S": 0})
                for k, v in data.items():
                    model[tuple(k.split(','))] = v
                return model
        return defaultdict(lambda: {"R": 0, "P": 0, "S": 0})

    def save_model(self):
        serializable_model = {",".join(k): v for k, v in self.model.items()}
        with open(self.filename, 'w') as f:
            json.dump(serializable_model, f)

    def predict(self):
        context = tuple(self.player_history)
        if len(context) < self.n - 1 or context not in self.model:
            return random.choice(["R", "P", "S"])

        stats = self.model[context]
        if sum(stats.values()) == 0:
            return random.choice(["R", "P", "S"])
            
        predicted_player_move = max(stats, key=stats.get)
        return {"R": "P", "P": "S", "S": "R"}[predicted_player_move]
        # R= stats["R"]
        # S= stats["S"]
        # P= stats["P"]
        # SS = R+S+P
        # predicted = random.choices(["R", "P", "S"], weights=[R/(SS)*100, P/(SS)*100, S/(SS)*100])[0]
        # return {"R": "P", "P": "S", "S": "R"}[predicted]


    def update(self, player_move):
        context = tuple(self.player_history)
        if len(context) == self.n - 1:
            self.model[context][player_move] += 1
        self.player_history.append(player_move)


# --- ИНТЕРФЕЙС И ИГРА ---
def winner(bm, pm):
    winner_tabble = {
        "RR": 0,
        "RP": -1,
        "RS": 1,
        "PP": 0,
        "PR": 1,
        "PS": -1,
        "SS": 0,
        "SP": 1,
        "SR": -1
    }
    return winner_tabble[bm+pm]
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Создаем бота (N=3 означает, что он смотрит на 2 последних хода)
bot = NGramBot(n=3)

while True:
    clear()
    print(Panel(
        "[bold cyan]1.[/bold cyan] Почати гру\n"
        "[bold cyan]2.[/bold cyan] Пам'ять бота (статистика)\n"
        "[bold cyan]3.[/bold cyan] Логи ігор (хто як ходив)\n"
        "[bold cyan]4.[/bold cyan] Вийти", 
        title="Виберіть дію"
    ))
    n = input("Введіть номер: ")
    clear()
    
    match n:
        case "1":
            round_num = 1
            while True:
                bot_move = bot.predict()
                player_move = input("Ваш ход (R/P/S): ").upper()
                
                if player_move not in ["R", "P", "S"]:
                    print("[red]Помилка: введіть R, P або S[/red]")
                    continue

                bot.update(player_move)
                bot.save_model()

                print(f"Бот выкинул: [bold cyan]{bot_move}[/bold cyan]. Вы выбрали: [bold green]{player_move}[/bold green]")
                
                # Открываем файл в режиме дозаписи ("a" - append)
                with open("game_logs.txt", "a", encoding="utf-8") as log_file:
                    log_file.write(f"Раунд {round_num} | Бот: {bot_move} - Гравець: {player_move}\n")
                
                round_num += 1

                if input("\nПродолжить? (y/n): ").lower() != 'y':
                    break
                    
        case "2":
            table = Table(title="Що бот знає про ваші звички")
            table.add_column("Попередні ходи", justify="center", style="cyan")
            table.add_column("Ймовірність R (Камінь)", justify="center", style="red")
            table.add_column("Ймовірність P (Папір)", justify="center", style="green")
            table.add_column("Ймовірність S (Ножиці)", justify="center", style="yellow")

            if not bot.model:
                print("[yellow]Бот ще не зібрав достатньо статистики.[/yellow]")
            else:
                for context, stats in bot.model.items():
                    ctx_str = " -> ".join(context)
                    table.add_row(ctx_str, str(stats["R"]), str(stats["P"]), str(stats["S"]))
                print(table)
            
            input("\nНатисніть Enter, щоб повернутися...")
            
        case "3":
            print(Panel("[bold yellow]Історія всіх зіграних раундів:[/bold yellow]"))
            if os.path.exists("game_logs.txt"):
                with open("game_logs.txt", "r", encoding="utf-8") as log_file:
                    logs = log_file.readlines()
                    # Выводим последние 20 записей, чтобы не засорять экран
                    for line in logs[-20:]:
                        print(line.strip())
            else:
                print("[yellow]Ви ще не зіграли жодного раунду.[/yellow]")
                
            input("\nНатисніть Enter, щоб повернутися...")
        
        case "4":
            print("[green]Гарного дня![/green]")
            break
        case _:
            print("[red]Невірний номер[/red]")
            input("Натисніть Enter...")
