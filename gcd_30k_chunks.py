# Diffs: 0 out of 13519825
# Original size: 67943.478515625 KB
# Compressed size: 54741.71875 KB
# brotli original: 19576.7958984375 KB
# brotly w/ gcd: 19376.34375 KB
# 20046639 Dec 31 18:35 compressed1.txt.br
# 19841376 Dec 31 18:45 compressed2.txt.br
# 205263 difference = 205kb reduction

import math
import numpy as np
import os
import sys

CHUNK_SIZE = 30000

import sys

sys.set_int_max_str_digits(300000)

with open("compressed1.txt", "r") as compressed_file:
    compressed_lines = compressed_file.readlines()

starter_nums = [int(i) for i in compressed_lines[0].split(" ")]

# print("starter_nums:", starter_nums)

# get first 100 lines
compressed_lines = compressed_lines  # [:10]

# 4990CHUNK_SIZE

# get len of each word
word_lengths = []

for line in compressed_lines:
    for integer in line.split(" "):
        word_lengths.append(len(integer))

# chunk the owrd lengths
wl_chunks = []

for i in range(0, len(word_lengths), CHUNK_SIZE):
    wl_chunks.append(word_lengths[i : i + CHUNK_SIZE])

# turn string into list of ints
items = []
cls = []

for line in compressed_lines:
    for integer in line.split(" "):
        items.append(int(integer))
        cls.append(len(integer))

data = np.array(items)

# divide into chunks of len CHUNK_SIZE each
chunks = []

for i in range(0, len(data), CHUNK_SIZE):
    # check if chunk would start with 0
    if str(data[i]).startswith("0"):
        print("Error on chunk", i)
    chunks.append(data[i : i + CHUNK_SIZE])

original_chunks = chunks

print("CHUNK LENGTH:", len(chunks))

chunks = chunks #[:20]

gcds = []

import tqdm
# add message to say "calculating gcds"
for chunk in tqdm.tqdm(chunks, total=len(chunks), desc="Calculating GCDs"):
    gcds.append(math.gcd(int("".join(map(str, chunk))), 10**CHUNK_SIZE))

# exit()
divided_chunks = []
remainders = []

print("Prepared chunks")

# print("CHUNK LENGTH:", len(chunks))
for chunk, gcd in tqdm.tqdm(zip(chunks, gcds), total=len(chunks), desc="Dividing chunks"):
    print("chunk:", chunk)
    print("gcd:", gcd)
    # concat chunk
    # if len("".join(map(str, chunk))) > len(str(int("".join(map(str, chunk))) // gcd)):
    #     print("difference:", len(str(int("".join(map(str, chunk))) // gcd)) - len("".join(map(str, chunk))))
    divided_chunks.append(int("".join(map(str, chunk))) // gcd)
    remainders.append(int("".join(map(str, chunk))) % gcd)

# count non-zero remainders
non_zero_remainders = 0

for remainder in remainders:
    if remainder != 0:
        non_zero_remainders += 1

# calculate difference between each chunk using delta encoding

# save all divided chunks in following format:
# chunk [space] gcd, chunk [space] gcd, ...

# save word lengths
with open("wls.txt", "w") as compressed_file:
    for wl_chunk in wl_chunks:
        compressed_file.write(f"{wl_chunk}")

with open("compressed2.txt", "w") as compressed_file:
    for chunk, gcd in zip(divided_chunks, gcds):
        compressed_file.write(f"{chunk} {gcd}\n")

# exit()

# get size of compressed2.txt
print("Original size:", os.path.getsize("compressed1.txt") / 1024, "KB")
print("Compressed size:", os.path.getsize("compressed2.txt") + os.path.getsize("wls.txt") / 1024, "KB")

# decompress
with open("compressed2.txt", "r") as compressed_file:
    compressed_lines = compressed_file.readlines()

# iterate over each, if second item gcd

chunks = []
gcds = []

for chunk in compressed_lines:
    if len(chunk.strip()) == 0:
        continue
    
    chk, gcd = chunk.split(" ")

    chunks.append(chk)
    gcds.append(gcd)

# multiply by gcd
multiplied_chunks = []

for chunk, gcd in zip(chunks, gcds):
    multiplied_chunks.append(int(chunk) * int(gcd))

# print("cmunks:", multiplied_chunks[-1])

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
subprocess.run(["brotli", "-fk", "wls.txt"])

print("brotli original:", os.path.getsize("compressed1.txt.br") / 1024, "KB")
print("brotly w/ gcd:", (os.path.getsize("compressed2.txt.br") + os.path.getsize("wls.txt.br")) / 1024, "KB")