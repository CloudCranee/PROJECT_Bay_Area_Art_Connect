# python zipcode stripper
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from model import Zipcode 


def seed_zipcodes()
    file = open("non_server_files/raw_zipcodes.txt")
    text = file.read()
    file.close()
    words = text.split('>')
    shorter_list = []
    final_list = []

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

    for zip_code in final_list:
        new_zcode = Zipcode(valid_zipcode=zip_code)
        db.session.add(new_zcode)

    db.session.commit()



# instantiate Zipcode object
# add to db
# string_output = string_output + zip_code + "),\n("


# print(final_list)

# for zip_code in final_list:
#     string_output = string_output + zip_code + "),\n("


# bayzips=open("bayareazipcodes.txt",'w')
# bayzips.write(string_output)
# bayzips.close()