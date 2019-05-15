# python zipcode stripper


file = open("raw_zipcodes.txt")
text = file.read()
file.close()

words = text.split('>')

print(type(words))

shorter_list = []

final_list = []

print(words)

for word in words:
    try:
        to_add = word[0].isdigit()  
    except:
        to_add = False
    if to_add:
        shorter_list.append(word[:5])

for code in shorter_list:
    if code.isdigit():
        final_list.append(code)

string_output = "("

for zip_code in final_list:
    string_output = string_output + zip_code + "),\n("


bayzips=open("bayareazipcodes.txt",'w')
bayzips.write(string_output)
bayzips.close()