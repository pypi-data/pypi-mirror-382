import os
import sys

def Pimemory():
    pi = "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679" 
    pi_list = ""
    i = 3
    print("Welcome to the Pi Memorization Practice Program!")

    print("\nType the num of decimal places you wish to start\n(enter for default)")

    piInput = (input())
    if piInput == None or piInput == '':
        i = 3
    elif int(piInput) > 1:
        i = int(piInput) + 1

    for x in range(i):
        pi_list += pi[x]

    os.system("cls")
    print(f'Please type the following Pi digits')
    while True:
        pi_list += pi[i]
        i += 1
        if i == 100:
            break
        print(pi_list)
        piInput = input()
        if piInput == pi_list:
            os.system("cls")
            piINput = input('Input once more time to finish\n')
            if piInput != pi_list:
                print('Wrong! Try again.')
                break
            if piInput == pi_list:
                os.system("cls")
            
        if piInput != pi_list:
            print('Wrong! Try again.')
            break
    