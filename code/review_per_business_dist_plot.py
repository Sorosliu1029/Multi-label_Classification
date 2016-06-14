import matplotlib.pyplot as plt
import json
from numpy import arange

cat_count = {}
with open('yelp_academic_dataset_business.json') as f:
    for line in f:
        bs = json.loads(line)
        for cat in bs['categories']:
            cat_count[cat] = cat_count.get(cat, 0) + 1

result = sorted(cat_count.items(), key=lambda t: t[1], reverse=True)

cat, cnt = zip(*result[:10])
review_cnt = {}
with open('yelp_academic_dataset_business.json') as f:
    for line in f:
        bs = json.loads(line)
        review_num = bs['review_count']
        for c in bs['categories']:
            if c in cat:
                review_cnt[c] = review_cnt.get(c, 0) + review_num

review_per_bs = [float(review_cnt[k]) / float(cat_count[k]) for k in cat]
print zip(cat, review_per_bs)

ind = arange(10)
width = 0.7
plt.bar(ind, review_per_bs, width, color='g')
plt.ylabel('Reviews per business')
plt.xticks(ind+width/2., cat, rotation=30)
plt.grid(color='b', linestyle='--')
plt.show()
