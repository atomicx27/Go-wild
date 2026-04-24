def calculate_average(numbers):
    total = 0
    for i in range(len(numbers) + 1): # BUG: Index out of bounds
        total += numbers[i]

    return total / len(numbers)

def greet_users(users):
    for u in users:
        # BUG: Cannot concatenate str and int directly
        msg = "Hello, user ID: " + u['id'] + ". Welcome " + u['name']
        print(msg)

if __name__ == "__main__":
    scores = [85, 90, 78, 92]
    avg = calculate_average(scores)
    print("The average score is: " + avg) # BUG: Can't concat str and float

    user_list = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'}
    ]
    greet_users(user_list)
