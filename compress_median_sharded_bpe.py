import tqdm
import os

from pysurprisal import Surprisal
import subprocess
import struct
import transformers

def get_dataset(dataset: str = ""):
    if dataset == "enwik8":
    # open enwik8/enwik8
        with open("enwik8/enwik8", "r") as enwik8_file:
            text = enwik8_file.read()
    else:
        text = ""

        for filename in os.listdir("../../jamesg.blog/_posts"):
            with open("../../jamesg.blog/_posts/" + filename, "r") as post_file:
                try:
                    text += post_file.read()
                except UnicodeDecodeError:
                    print("UnicodeDecodeError on file", filename)
            
    return text

text = get_dataset("enwik8")

# save raw text into raw.txt
with open("raw.txt", "w+") as raw_file:
    raw_file.write(text)

print("Unique words in text:", len(set(text.split(" "))))

chunks = []

EPOCHS = None

i = 1

print("Calculating minimum epochs...")

# while EPOCHS is None:
#     # print(i)
#     chunk_size = len(text) // i

#     # print("Chunk size:", chunk_size)

#     unique_words_in_chunk = len(set(text[chunk_size : chunk_size * 2].split(" ")))

#     # print("Unique words in chunk:", unique_words_in_chunk)

#     # if unique_words_in_chunk > 999, stop here
#     if unique_words_in_chunk < 900 or unique_words_in_chunk > 1000:
#         # print("ERROR: Unique words in chunk > 999 at chunk size", i)
#         i += 10
#         continue
    
#     EPOCHS = i

# set epochs so that no chunk is more than 200000 words
EPOCHS = 1
chunk_size = len(text) // EPOCHS

# get first 500 chunks
# chunks = chunks[:500]

# concat_text = ""

# master_dictionary = {}
# word_counts_per_epoch = {}

# text = " ".join(text.split(" "))
# data = Surprisal(text)
# surprisals = data.calculate_surprisals()

# # Sort words by surprisal
# least_surprising = [
#     word for word in sorted(surprisals, key=surprisals.get)
# ]

# compressed = []
# word_to_quantized = {}
# quantized_to_word = {}

# # Reserve lower quantized values for least surprising words
# for index, word in enumerate(least_surprising):
#     word_to_quantized[word] = index + 1  # Start from 1
#     quantized_to_word[index + 1] = word

# quantized_index = len(least_surprising) + 1

# for word in text.split(" "):
#     if word not in word_to_quantized:
#         quantized_index += 1
#         word_to_quantized[word] = quantized_index
#         quantized_to_word[quantized_index] = word
#     compressed.append(int(word_to_quantized[word]))

#     # print("Concat text:", concat_text)

# master_dictionary = quantized_to_word

# tokenize with OpenAIGPTTokenizerFast
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

tokenizer = Tokenizer(BPE())

tokenizer.pre_tokenizer = Whitespace()

print("Training tokenizer")

