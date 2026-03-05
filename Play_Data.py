# variables
    # product names
product1 = "Cheapa-Cola"
product2 = "Mr. Salt"
product3 = "Door Eatos"
product4 = "Air Bag Potato Chips"
product5 = "Red Dye 3000 Sports Drink"
    # product prices
price1 = 0.01
price2 = 1.85
price3 = 2.37
price4 = 3.09
price5 = 1.99

# Selection Prompt
while True:
    print(f"Welcome to my vending machine. Our available items are as follows: 1. {product1}: ${price1}, 2. {product2}: ${price2}, 3. {product3}: ${price3}, 4. {product4}: ${price4}, 5. {product5}: ${price5}, ")
    selection = input("What item would you like today? ( enter 1, 2, 3, 4, or 5)")
    if selection == 1:
        selection = product1
        price = price1
    elif selection == 2:
        selection = product2
        price = price2
    elif selection == 3:
        selection = product3
        price = price3
    elif selection == 4:
        selection = product4
        price = price4
    elif selection == 5:
        selection = product5
        price = price5
    else:
        print("Invlid input. Please try again.")
        continue
    amount = input(f"Ok. How many of that item would you like?")
    total = price * amount
    done = input(f"You ordered {selection} and your current total is {total}. Would you like anything else? (type 1 for no and 2 for yes.)")