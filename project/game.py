"""
building a stone paper scissor game
"""
import random
def comp_choice():
    return random.choice(["stone","paper","scissor"])

def user_choice():
    
    element={1:"stone",
         2:"paper",
         3:"scissor"}
    while True:
        user=input('1:stone     2:paper     3:scissor \n ')
        
        if user=="quit":
            return "quit"
        try:
            useri=int(user)
            if useri in element:
                return element[useri]
        except ValueError:
            pass        
          
        print("invalid input")    
       

def winner(comp,user):
    if(comp==user):
        print("Draw...")

    elif( user=="stone" and comp=="scissor") or (user=="paper" and comp=="stone") or (user=="scissor" and comp=="paper"):
        print("You win!!!!!")

    else:
        print("you loose")

def play_game():
    while True:
        user=user_choice()
        if user=="quit":
            break
        computer=comp_choice()
        print(f"you choose {user} comp choose : {computer}")
        winner(computer,user)
        print('\n  ')

play_game()



