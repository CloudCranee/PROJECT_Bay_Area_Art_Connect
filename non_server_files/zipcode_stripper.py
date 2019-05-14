# python zipcode stripper


file = open("raw_zipcodes.txt")
text = file.read()
file.close()

words = text.split('>')

print(type(words))

shorter_list = []

print(words)

for word in words:
    try:
        to_add = word[0].isdigit()  
    except:
        to_add = False
    if to_add:
        shorter_list.append(word[:5])

print(shorter_list)