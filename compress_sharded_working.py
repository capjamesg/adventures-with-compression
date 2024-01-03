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

# compressed_size = sum(
#     os.path.getsize(f"shards/compressed{i}.txt.br") for i in range(10000)
# )

# print("jzip size in MB (after brotli):", round(compressed_size / 1000000, 3), "MB")

# exit()

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

    text = ""
    # open all posts in ../../jamesg.blog/_posts
    # for filename in os.listdir("../../jamesg.blog/_posts"):
    #     with open("../../jamesg.blog/_posts/" + filename, "r") as post_file:
    #         try:
    #             text += post_file.read()
    #         except UnicodeDecodeError:
    #             print("UnicodeDecodeError on file", filename)
    # open enwik8/enwik8
    with open("enwik8/enwik8", "r") as enwik8_file:
        text = enwik8_file.read()

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

    # split into 5000 word chunks
    chunks = []

    chunk_size = len(processed_text) // 10000

    # get count of unique nums in second chunk
    print("Chunk size:", chunk_size)
    print("Unique words in chunk:", len(set(processed_text[chunk_size : chunk_size * 2].split(" "))))

    # exit()

    for i in range(10000):
        chunks.append(processed_text[i * chunk_size : (i + 1) * chunk_size])

    # get size of first 

    # calculate surprisals for each chunk
    import tqdm

    concat_text = ""
    concat_dict = ""

    master_dictionary = {}
    word_counts_per_epoch = {}

    # master dictionary will take the form of
    # {word: { epoch: value }}

    for i, processed_text in tqdm.tqdm(enumerate(chunks), total=len(chunks)):
        processed_text = " ".join(processed_text.split(" "))
        data = Surprisal(processed_text)
        surprisals = data.calculate_surprisals()

        # Sort words by surprisal, filter by length > 4
        least_surprising = [
            word for word in sorted(surprisals, key=surprisals.get) if len(word) > 4
        ][:100]

        # print("Least surprising:", least_surprising)

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

        # print("Index for 'coffee':", word_to_quantized["coffee"])

        with open(f"shards/dictionary{i}.txt", "w") as dict_file:
            # order by index
            dict_file.write(" ".join(map(str, quantized_to_word.keys())))

        # save numbers in compressed1.txt
        with open(f"shards/compressed{i}.txt", "w") as compressed_file:
            compressed_file.write(" ".join(map(str, compressed)))

        concat_text += " ".join(map(str, compressed)) + " | "
        # save dictionary as json string
        import json
        concat_dict += json.dumps(quantized_to_word) + " | "
        
        # add to master dict
        for word in quantized_to_word.values():
            if word not in master_dictionary:
                master_dictionary[word] = {}

            master_dictionary[word][i] = word_to_quantized[word]

        # add to word counts per epoch
        for word in quantized_to_word.values():
            if word not in word_counts_per_epoch:
                word_counts_per_epoch[word] = {}

            word_counts_per_epoch[word][i] = data.counts[word]

    # invert master dictionary so it takes the form of
    # {value: { epoch: word }}
            
    # use an ordered dict and use struct
    # {epoch: word}
    # where the index of the word is the value
    # the dictionary should be ordered by count of words in epoch
            
    new_master_dictionary = {}

    # use word count for insertion order
    for word in sorted(word_counts_per_epoch, key=lambda word: sum(word_counts_per_epoch[word].values()), reverse=True):
        new_master_dictionary[word] = {}

        for epoch in sorted(word_counts_per_epoch[word], key=word_counts_per_epoch[word].get, reverse=True):
            new_master_dictionary[word][epoch] = master_dictionary[word][epoch]
            
    master_dictionary = new_master_dictionary

    # print("Master dictionary:", new_master_dictionary)

    # exit()
    # consolidate dictionary so that if a word has the same value in all epochs, it is removed
    # this is because the value is the same in all epochs, so it is redundant

    # print("Master dictionary:", master_dictionary)
    
    with open("dictionary_concat.json", "w") as dict_file:
        # save master dictionary
        import json
        dict_file.write(json.dumps(master_dictionary))

    # save numbers in binary
    with open("compressed_concat.bin", "wb") as compressed_file:
        # save as bytestring
        import struct
        compressed_file.write(struct.pack("i" * len(compressed), *compressed))

    # represent dictionary as cbor
    with open("dictionary_concat.cbor", "wb") as dict_file:
        import cbor2

        dict_file.write(cbor2.dumps(master_dictionary))

    # open cbor
    with open("dictionary_concat.cbor", "rb") as dict_file:
        import cbor2

        master_dictionary = cbor2.loads(dict_file.read())

    print("writing concatenated files")

    subprocess.run(["brotli", "-fk", "dictionary_concat.cbor"])
    print("wrote dictionary")
    subprocess.run(["brotli", "-fk", "compressed_concat.bin"])
    print("wrote compressed")

    compressed_size = os.path.getsize("compressed_concat.bin.br") + os.path.getsize("dictionary_concat.cbor.br")

    # 12M compressed text, 30M compressed dictionary

    print("jzip size in MB (after brotli):", round(compressed_size / 1000000, 3), "MB")

    # reconstruct using | as shard indicator
    with open("compressed_concat.bin.br", "rb") as compressed_file:
        import struct

        compressed_text = struct.unpack("i" * (compressed_size // 4), compressed_file.read())

    with open("dictionary_concat.cbor", "rb") as dict_file:
        import cbor2

        master_dictionary = cbor2.loads(dict_file.read())

    # print("Master dictionary:", master_dictionary)

    # print("Dictionaries:", dictionaries_by_shard)

    reconstructed_text = ""

    # print(master_dictionary["coffee"])

    # exit()

    for i, shard in enumerate(compressed_text.split(" | ")):
        reconstructed_text += " ".join(
            master_dictionary[int(value)][i]
            for value in shard.strip().split(" ")
            if int(value) in master_dictionary
        )

    print("Reconstructed text:", reconstructed_text[:1000])

main()