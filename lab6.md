# CS 179G Lab 6

This lab will show a few example programs to find word frequencies in a document. We consider lower case letters only.

- Input: Input file path.
- Output: A TSV (tab-separate-vector) file of word frequencies, in the format of <word, frequency>.

## Word Count by `HashTable`
Hash table provides *O(1)* average cost (linear in the worst case) for writing/querying data. It is usually an in-memory data structure which shall only be used for small sized data.
```python
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "r") as inf, open(output_file, "w") as outf:
    freqs = {}  # Python dict is implemented using hash table
    for line in inf:
        # Remove new line chars and leading/trailing spaces
        line = line.replace("\t", " ").rstrip("\n").rstrip("\n").strip()
        # For each none-empty word (split by space)
        for word in filter(None, line.lower().split(" ")):
            # Increment the count. If the word is first-time seen, initialize
            # it to 0 before incrementing
            freqs[word] = freqs.get(word, 0) + 1

    # We have scanned the whole file and obtained all unique word
    # frequencies
    for word in sorted(freqs.keys()):
        outf.write(f"{word}\t{freqs[word]}\n")
```

#### Memory usage analysis
Assume there are *W* unique words in total. All unique words have an average length of *4* characters (*4* bytes). On a 64-bit system, a key-value pair in the dictionary is *4 + 8 = 12* bytes. The counter variable is int64 type of *8* bytes.

The total memory needed for the dictionary is *12W* bytes.
| ***W***       | **Memory** |
|---------------|------------|
|         1,000 |   11.7 kB  |
|     1,000,000 |   11.4 MB  |
| 1,000,000,000 |   11.1 GB  |

## Word Count by `B-tree`
B-tree (B<sup>+</sup>-tree) is a disk based data structure that provides *O(log N)* write/read cost. Note here the cost is disk access cost, which is far more expensive than memory operations. Constant memory, *O(N log N)* total time.

```python
import os
import sqlite3
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "r") as inf, open(output_file, "w") as outf:
    if os.path.isfile("word_count.db"):
        os.remove("word_count.db")

    conn = sqlite3.connect("word_count.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE word_count "
                "(word TEXT PRIMARY KEY, freq UNSIGNED BIG INT);")
    conn.commit()

    for line in inf:
        # Remove new line chars and leading/trailing spaces
        line = line.replace("\t", " ").rstrip("\n").rstrip("\n").strip()
        # For each none-empty word (split by space)
        for word in filter(None, line.lower().split(" ")):
            res = cur.execute("SELECT freq FROM word_count WHERE word = ?;",
                              (word,)).fetchone()
            if res is None:
                # First-time seen this word
                cur.execute("INSERT INTO word_count VALUES (?, ?);", (word, 1))
            else:
                # Increment the frequency
                freq = int(res[0]) + 1
                cur.execute("UPDATE word_count SET freq = ? WHERE word = ?;",
                            (freq, word))

    # We have scanned the whole file and obtained all unique word frequencies
    cur.execute("SELECT word, freq FROM word_count ORDER BY word;")
    while True:
        rows = cur.fetchmany()
        if len(rows) == 0:
            break
        for row in rows:
            outf.write(f"{row[0]}\t{row[1]}\n")

    conn.close()
    os.remove("word_count.db")
```


## Word Count by `divide-and-conquer`
This is roughly what `MapReduce` does internally. Constant memory (depends on batch size), linear time. 

```python
import heapq
import os
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]
# Maximum size per batch in bytes
batch_size = int(sys.argv[3])


def save_tmp_results(freqs: dict, tmp_id: int) -> str:
    """ Save a temporary dict of word frequencies and return the file path. """
    tmp_path = f"tmp-{tmp_id}"
    with open(tmp_path, "w") as tmpf:
        for word in sorted(freqs.keys()):
            tmpf.write(f"{word}\t{freqs[word]}\n")
    return tmp_path


tmp_files = []

with open(input_file, "r") as inf:
    batch_freqs = {}
    cur_size = 0
    for line in inf:
        # Remove new line chars and leading/trailing spaces
        line = line.replace("\t", " ").rstrip("\n").rstrip("\n").strip()
        # For each none-empty word (split by space)
        for word in filter(None, line.lower().split(" ")):
            cur_freq = batch_freqs.get(word, 0)
            if cur_freq == 0:
                # current size + word length + 8 bytes counter
                if cur_size + len(word) + 8 > batch_size:
                    # Save temporary results
                    tmp_files.append(
                        save_tmp_results(batch_freqs, len(tmp_files)))
                    # Restart
                    batch_freqs.clear()
                    cur_size = 0
                cur_size += len(word) + 8
            # (Add and) increment
            batch_freqs[word] = cur_freq + 1

    if len(batch_freqs) > 0:
        tmp_files.append(save_tmp_results(batch_freqs, len(tmp_files)))
        batch_freqs.clear()
        cur_size = 0


# Merge word frequencies via a PriorityQueue (heapq)

def parse_line(line: str) -> tuple:
    t = line.rstrip("\n").split("\t")
    if len(t) == 2:
        return t[0], int(t[1])  # Word and frequency
    return None, 0


with open(output_file, "w") as outf:
    files = []
    pq = []
    for tmp_file in tmp_files:
        f = open(tmp_file, "r")
        word, freq = parse_line(f.readline())
        if word is None:
            f.close()
        else:
            pq.append((word, freq, len(files)))
            files.append(f)
    heapq.heapify(pq)

    cur_word = None
    cur_freq = 0
    while len(pq) > 0:
        word, freq, i = heapq.heappop(pq)
        if word != cur_word:
            if cur_word is not None:
                outf.write(f"{cur_word}\t{cur_freq}\n")  # Write final result
            cur_word = word
            cur_freq = freq
        else:
            cur_freq += freq  # Aggregate
        new_word, new_freq = parse_line(files[i].readline())
        if new_word is not None:
            heapq.heappush(pq, (new_word, new_freq, i))  # Add the next word
        else:
            files[i].close()

    if cur_word is not None:
        outf.write(f"{cur_word}\t{cur_freq}\n")  # Write the last final result

# Remove all temporary files
for tmp_file in tmp_files:
    os.remove(tmp_file)
```

## Examples Word Count usages
Language model, such as [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf), [BM25](https://en.wikipedia.org/wiki/Okapi_BM25).

1. To compute **tf**: Use MapReduce to compute all word frequencies;
2. To compute **idf**: Use MapReduce to compute the number of documents that contain the word, for each word in the vocabulary;
3. Inverted index: build separately;
4. Search: Use the inverted index to find relevant documents, use **tf-idf** for the ranking.

## Other usages of Spark
Parallel computing, e.g, multi-thread/process/nodes to compute the count/average/min/max, etc more efficiently than a single thread application.