import re
file_path = '/content/Election Query.txt'

with open(file_path, 'r') as file:
	file_content = ''
	line = file.readline()

	while line:
		file_content += line
		line = file.readline()
file_content=file_content.lower()
file_content=file_content[7:]
without_=file_content.replace("_", " ").replace('"','').replace("(",'').replace(')','').replace("'","")
# print(without_)
with open('/content/modified_query.txt','w') as file:
  file.write(without_)

with open('/content/modified_query.txt', 'r') as file:
  query = ''
  line = file.readline()

  while line:
    query += line
    line = file.readline()

def query_in_string(string):
    for term in query.split('or'):
        lst = map(str.strip, term.split('and'))
        if all(re.search(r"\b%s\b" % re.escape(word), string) for word in lst):
           print(term)
           print("The Query was found in STT result. This video/audio is about elections")
           return True
    print("The Query was not found in STT result.")
    return False

query_in_string(corrected_text)
