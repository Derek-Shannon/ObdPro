with open("output(official).txt", "r") as file:
    # Read all lines in the file
    lines = file.readlines()
    
    # Split each line by spaces
    split_lines = [line.strip().split()[2] for line in lines]

# Print the result
for line in split_lines:
    print(line) 