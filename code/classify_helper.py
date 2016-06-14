import scipy as sp

def get_labels(label_marks):
    all_labels = ['IsFoodGood', 'IsServiceGood', 'IsAmbianceGood', 'IsDealsGood', 'IsPriceGood']
    if len(all_labels) != len(label_marks):
        print "Error: length is unequal"
        return None
    results = set()
    for i in range(len(label_marks)):
        if label_marks[i] == 1:
            results.add(all_labels[i])
    return results

def report_precision_and_recall(expected, actual, algorithm):
    precision = 0.0
    recall = 0.0
    for i in xrange(len(expected)):
        expected_label_marks = expected[i]
        actual_label_marks = actual[i]
        expected_labels = get_labels(expected_label_marks)
        actual_labels = get_labels(actual_label_marks)
        correctly_predicted_labels = expected_labels.intersection(actual_labels)

        if len(actual_labels) > 0:
            precision += float(len(correctly_predicted_labels)) / float(len(actual_labels))
        if len(expected_labels) > 0:
            recall += float(len(correctly_predicted_labels)) / float(len(expected_labels))

    precision /= float(len(expected))
    recall /= float(len(expected))

    harmonic_mean = sp.stats.mstats.hmean([precision, recall])
    return {'algorithm': algorithm, 'precision': precision, 'recall': recall, 'harmonic mean': harmonic_mean}
