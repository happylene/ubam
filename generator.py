import csv
import os
from datetime import date

today = date.today().strftime("%m_%d_%Y")

folder_name = './lists/'
lists = os.listdir(folder_name)

# The expected headers from imported csv files
isbn_key = "ISBN"
name_key = "Name"
price_key = "Price"
qty_key = "Quantity"
total_key = "Total Price"
csv_header = [isbn_key, name_key, price_key, qty_key, total_key]

# {ISBN: {Name, Price, Quantity, TotalPrice, FileName}}
# Use FileName to identify the buyer
# e.g. { '12345': {'name': '', 'price': '', qty_key: 0, total_key: '', 'someone': '1', 'someone_else': '1'}}
parsed_list = {}

# buyers list
buyers = []

def get_buyer_name(list):
    return list[:-4]

def generate_dict(row, list):
    isbn = row[0]
    name = row[1]
    price = float(row[2].strip()[1:])
    qty = int(row[3].strip())
    total = float(row[4].strip()[1:])
    buyer_name = get_buyer_name(list)

    if isbn in parsed_list:
        # combine qty from all the buyers
        prev_qty = parsed_list[isbn][qty_key]
        parsed_list[isbn][qty_key] = prev_qty + qty

        # combine total from all the buyers
        prev_total = parsed_list[isbn][total_key]
        parsed_list[isbn][total_key] = prev_total + total

        # total qty of this particular buyer
        parsed_list[isbn][buyer_name] = qty
        # total of this particular buyer
        parsed_list[isbn][buyer_name+"_total"] = total
    else:
        new_list = {}
        new_list[name_key] = name
        new_list[price_key] = price
        new_list[qty_key] = qty
        new_list[total_key] = total
        new_list[buyer_name] = qty
        new_list[buyer_name+"_total"] = total
        parsed_list[isbn] = new_list


def parseList(list):
    with open(folder_name + list) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        # add current buyer to the buyers list
        update_buyers(get_buyer_name(list))

        line_count = 0
        #csv file format: ISBN,Name,Price,Quantity,Total Price
        for row in csv_reader:
			# header row
            if line_count == 0:
                valid_header = (row == csv_header)
				# check whether the csv file has the correct header,
				# and throw error and exit if not
                if not valid_header:
                    raise Exception("invalid header for file " + list)
                line_count += 1
            else:
                generate_dict(row, list)
                line_count += 1

def generate_final_list_field_names():
    new_header = csv_header.copy()
    new_header += buyers
    new_header += map(lambda str: str + "_total", buyers)
    return new_header
    
def generate_combined_list(new_list, additional_numbers):
    print("list size is ", len(new_list))
    fieldnames = generate_final_list_field_names()

    print("###### starting to write to the combined list ######")

    # additional_numbers = [total_qty, total_price, buyer_total_qty_dict, buyers_total_dict]

    with open(today+'_book_list.csv', mode='w') as book_list_file:
        writer = csv.DictWriter(book_list_file, fieldnames = fieldnames)
        print(fieldnames)
        writer.writeheader()
        writer.writerows(new_list)
        print(additional_numbers[0])
        print(additional_numbers[1])
        print(additional_numbers[2])
        print(additional_numbers[3])
        final_row = {}
        final_row[qty_key] = additional_numbers[0]
        final_row[total_key] = additional_numbers[1]
        for buyer in additional_numbers[2]:
            final_row[buyer] = additional_numbers[2][buyer]
        for buyer in additional_numbers[3]:
            final_row[buyer+"_total"] = additional_numbers[3][buyer]

        writer.writerow(final_row)


def update_buyers(buyer):
	buyers.append(buyer)

def convert_dict_to_list(parsed_list):
    new_list = []
    print("#### convert dict to list #####")
    for isbn in parsed_list:
        new_dict = parsed_list[isbn]
        new_dict[isbn_key] = isbn
        for buyer in buyers:
            if buyer not in new_dict:
                new_dict[buyer] = 0
                new_dict[buyer+"_total"] = 0
        print(new_dict)
        new_list.append(new_dict)
    print("#### end of converting ####")
    return new_list

def calc_list(new_list):
    total_qty = 0
    total_price = 0
    buyer_total_qty_dict = {}
    buyers_total_dict = {}
    for row in new_list:
        total_qty += row[qty_key]
        total_price += row[total_key]
        for buyer in buyers:
            if buyer in buyer_total_qty_dict:
                buyer_total_qty = buyer_total_qty_dict[buyer]
                buyer_total_qty_dict[buyer] = buyer_total_qty + row[buyer]
            else:
                buyer_total_qty_dict[buyer] = row[buyer]

            if buyer in buyers_total_dict:
                buyer_total = buyers_total_dict[buyer]
                buyers_total_dict[buyer] = row[buyer+"_total"] + buyer_total
            else:
                buyers_total_dict[buyer] = row[buyer+"_total"]
    print(total_qty)
    print(total_price)
    print(buyer_total_qty_dict)
    print(buyers_total_dict)
    return [total_qty, total_price, buyer_total_qty_dict, buyers_total_dict]

# main
for list in lists:
    if list.endswith(".csv"):
        parseList(list)
new_list = (convert_dict_to_list(parsed_list))
additional_numbers = calc_list(new_list)

generate_combined_list(new_list, additional_numbers)
