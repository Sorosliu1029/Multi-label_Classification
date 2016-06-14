import matplotlib.pyplot as plt
from numpy import arange
import json
cat_count = {}
with open('yelp_academic_dataset_business.json') as f:
    for line in f:
        bs = json.loads(line)
        for cat in bs['categories']:
            cat_count[cat] = cat_count.get(cat, 0) + 1

print len(cat_count.keys())
result = sorted(cat_count.items(), key=lambda t: t[1], reverse=True)

cat, cnt = zip(*result[:10])
print zip(cat, cnt)
explode = [0.05, 0, 0.05] + [0]*(len(cat)-3)
colors = ('r','g','#6DB3FC', 'c', 'm','y', 'w', '#A97946','#FF9224','#922890')
plt.pie(cnt, explode=explode, labels=cat, labeldistance=1.1,
        startangle=90, autopct='%3.1f%%', pctdistance=0.6, colors=colors)
plt.axis('equal')
plt.show()
