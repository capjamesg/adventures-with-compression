# cmunks: 1546908751127640268109
# Diffs: 0 out of 13519825
# Original size: 67943.478515625 KB
# brotli original: 19576.7958984375 KB
# brotly w/ gcd: 21496.8271484375 KB
# equivalence? True.
# 642K Dec 31 18:23 compressed1.txt.br
# 631K Dec 31 18:33 compressed2.txt.br

import math
import numpy as np
import os
import sys

with open("compressed1.txt", "r") as compressed_file:
    compressed_lines = compressed_file.readlines()

starter_nums = [int(i) for i in compressed_lines[0].split(" ")]

# print("starter_nums:", starter_nums)

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
cls = []

for line in compressed_lines:
    for integer in line.split(" "):
        items.append(int(integer))
        cls.append(len(integer))

data = np.array(items)

# divide into chunks of len 20 each
chunks = []

for i in range(0, len(data), 20):
    # check if chunk would start with 0
    if str(data[i]).startswith("0"):
        print("Error on chunk", i)
    chunks.append(data[i : i + 20])

original_chunks = chunks

gcds = []

for chunk in chunks:
    gcds.append(math.gcd(int("".join(map(str, chunk))), 10**20))

divided_chunks = []
remainders = []

for chunk, gcd in zip(chunks, gcds):
    divided_chunks.append(int("".join(map(str, chunk))) // gcd)
    remainders.append(int("".join(map(str, chunk))) % gcd)

# count non-zero remainders
non_zero_remainders = 0

for remainder in remainders:
    if remainder != 0:
        non_zero_remainders += 1

# calculate difference between each chunk using delta encoding
        
deltas = []

for i in range(1, len(divided_chunks)):
    deltas.append(divided_chunks[i] - divided_chunks[i - 1])

# save all divided chunks in following format:
# chunk [space] gcd, chunk [space] gcd, ...


with open("compressed2.txt", "w") as compressed_file:
    for chunk, gcd in zip(divided_chunks, gcds):
        # divide each chunk num by 2
        # chunk = int(chunk) // 2

        compressed_file.write(f"{chunk} {gcd}\n")

# get size of compressed2.txt
# print("Original size:", os.path.getsize("compressed1.txt") / 1024, "KB")
# print("Compressed size:", os.path.getsize("compressed2.txt") / 1024, "KB")

# decompress
with open("compressed2.txt", "r") as compressed_file:
    compressed_lines = compressed_file.readlines()

# iterate over each, if second item gcd

chunks = []
gcds = []

for chunk in compressed_lines:
    if len(chunk.strip()) == 0:
        continue

    # join chunk, get last num
    chunk = chunk.strip()
    
    chk, gcd = chunk.split(" ")

    chunks.append(chk)
    gcds.append(gcd)

# multiply by gcd
multiplied_chunks = []

for chunk, gcd in zip(chunks, gcds):
    multiplied_chunks.append(int(chunk) * int(gcd))

print("cmunks:", multiplied_chunks[-1])

reconstructed_chunks = [int(chunk) * int(gcd.strip()) for chunk, gcd in zip(chunks, gcds)]

# Convert back to strings
reconstructed_strings = []
for num, length_list in zip(reconstructed_chunks, wl_chunks):
    num_str = str(num)
    start_index = 0
    for length in length_list:
        end_index = start_index + length
        reconstructed_strings.append(num_str[start_index:end_index].zfill(length))
        start_index = end_index

# Join the strings to form the original data
original_data = ' '.join(reconstructed_strings)

# Write the original data to a file
with open("decompressed.txt", "w") as decompressed_file:
    decompressed_file.write(original_data)

# check integrity
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

# get size of compressed2.txt
print("Original size:", os.path.getsize("compressed1.txt") / 1024, "KB")
print("Compressed size:", os.path.getsize("compressed2.txt") / 1024, "KB")

# compress w/ brotli and keep

import subprocess

subprocess.run(["brotli", "-fk", "compressed1.txt"])
subprocess.run(["brotli", "-fk", "compressed2.txt"])

print("brotli original:", os.path.getsize("compressed1.txt.br") / 1024, "KB")
print("brotly w/ gcd:", os.path.getsize("compressed2.txt.br") / 1024, "KB")