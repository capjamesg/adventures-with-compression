# jzip, capjamesg 2023

# This file represents ~3 hours of explorations into compression.
# I had an idea: could I use word surprisals (entropy) to compress text?
# I wanted the output to be a series of numbers that I could unquantize.
# This was not possible, however; there would be too many collisions.
# I ended up with lossy text compression, not ideal.
# Then, I decided to use surprisals to assign numbers to common words
# and then use those numbers to compress the text.
# Other numbers were assigned sequentially in order of appearance in a document.
# Thus, the algorithm is sensitive to the distribution of text.
# If the start of a document talks about one topic and the entire rest of the document
# uses a different vocabulary, the algorithm will not compress less well than
# a document that uses a consistent same vocabulary throughout.

# The result is informally called "jzip" (jameszip)

# In this script, I assign every word a number in my posts. There is a lookup table
# that maps numbers to words. Then, I compress the text using the numbers.

# The algorithm is as follows:
# 1. Read in all of my blog posts
# 2. Calculate surprisals for each word
# 3. Sort words by surprisal
# 4. Assign the first 50 words to the first 50 numbers
# 5. Assign the rest of the words sequentially
# 6. Compress the text using the assigned numbers
# 7. Write the dictionary, compressed text, and original text to files
# 8. Gzip the dictionary and compressed text

# To decompress:

# 1. Read in the dictionary and compressed text
# 2. Decompress the compressed text using the dictionary as a lookup table
# 3. Write the decompressed text to a file

# jzip (followed by gzip) achieved a compression ratio of 0.296 on my blog posts
# gzip achieved a compression ratio of 0.356 on my blog posts

from pysurprisal import Surprisal
import os
import string
import subprocess
import cProfile

# these functions aren't used
# but were used in a previous iteration of this project
# I was aiming to make the numbers quantized to 8 bits
# So that I could encode _both_ words and their surprisals
def preprocess_text(raw_text):
    return raw_text.translate(str.maketrans("", "", string.punctuation))


def quantize(x, max_val, bits):
    return int(round((x / max_val) * (2**bits - 1)))


def dequantize(x, max_val, bits):
    return (x / (2**bits - 1)) * max_val


