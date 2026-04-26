def calculate_sum(a, b):
    # Intentional bug: returning a string concatenation instead of integer sum
    return str(a) + str(b)

def main():
    result = calculate_sum(5, 10)

    # This will fail because we are trying to add a string to an integer
    final_result = result + 20

    print(f"The final result is {final_result}")

if __name__ == "__main__":
    main()