trainer = BpeTrainer(special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"])
tokenizer.train(files=["raw.txt"], trainer=trainer)
print("Trained tokenizer")

print("Tokenizing text")
# print(tokenizer.encode(text))

# tokenize text
# split text into chunks of 512
chunk_size = 512

# tokenized_text = ""

# for i in tqdm.tqdm(range(0, len(text), chunk_size), total=len(text) // chunk_size):
#     tokenized_text += " ".join(tokenizer.tokenize(text[i : i + chunk_size])) + " "

# print("Tokenized text:", len(tokenized_text))

compressed = tokenizer.encode_batch(text.split(". "))
compressed = [value.ids for value in compressed]
# concate
compressed = [value for sublist in compressed for value in sublist]

# add all words ot tokenizer if not in there
# vocab = set(tokenizer.get_vocab())

# set_tokenized = set(tokenized_text.split(" "))

# for word in tqdm.tqdm(set_tokenized, total=len(set_tokenized), desc="Adding words to tokenizer"):
#     if word not in vocab:
#         tokenizer.add_tokens([word])

# # map each word to a quantized value
# for word in tqdm.tqdm(tokenized_text, total=len(tokenized_text), desc="Mapping words to quantized values"):
#     compressed.append(tokenizer.convert_tokens_to_ids([word])[0])

# create chunks
chunks = []

for i in tqdm.tqdm(range(0, len(compressed), chunk_size), total=len(compressed) // chunk_size):
    chunks.append(compressed[i : i + chunk_size])

concat_text = ""

for i, text in tqdm.tqdm(enumerate(chunks), total=len(chunks)):
    if len(text) == 0:
        continue

    median_compressed = sorted(text)[len(text) // 2]

    # map each value so everything is offset from median
    compressed = [int(value) - median_compressed for value in text]
    
    # print("Median compressed:", median_compressed)

    compressed.append(median_compressed)

    # exit()

    concat_text += " ".join(map(str, compressed)) + " | "

# save concat text to a file
with open("compressed_concat1.txt", "w+") as compressed_file:
    compressed_file.write(concat_text)


# exit()

# exit()

chunk_len = len(chunks)

# del text
# del compressed
# del word_to_quantized
# del quantized_to_word

# save dictionary from tokenizer
with open("dictionary.txt", "w+") as dictionary_file:
    dictionary_file.write(" ".join(tokenizer.get_vocab()))
    
# print(concat_text.strip().split(" |")[0][100:1000])

# exit()

with open("compressed_concat.txt", "wb") as compressed_file:
    # save as struct
    for shard in tqdm.tqdm(concat_text.strip().split(" | "), total=len(concat_text.strip().split(" | "))):
        shard = shard.strip()
        # remove |
        shard = shard.split(" ")
        shard = [int(value) for value in shard if value != "" and value != "|"]

        compressed_file.write(struct.pack("i" * len(shard), *shard))

with open("compressed_concat.txt", "rb") as compressed_file:
    compressed_text = compressed_file.read()

print("Compressing concatenated text with brotli")

subprocess.run(
    ["brotli", "-fk", "compressed_concat.txt"]
)

# exit()

print("Compressed reverse mappings with brotli")

subprocess.run(
    ["brotli", "-fk", "dictionary.txt"]
)

print("Size of compressed text and dictionary in MB: ")
print(
    "Compressed text:",
    round(os.path.getsize("compressed_concat.txt.br") / 1024 / 1024, 2),
    "MB",
)
print(
    "Compressed dictionary:",
    round(os.path.getsize("dictionary.txt.br") / 1024 / 1024, 2),
    "MB",
)

# open with sturct
with open("compressed_concat.txt", "r") as compressed_file:
    compressed_text = compressed_file.read()

compressed_text = compressed_text.strip().split(" | ")

result = ""

special_tokens = ["</w>", "<unk>", "<pad>"]

for shard in tqdm.tqdm(compressed_text, total=len(compressed_text)):
    # if -1 in shard:
    shard = [int(value) for value in shard.split(" ") if value.strip() != "" and value.strip() != "|"]

    median = shard[-1]

    shard = shard[:-1]

    shard = [value + median for value in shard]

    # print(shard)

    shard = tokenizer.convert_ids_to_tokens(shard)

    for word in shard:
        result += word

# remove special tokens from result
for token in special_tokens:
    result = result.replace(token, "")

print("Result:", result)

exit()

decompressed_text = ""

for i, shard in tqdm.tqdm(enumerate(compressed_text.strip().split(b" | ")), total=len(compressed_text.strip().split(b" | "))):
    decompressed_text_in_shard = ""

    for value in shard.strip().split(b" "):
        value = int(value)

        # stop at 500 epoch
        if i >= 500:
            break
        
        # Use reverse mapping to directly find the word
        if len(reverse_mappings) <= i:
            print("ERROR: Reverse mapping not found for epoch", i)
            continue

        if value in reverse_mappings[i]:
            word = reverse_mappings[i][value]
            decompressed_text_in_shard += word + " "
        else:
            print(f"ERROR: Value {value} not found in reverse mapping for epoch {i}")

    decompressed_text += decompressed_text_in_shard

    print("Decompressed text in shard", i, ":", decompressed_text_in_shard)

print("Decompressed text:", decompressed_text)

# check equivalence
decompressed_length = len(decompressed_text)
print("Equivalence:", text[:decompressed_length] == decompressed_text)

# save to decompressed_concat.txt
with open("decompressed_concat.txt", "w") as decompressed_file:
    decompressed_file.write(decompressed_text)
