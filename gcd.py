# cmunks: 1546908751127640268109
# Diffs: 0 out of 13519825
# Original size: 67943.478515625 KB
# brotli original: 19576.7958984375 KB
# brotly w/ gcd: 21496.8271484375 KB
# equivalence? True.
# 642K Dec 31 18:23 compressed1.txt.br
# 631K Dec 31 18:33 compressed2.txt.br

# -rw-r--r--   1 james  staff   2.0M Dec 31 22:30 compressed2.txt
# -rw-r--r--   1 james  staff   732K Dec 31 21:15 compressed2.txt.br
# 867K Dec 31 22:31 starter_nums (1).flac

import math
import numpy as np
import os
import sys

CHUNK_SIZE = 3

import sys

sys.set_int_max_str_digits(3000000)

with open("compressed1.txt", "r") as compressed_file:
    compressed_lines = compressed_file.readlines()

starter_nums = [int(i) for i in compressed_lines[0].split(" ")]

starter_nums = [int(i) for i in starter_nums]

# remove values below 35000
# starter_nums = [i for i in starter_nums if i < 35000]

original_starter_nums = starter_nums.copy()
#

# turn starter nums from 414 151, etc.
# into signals like 414.151

# print max value
print("max value:", max(starter_nums))

# starter_nums = [re.sub(r"(\d{3})(\d{3})", r"\1.\2", i) for i in starter_nums]
import soundfile

max_val = max(starter_nums)
min_val = min(starter_nums)
normalized_starter_nums = [int(32767 * (i - min_val) / (max_val - min_val)) - 16384 for i in starter_nums]

# Convert to np.int16
starter_nums_np = np.array(normalized_starter_nums, dtype=np.int16)

# Save as WAV
soundfile.write("starter_nums.wav", starter_nums_np, samplerate=44100)

starter_nums, samplerate = soundfile.read("starter_nums.wav", dtype='int16')
# check for equality
print("starter_nums == starter_nums_np:", np.array_equal(starter_nums, starter_nums_np))

# unnormalize
starter_nums = [int((i + 16384) * (max_val - min_val) / 32767) + min_val for i in starter_nums]

# check for equality
print("starter_nums == original_starter_nums:", np.array_equal(starter_nums, original_starter_nums))

# compare file sizes

# get size of compressed2.txt
print("Original size:", os.path.getsize("compressed1.txt") / 1024, "KB")
print("Compressed size:", os.path.getsize("starter_nums.wav") / 1024, "KB")

exit()

# get len of each word
word_lengths = []

for integer in starter_nums:
    word_lengths.append(len(str(integer)))

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

divided_chunks = []
remainders = []

print("Prepared chunks")

# print("CHUNK LENGTH:", len(chunks))
for chunk, gcd in tqdm.tqdm(zip(chunks, gcds), total=len(chunks), desc="Dividing chunks"):
    divided_chunks.append(int("".join(map(str, chunk))) // gcd)
    remainders.append(int("".join(map(str, chunk))) % gcd)

# count non-zero remainders
non_zero_remainders = 0

for remainder in remainders:
    if remainder != 0:
        non_zero_remainders += 1

# save to compressed2
with open("compressed2.txt", "w") as compressed_file:
    for chunk, gcd in zip(divided_chunks, gcds):
        compressed_file.write(f"{chunk} {gcd}\n")

# get size of compressed2.txt
print("Original size:", os.path.getsize("compressed1.txt") / 1024, "KB")
print("Compressed size:", os.path.getsize("compressed2.txt") / 1024, "KB")

# brotli compress 2
import subprocess

# subprocess.run(["brotli", "-fk", "compressed1.txt"])
# subprocess.run(["brotli", "-fk", "compressed2.txt"])

print("brotli original:", os.path.getsize("compressed1.txt.br") / 1024, "KB")
print("brotly w/ gcd:", os.path.getsize("compressed2.txt.br") / 1024, "KB")

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

print("brotli original:", os.path.getsize("compressed1.txt.br") / 1024, "KB")
print("brotly w/ gcd:", os.path.getsize("compressed2.txt.br") / 1024, "KB")