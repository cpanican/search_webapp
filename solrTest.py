import solr
import os

# Create connection to a solr server
s = solr.SolrConnection('http://localhost:8983/solr/testcore')
os.system("solr start")
# os.system("solr create -c testcore")


s.add(_commit=True, id="1", word="heart")
s.add(_commit=True, id="2", word="cardio")
s.add(_commit=True, id="3", word="cardiac")


test = s.query('heart')
test.results

y = []
for x in test.results:
    y.append(x["word"][0])
y.append('cardiac')
print(y)




query = 'SELECT * FROM umls_label WHERE '
for i in y:
    if i == y[-1]:
        temp = "(SIDE_EFFECT NAME LIKE '%{}%') ".format(i)
    else:
        temp = "(SIDE_EFFECT NAME LIKE '%{}%') ".format(i) + "OR "
    query = query + temp


print(query)