def predict(text):
    valid_pos_tags = {'NOUN', 'NUM', 'NOUN,EZ', 'ADJ', 'NUM,EZ'}
    extractor = TopicRank(valid_pos_tags=valid_pos_tags)
    extractor.load_text(input=text, word_normalization_method=None)
    extractor.select_candidates()
    extractor.weight_candidates(threshold=0.5, metric='jaccard', linkage_method='average')
    keyphrases = extractor.get_n_best(n=20)
    score = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    keywords = []
    for i, (keyphrase, weight) in enumerate(keyphrases):
        keywords.append(keyphrase)
    dict_score = {score[i]: keywords[i] for i in range(len(keywords))}
    sorted_dict = dict(sorted(dict_score.items()))
    for i in range(0, 10):
        print(f'{i + 1}. \t{sorted_dict[20 - i]}')
    return sorted_dict
