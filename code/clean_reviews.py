import re
import nltk

FILTERED_WORDS = ('.', ',', '!', '?', '$', ':')

def clean_text(text):
    result = re.sub('[\'\"]+', '', text.lower())
    result = re.sub('[\.]+', '.', result)
    result = re.sub('[\,]+', ',', result)
    result = re.sub('[\!]+', '!', result)
    result = re.sub('[\?]+', '?', result)
    result = re.sub('[\$]+', '$', result)
    result = re.sub('[:]+', ':', result)
    return result

def extract_unigrams(text):
    tokens = nltk.wordpunct_tokenize(clean_text(text))
    tokens = [token for token in tokens
                if token not in FILTERED_WORDS]
    return tokens


def extract_bigrams(text):
    tokens = nltk.wordpunct_tokenize(clean_text(text))
    bgm = nltk.collocations.BigramAssocMeasures()
    finder = nltk.collocations.BigramCollocationFinder.from_words(tokens)
    finder.apply_word_filter(lambda w: w in FILTERED_WORDS)
    scored_bigrams = finder.score_ngrams(bgm.raw_freq)
    return ['_'.join(one_scored_bigram[0]) for one_scored_bigram in scored_bigrams]


def extract_trigrams(text):
    tokens = nltk.wordpunct_tokenize(clean_text(text))
    bgm = nltk.collocations.TrigramAssocMeasures()
    finder = nltk.collocations.TrigramCollocationFinder.from_words(tokens)
    finder.apply_word_filter(lambda w: w in FILTERED_WORDS)
    scored_trigrams = finder.score_ngrams(bgm.raw_freq)
    return ['_'.join(one_scored_trigram[0]) for one_scored_trigram in scored_trigrams]
