import random
import string

print("Test generator by Drew")

def random_alpha_line():
    first_char = random.choice(string.ascii_letters)
    word = ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 10)))
    return f"{first_char}{word} test line"

def random_numerical_line():
    first_digit = str(random.randint(0, 9))
    word = ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 10)))
    return f"{first_digit}{word} numeric line"

def get_sort_mode():
    while True:
        choice = input("Sort mode: (a)lphabetical or (n)umerical: ").strip().lower()
        if choice in ('a', 'n'):
            return 'alphabetical' if choice == 'a' else 'numerical'
        print("Please choose a or n.")

def get_line_count():
    while True:
        count = input("How many lines would you like listed? ").strip()
        if count.isdigit() and int(count) > 0:
            return int(count)
        print("Please enter a positive whole number.")

def generate_test_file(mode, num_lines):
    filename = f"{mode}_test.txt"
    generator = random_alpha_line if mode == 'alphabetical' else random_numerical_line
    with open(filename, 'w', encoding='utf-8') as f:
        for _ in range(num_lines):
            f.write(generator() + '\n')
    print(f"Test file '{filename}' with {num_lines} {mode} lines created.")

if __name__ == "__main__":
    mode = get_sort_mode()
    num_lines = get_line_count()
    generate_test_file(mode, num_lines)
