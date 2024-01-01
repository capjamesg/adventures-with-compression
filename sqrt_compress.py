import math
import os

import numpy as np
import tqdm

# open compressed.txt line by line
with open("compressed1.txt", "r") as compressed_file:
    compressed_lines = compressed_file.readlines()

# get first 100 lines
compressed_lines = compressed_lines  # [:10]

# 499020

# get len of each word
word_lengths = []

for line in compressed_lines:
    for integer in line.split(" "):
        word_lengths.append(len(integer))

# chunk the owrd lengths
wl_chunks = []

for i in range(0, len(word_lengths), 20):
    wl_chunks.append(word_lengths[i : i + 20])

# turn string into list of ints
items = []

for line in compressed_lines:
    for integer in line.split(" "):
        items.append(int(integer))

print(len(items))

data = np.array(items, dtype=np.int32)

# divide into chunks of len 20 each
chunks = []

for i in range(0, len(data), 20):
    chunks.append(data[i : i + 20])

# for each chunk, get square root
sqrts = []
not_sqrts = []

import math

for i, chunk in enumerate(chunks):
    # concat all the numbers
    chunk = "".join(map(str, chunk))
    # if chunk starts with 0, print error
    if chunk.startswith("0"):
        # TODO: More robust out of range handling
        print("Error on chunk", i)
    sqrt_value = math.sqrt(int(chunk))
    # preserve full precision,
    sqrts.append(math.sqrt(int(chunk)))
    not_sqrts.append(int(chunk))

print(int(not_sqrts[0]), "first chunk as ints")

# print(len(sqrts), "sqrts")

# save
with open("compressed2.txt", "w") as compressed_file:
    compressed_file.write(" ".join(map(str, sqrts)))

# in kb
print("Compressed size:", os.path.getsize("compressed1.txt") / 100000)
print("New size:", os.path.getsize("compressed2.txt") / 100000)

# reverse
# open compressed.txt line by line
with open("compressed2.txt", "r") as compressed_file:
    compressed_lines = compressed_file.readlines()
# Read the compressed data from 'compressed2.txt'
with open("compressed2.txt", "r") as file:
    compressed_data = file.read().split()

# Convert the data back to their squared values
# 102103104105106107108109110111112113114115112116117118119112
# 102103104105106092903245206908614382166530351861722861535232
squared_data = [str(int(float(number) ** 2)) for number in compressed_data]

print(squared_data[0], "squared")
# Write the decompressed data to a file
final_result = []

for i, number in enumerate(squared_data):
    for length in wl_chunks[i]:
        final_result.append(number[:length])
        number = number[length:]

# restore to original length of

with open("decompressed.txt", "w") as file:
    file.write(" ".join(final_result))

# check for equality
with open("compressed1.txt", "r") as compressed_file:
    compressed_lines = compressed_file.read()

with open("decompressed.txt", "r") as decompressed_file:
    decompressed_lines = decompressed_file.read()

compressed_nums = compressed_lines.split(" ")
decompressed_nums = decompressed_lines.split(" ")

diffs = 0

for i, num in enumerate(compressed_nums):
    if num != decompressed_nums[i]:
        if num == "0" + decompressed_nums[i]:
            print("Added leading 0")
            continue

        diffs += 1

print("Diffs:", diffs, "out of", len(compressed_nums))

# import tqdm

# # Pre-calculate the total number of elements to be added
# total_elements = 0
# for number in tqdm.tqdm(squared_data, desc="Calculating total elements"):
#     total_elements += sum(len(number) // length for length in word_lengths)
# print(total_elements)
# # Pre-allocate the list with None to avoid dynamic resizing
# decompressed_data = [None] * total_elements

# # Use a single loop with enumerate for better efficiency
# current_index = 0
# for number in tqdm.tqdm(squared_data):
#     start_index = 0
#     for length in word_lengths:
#         end_index = start_index + length
#         decompressed_data[current_index] = number[start_index:end_index]
#         start_index = end_index
#         current_index += 1

# # Filter out None values in case of any miscalculation
# decompressed_data = [num for num in decompressed_data if num is not None]

# # Convert the decompressed data back to integers
# decompressed_integers = [int(num) for num in decompressed_data]

# # Write the decompressed data to a file
# with open("decompressed.txt", "w") as file:
#     for integer in decompressed_integers:
#         file.write(f"{integer} ")

# # Verify the size of the decompressed file
# import os
# print("Decompressed size:", os.path.getsize("decompressed.txt") / 1000, "KB")

# # check for equality
# with open("compressed1.txt", "r") as compressed_file:
#     compressed_lines = compressed_file.readlines()

# # TODO: compute errors
