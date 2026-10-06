# import os

# # Ask the user which folder to look at
# path = input("Enter a folder path (or press Enter for the current folder): ")

# # If the user typed nothing, use the current folder
# if path == "":
#     path = "."

# # Get the list of names inside that folder
# contents = os.listdir(path)

# # Print each name on its own line
# print("Contents of the folder:")
# for item in contents:
#     print(item)


text = "Python Programming"
up = text[0:6]
ne = text[::-1]
print(up)
print(ne)