def main():
    import time

    start = time.time()

    text = ""
    # open all posts in ../../jamesg.blog/_posts
    for filename in os.listdir("../../jamesg.blog/_posts"):
        with open("../../jamesg.blog/_posts/" + filename, "r") as post_file:
            try:
                text += post_file.read()
            except UnicodeDecodeError:
                print("UnicodeDecodeError on file", filename)
    # open enwik8/enwik8
    # with open("enwik8/enwik8", "r") as enwik8_file:
    #     text = enwik8_file.read()

    # # open 2148716 char
    # print(text[2148716:2148716+200])
    # with open("decompressed.txt", "r") as enwik8_file:
    #     text = enwik8_file.read()

    # # open 2148716 char
    #     print()
    # print(text[2148716:2148716+200])
    # exit()

    # 15284944	

    # 03267447
    # 24616488
    
    # 03267459
    # 24557463

    processed_text = text

    data = Surprisal(processed_text)
    surprisals = data.calculate_surprisals()

    # Sort words by surprisal, filter by length > 4
    least_surprising = [
        word for word in sorted(surprisals, key=surprisals.get) if len(word) > 4
    ][:100]

    print("Least surprising:", least_surprising)

    # use counts for least surprising in data.counts
    # least_surprising = [word for word in sorted(data.counts, key=data.counts.get) if len(word) > 4][:50]

    # max_abs_surprisal = max(map(abs, surprisals.values()))

    compressed = []
    word_to_quantized = {}
    quantized_to_word = {}

    # Reserve lower quantized values for least surprising words
    for index, word in enumerate(least_surprising):
        word_to_quantized[word] = index + 1  # Start from 1
        quantized_to_word[index + 1] = word

    quantized_index = len(least_surprising) + 1

    for word in processed_text.split(" "):
        if word not in word_to_quantized:
            quantized_index += 1
            word_to_quantized[word] = quantized_index
            quantized_to_word[quantized_index] = word
        compressed.append(word_to_quantized[word])

    # train a cnn on compressed to predict next word
    # dataset is lists of 10 words, predict 11th
        
    # predict next word for each word

    print("Index for 'coffee':", word_to_quantized["coffee"])

    with open("dictionary.txt", "w") as dict_file:
        # order by index
        dict_file.write(" ".join(map(str, quantized_to_word.keys())))

    # save numbers in compressed1.txt
    with open("compressed1.txt", "w") as compressed_file:
        compressed_file.write(" ".join(map(str, compressed)))

    print("Compressed size:", os.path.getsize("compressed1.txt"))

    with open("compressed.txt", "wb") as compressed_file:
        import struct
        binary_data = b''.join([struct.pack('H', quantized) if quantized < 2**16 else struct.pack('I', quantized) for quantized in compressed]) 

        # turn into bytearray
        binary_data = bytearray(binary_data)

        compressed_file.write(binary_data)

    print("Compressed size:", os.path.getsize("compressed.txt"))

    with open("original_text.txt", "w") as original_file:
        original_file.write(text)

    # subprocess.run(["brotli", "-fk", "dictionary.txt"])
    # subprocess.run(["brotli", "-fk", "compressed.txt"])

    with open("dictionary.txt", "r") as dict_file:
        quantized_to_word = dict(
            zip(map(int, dict_file.read().split(" ")), quantized_to_word.values())
        )

    with open("compressed.txt", "rb") as compressed_file:
        compressed = []
        import struct

        while True:
            try:
                # try read with H and I
                quantized = struct.unpack("H", compressed_file.read(2))[0]
                if quantized >= 2**16:
                    quantized = struct.unpack("I", compressed_file.read(4))[0]
                compressed.append(quantized)
            except:
                break

    end = time.time()

    print("Time taken:", round(end - start, 3), "seconds")

    decompressed_text = " ".join(
        [quantized_to_word.get(quantized, str(quantized)) for quantized in compressed]
    )

    subprocess.run(["brotli", "-fk", "original_text.txt"])

    with open("decompressed.txt", "w") as decompressed_file:
        decompressed_file.write(decompressed_text)

    print("Original size:", os.path.getsize("original_text.txt.br"))

    print(
        "jzip size:",
        os.path.getsize("compressed.txt.br") + os.path.getsize("dictionary.txt.br"),
    )
    print("Dictionary size:", os.path.getsize("dictionary.txt.br"))
    print("Decompressed size:", os.path.getsize("decompressed.txt"))

    print(
        "Compressed to decompressed:",
        round(
            os.path.getsize("compressed.txt.br")
            / os.path.getsize("decompressed.txt")
            * 100,
            3,
        ),
        "%",
    )

    compressed_size = os.path.getsize("compressed.txt.br") + os.path.getsize(
        "dictionary.txt.br"
    )
    original_size = os.path.getsize("original_text.txt.br")

    print("jzip size in MB (after gzip):", round(compressed_size / 1000000, 3), "MB")
    print("gzip size in MB:", round(original_size / 1000000, 3), "MB")

    print(
        "Before gzip jzip size:",
        round(
            (os.path.getsize("compressed.txt") + os.path.getsize("dictionary.txt"))
            / 1000000,
            3,
        ),
        "MB",
    )
    print(
        "Before gzip original size:",
        round(os.path.getsize("original_text.txt") / 1000000, 3),
        "MB",
    )

    print("Original == Decompressed:", text == decompressed_text)

    print(
        "jzip compression ratio:",
        round(compressed_size / os.path.getsize("original_text.txt"), 3),
    )
    print(
        "gzip compression ratio:",
        round(
            os.path.getsize("original_text.txt.br")
            / os.path.getsize("original_text.txt"),
            3,
        ),
    )


# cProfile.run('main()', 'profile.txt')

main()
