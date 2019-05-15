# python zipcode stripper.

from flask_sqlalchemy import SQLAlchemy

from model import Zipcode 

file = open("non_server_files/raw_zipcodes.txt")
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

# string_output = "("

# This code will seed all zipcodes into the bayart database.

for zip_code in final_list:
    new_zcode = Zipcode(valid_zipcode=zip_code)
    db.session.add(new_zcode)

    # instantiate Zipcode object
    # add to db
    # string_output = string_output + zip_code + "),\n("

db.session.commit()
# commit to db

# bayzips=open("bayareazipcodes.txt",'w')
# bayzips.write(string_output)
# bayzips.close()