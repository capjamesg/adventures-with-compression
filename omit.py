import os
import requests
import random
import time

SUPPORTED_DIFFICULTIES = {"easy": 0.95, "medium": 0.9, "hard": 0.7}

MIN_WORD_LEN = 4
DIFFICULTY = "medium"
WORDS_TO_GENERATE = 10

if not os.path.exists("count_1w.txt"):
    print("Downloading count_1w.txt...")
    url = "https://norvig.com/ngrams/count_1w.txt"
    r = requests.get(url, allow_redirects=True)
    open("count_1w.txt", "wb").write(r.content)

words = []
counts = []

with open("count_1w.txt", "r") as count_1w_file:
    for line in count_1w_file:
        word, count = line.split("\t")
        if len(word) > MIN_WORD_LEN:
            words.append(word)
            counts.append(int(count))

new_words = []

word_set = set(words)

median_count = sorted(counts)[int(len(counts) * SUPPORTED_DIFFICULTIES[DIFFICULTY])]

for i, count in enumerate(counts):
    if count > median_count:
        new_words.append(words[i])

words = new_words
correct = 0

start = time.time()

for i in range(WORDS_TO_GENERATE):
    wd = random.choice(words)

    random_letter = random.randint(0, len(wd) - 1)
    removed_letter = wd[random_letter].lower()

    wd = wd[:random_letter] + "_" + wd[random_letter + 1 :]

    guess = input(f"Guess the letter: {wd} ")

    if wd[:random_letter] + guess + wd[random_letter + 1 :] in word_set:
        print("Correct!")
        correct += 1
    else:
        print("Incorrect!")
        print("The correct word was: " + wd.replace("_", removed_letter))

end = time.time()

avg_time = (end - start) / 10

print("Your score:", correct)
print("Time taken:", end - start)
print("Avg time:", round(avg_time, 2))

exit()
