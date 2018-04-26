import os
import subprocess
from model.config import Config
from model.data_utils import CoNLLDataset, get_vocabs, UNK, NUM, \
    get_word2vec_vocab, write_vocab, load_vocab, get_char_vocab, \
    export_trimmed_word2vec_vectors, get_processing_word


def main():
    """Procedure to build data

    You MUST RUN this procedure. It iterates over the whole dataset (train,
    dev and test) and extract the vocabularies in terms of words, tags, and
    characters. Having built the vocabularies it writes them in a file. The
    writing of vocabulary in a file assigns an id (the line #) to each word.
    It then extract the relevant word2vec vectors and stores them in a np array
    such that the i-th entry corresponds to the i-th word in the vocabulary.


    Args:
        config: (instance of Config) has attributes like hyper-params...

    """
    # get config and processing of words

    config = Config(load=False)
    processing_word = get_processing_word(lowercase=False)

    # Generators
    dev   = CoNLLDataset(config.filename_dev, processing_word)
    test  = CoNLLDataset(config.filename_test, processing_word)
    train = CoNLLDataset(config.filename_train, processing_word)

    # Build Word and Tag vocab
    vocab_words, vocab_tags = get_vocabs([train, dev, test])
    vocab_word2vec2 = get_word2vec_vocab(config.filename_word2vec2)

    #vocab = vocab_words & vocab_word2vec
    vocab = vocab_words
    vocab.add(UNK)
    vocab.add(NUM)

    # Save vocab
    write_vocab(vocab, config.filename_words)
    write_vocab(vocab_tags, config.filename_tags)

    # Trim word2vec Vectors
    abs_f_words = os.path.abspath(config.filename_words)
    abs_f_vec = os.path.abspath(config.filename_word2vec)
    cmd = '/home/emre/programs/fastText-0.1.0/fasttext print-word-vectors /home/emre/embeddings/fasttext.bin ' \
          '< {} > {}'.format(abs_f_words, abs_f_vec)
    subprocess.check_call(cmd, shell=True)
    vocab = load_vocab(config.filename_words)
    export_trimmed_word2vec_vectors(vocab, config.filename_word2vec,
                                    config.filename_trimmed, config.dim_word)

    vocab = vocab & vocab_word2vec2
    vocab.add(UNK)
    vocab.add(NUM)
    export_trimmed_word2vec_vectors(vocab, config.filename_word2vec2,
                                    config.filename_trimmed2, config.dim_word)

    # Build and save char vocab
    train = CoNLLDataset(config.filename_train)
    vocab_chars = get_char_vocab(train)
    write_vocab(vocab_chars, config.filename_chars)


if __name__ == "__main__":
    main()
