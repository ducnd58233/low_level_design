from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Player:
    name: str
    sign: str
    
class Board:
    def __init__(self, size: int):
        if not (1 <= size <= 20):
            raise ValueError("Board size must be between 1 and 20")
        
        self.__size = size
        self.__id_to_sign = defaultdict(str)
    
    def get_size(self) -> int:
        return self.__size
    
    def __get_id(self, row: int, col: int) -> int:
        return col + row * self.__size
    
    def display(self):
        for row in range(self.__size):
            line = []
            for col in range(self.__size):
                sign = self.__id_to_sign.get(self.__get_id(row, col), '.')
                line.append(sign)
            print(" ".join(line))
            
    def place(self, row: int, col: int, sign: str) -> bool:
        if not self.__is_valid(row, col, '.'):
            return False
        
        self.__id_to_sign[self.__get_id(row, col)] = sign
        return True
    
    def check_winner(self, sign: str) -> bool:
        def count_consecutive(dr, dc):
            for r in range(self.__size):
                for c in range(self.__size):
                    count = 0
                    for k in range(5):
                        nr, nc = r + k * dr, c + k * dc
                        if not self.__is_valid(nr, nc, sign):
                            break
                        count += 1
                    if count == 5:
                        return True
            return False
        
        return (
            count_consecutive(1, 0) or # vertical
            count_consecutive(0, 1) or # horizontal
            count_consecutive(1, 1) or # diagonal
            count_consecutive(1, -1) # anti-diagonal
        )
    
    def __is_valid(self, row: int, col: int, sign: str) -> bool:
        return 0 <= row < self.__size and 0 <= col < self.__size and self.__id_to_sign.get(self.__get_id(row, col), ".") == sign

class Game:
    def __init__(self, size: int):
        self.__board = Board(size = size)
        self.__players = [
            Player(name="Player 1", sign="X"),
            Player(name="Player 2", sign="O"),
        ]
        self.__current_turn = 0
        
    def __switch_player(self):
        self.__current_turn = 1 - self.__current_turn
        
    def play(self):
        self.__board.display()
        move_cnt = 0
        max_moves = self.__board.get_size() * self.__board.get_size()
        x = y = -1
        
        while move_cnt < max_moves:
            player = self.__players[self.__current_turn]
            print(f"{player.name} ({player.sign})'s turn")
            
            try:
                x, y = map(int, input("Enter your move (row col): ").strip().split())
            except ValueError:
                print(f"Invalid input (${x} ${y}). Please enter 2 numbers")
                continue
            
            if self.__board.place(x, y, player.sign):
                self.__board.display()
                move_cnt += 1
                
                if self.__board.check_winner(player.sign):
                    print(f"{player.name} wins")
                    return
                self.__switch_player()
            else:
                print("Invalid move. Try again.")
        print("It's a draw")
        
if __name__ == "__main__":
    size = input("Enter board size (<= 20): ")
    try:
        game = Game(int(size))
        game.play()
    except ValueError as e:
        print("Error:", e)