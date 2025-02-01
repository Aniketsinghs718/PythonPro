import random

# create a game that help to guess the number between 1 to 100
# the program will generate a random number between 1 to 100 and ask the user to guess the number

def game():
    number=random.randint(1,100)
    guess=False
    print("Welcome to the guess the number game!!")
    print("Guess no. between 1 to 100")
    attempt=0
    while not guess:
        attempt+=1
        user = int(input("enter the no."))
        if user>number:
            if(abs(user-number)<=5):
                print("pretty close:HIGH")
            else:
                print("Too high!!")
        elif user==number:
            print(f"Hurray to guessed correct in {attempt} attempt. the no. is {number} ")
            print("Thanks for playing😊😊")
            guess=True
        else:
            if(abs(user-number)<=5):
                print("pretty close: LOW")
            else:
                print("Too low!!")

game()
