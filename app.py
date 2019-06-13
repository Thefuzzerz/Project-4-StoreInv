"""
Application for User to control inventory. Database is initially created with
existing CSV file. Database can be backed up to CSV file. Users can view,
edit and delete inventory as needed.
"""

import platform
import sys
import os
import csv
import datetime
from peewee import SqliteDatabase
from peewee import Model
from peewee import DecimalField, CharField, DateTimeField, IntegerField

#pylint: disable=C0103
db = SqliteDatabase('inventory.db')

class Product(Model):
    """ Model for Product in database. """
    product_name = CharField(max_length=255)
    product_quantity = IntegerField()
    product_price = DecimalField()
    product_date = DateTimeField()

    #pylint: disable=R0903
    class Meta:
        """ Peewee Meta Class. """
        database = db

def app():
    """ Main application function. """
    attempts = 0
    while True:
        clr_scr()
        app_header()
        if attempts > 0:
            print('\n' + '*'*8 + ' Invalid Selection Made ' + '*'*9 + '\n')
        menu_selection = menu()
        if menu_selection == 'v':
            select_prod = view_product()
            display_product(select_prod)
        if menu_selection == 'a':
            entry = add_product()
            if entry is None:
                app()
            else:
                db_entry(entry)
                app()
        if menu_selection == 'b':
            csv_backup()
            clr_scr()
            app_header()
            print('\n' + '='*8 + ' Database Backed to CSV ' + '='*8+ '\n'
                  '\n' + ' '*10 + 'Hit Enter to Continue')
            input()
        if menu_selection == 'i':
            view_db()
        attempts += 1

def csv_backup():
    """ Func writes all informatio in database to temp CSV file """
    query = Product.select()
    with open('backup.csv', 'x') as csvfile:
        fieldnames = ['product_name', 'product_price', 'product_quantity',
                      'date_updated']
        csvwriter = csv.DictWriter(csvfile, lineterminator='\n',
                                   fieldnames=fieldnames)
        csvwriter.writeheader()
        for product in query:
            date_format = product.product_date.strftime('%m/%d/%Y')
            csvwriter.writerow({'product_name': product.product_name,
                                'product_price': f'${product.product_price}',
                                'product_quantity': product.product_quantity,
                                'date_updated': date_format
                               })

def csv_import():
    """ Func to read CSV file into a variable return ass import_dict. """
    import_dict = []
    with open('inventory.csv', 'r', newline="") as csvfile:
        fieldnames = ['product_name', 'product_price', 'product_quantity',
                      'date_updated']
        workreader = csv.DictReader(csvfile, fieldnames=fieldnames)
        for row in workreader:
            if row['product_name'] == 'product_name':
                pass
            else:
                row['product_price'] = float(row['product_price'][1:])
                row['product_quantity'] = int(row['product_quantity'])
                row['product_date'] = datetime.datetime.strptime(
                    row['date_updated'], '%m/%d/%Y').date()
                import_dict.append(row)
    return import_dict

def db_update():
    """
    Func to check if database matches CSV file.
    If it finds a missing entry it creates it.
    """
    csv_data = csv_import()
    for item in csv_data:
        db_exists = Product.select().where(
            (Product.product_name == item['product_name']),
            (Product.product_price == item['product_price']),
            (Product.product_quantity == item['product_quantity']),
            (Product.product_date == item['product_date']))
        if db_exists.exists():
            pass
        else:
            Product.create(product_name=item['product_name'],
                           product_price=item['product_price'],
                           product_quantity=item['product_quantity'],
                           product_date=item['product_date']
                          )

def db_entry(entry):
    """ Func for adding a Product into the database. """
    Product.create(product_name=entry[0],
                   product_quantity=entry[1],
                   product_price=entry[2],
                   product_date=entry[3]
                  )
    clr_scr()
    app_header()
    print(f'\n{entry[0]} -- Added to Store Inventory -- Hit Enter to Continue')
    input()

def add_product():
    """ Function for reviewing and confirming addition to database. """
    new_product = product_info()
    clr_scr()
    print('*'*5 + ' Confirm Addition to Inventory ' + '*'*5 +
          f'\n\nProduct Name: {new_product[0]}'
          f'\nProduct Quantity: {new_product[1]}')
    print('Product Cost per Unit: ${}'.format(format(new_product[2], '.2f')))
    print('\n[Y]es or [N]o')
    while True:
        confirm = input()
        if confirm.lower() == 'y':
            return new_product
        elif confirm.lower() == 'n':
            return None
        else:
            print('Please Enter Y or N\n')

def update_product(choice, product):
    """ Func for updating a Product in database. """
    if choice == '1':
        clr_scr()
        app_header()
        print('Enter a the New Product Name:\n'
              'Enter [X] to Cancel')
        new_product_name = product_length_check()
        product.product_name = new_product_name
        product.save()
    elif choice == '2':
        clr_scr()
        app_header()
        print('Enter a the New Product Quantity:\n'
              'Enter [X] to Cancel')
        while True:
            new_product_qnty = positive_number()
            if '.' in str(new_product_qnty):
                print('Quantity Must be a Whole Number')
            else:
                product.product_quantity = new_product_qnty
                product.save()
                break
    elif choice == '3':
        clr_scr()
        app_header()
        print('Enter a the New Product Price (X.XX):\n'
              'Enter [X] to Cancel')
        new_product_price = positive_number()
        product.product_price = new_product_price
    new_product_date = datetime.datetime.now().date()
    product.product_date = new_product_date
    product.save()

def change_menu(product):
    """
    Func for viewing current Product and obtaining which value to change.
    """
    clr_scr()
    app_header()
    print(f'[1] -- Change Product Name: {product.product_name}\n'
          f'[2] -- Change Product Quantity: {product.product_quantity}\n'
          f'[3] -- Change Product Price: {product.product_price}\n'
         )
    choice = input('Select 1 - 3 -- Enter [X] to Exit\n')
    while True:
        if choice == 'x':
            return False
        elif choice in ('1', '2', '3'):
            clr_scr()
            app_header()
            update_product(choice, product)
            print(f'Updated [{product.product_name}] - Hit Enter to Exit')
            input()
            return False
        else:
            clr_scr()
            app_header()
            print(f'[1]-- Change Product Name: {product.product_name}\n'
                  f'[2]-- Change Product Quantity: {product.product_quantity}\n'
                  f'[3]-- Change Product Price: {product.product_price}\n'
                 )
            print('*'*8 + ' Invalid Selection ' + '*'*8)
            choice = input('Select 1 - 3 -- Enter [X] to Return\n')

def delete_product(product):
    """ Func for deleting database entry of Product passed into func. """
    product.delete_instance()

def positive_number():
    """ Function to check for valid number and allow exit. """
    while True:
        num = input()
        if len(num) > 5:
            print('Invalid Number')
        else:
            if num.lower() == 'x':
                app()
            try:
                if '.' in num:
                    num = float(num)
                    if num < 0:
                        raise ValueError()
                    else:
                        return num
                else:
                    num = int(num)
                    if num <= 0:
                        raise ValueError()
                    else:
                        return num
            except ValueError:
                print('Enter a Valid Number')

def product_length_check():
    """ Func for checkiing that user has entered a value. """
    while True:
        user_product_word = input()
        word_len = len(user_product_word)
        if word_len >= 1:
            if user_product_word.lower() == 'x':
                app()
            return user_product_word
        else:
            print('Product Must Have Name')

def product_info():
    """ Function to obtain new product information. """
    product_header()
    print('Product Name:')
    new_product_name = product_length_check()
    if new_product_name.lower() == 'x':
        app()
    product_header()
    print('Product Quantity:')
    while True:
        new_product_qnty = positive_number()
        if '.' in str(new_product_qnty):
            print('Quantity Must be a Whole Number')
        else:
            product_header()
            print('Product Price per Unit (X.XX):')
            new_product_price = positive_number()
            new_product_date = datetime.datetime.now().date()
            return(new_product_name, new_product_qnty, new_product_price,
                   new_product_date)


def view_db():
    """ Func for viewing current contents of database. """
    db_import = []
    for item in Product.select():
        entry = (item.product_name, item.product_quantity,
                 item.product_price, item.product_date.date(),
                 item.id)
        db_import.append(entry)
    def print_product_info(entry):
        """ Prints line for each item in variable entry. """
        for product in entry:
            print(f'ID [{product[4]}] - {product[0]}')
    def scroll_func(db_import):
        """ Func to scroll through db_import with user input. """
        index = 0
        db_len = len(db_import)
        while True:
            clr_scr()
            app_header()
            print('Hit Enter to Scroll Through Inventory\n'
                  'Enter ID # to View Product Details\n'
                  'Enter [P] to Scroll Up - Enter [X] to Return\n')
            entry = db_import[index:index+5]
            print_product_info(entry)
            choice = input()
            for item in db_import:
                if str(item[4]) == choice:
                    product = Product.get(Product.id == choice)
                    display_product(product)
            if isinstance(choice, int):
                choice = 'null'
                index = index
            if choice.lower() == '':
                if (index+5) > (db_len-1):
                    index = index
                else:
                    index += 1
            if choice.lower() == 'p':
                if index == 0:
                    index = 0
                else:
                    index -= 1
            if choice.lower() == 'x':
                app()

    scroll_func(db_import)

def product_header():
    """ Func for console header when adding Product. """
    clr_scr()
    app_header()
    print('Add New Product to Store Inventory - Enter [x] to exit\n')

def app_header():
    """ Function to print application header. """
    title = (' STORE INVENTORY DATABASE ')
    print(' '+'-'*40+'\n '+'*'*7+title+'*'*7+'\n '+'-'*40)

def menu():
    """ Func for Main menu selection. """
    print('[v] -- View Details of Product\n'
          '[a] -- Add a New Product\n'
          '[b] -- Backup Database to CSV\n'
          '[i] -- View Current Inventory\n'
          '[x] -- Exit Application\n'
          '\nPlease make a selection:')
    choice = input().lower()
    if choice == 'x':
        sys.exit()
    else:
        return choice

def display_product(select_prod):
    """ Func for displaying Product passed into func. """
    clr_scr()
    app_header()
    print('\n' + '='*12 + f' PRODUCT ID#: {select_prod.id} ' + '='*12 + '\n'
          f'\nProduct Name: {select_prod.product_name}\n'
          f'Quantity in Stock: {select_prod.product_quantity}\n'
          f'Price Per Unit: ${select_prod.product_price}\n'
          f'Date Added to Inventory: {select_prod.product_date.date()}\n'
         )
    print('\nHit Enter to Exit - [D] to Delete Entry - [C] - Change Value')
    while True:
        choice = input()
        if choice.lower() == 'd':
            delete_product(select_prod)
            clr_scr()
            app_header()
            print(f'\n{select_prod.product_name} Removed from Inventory')
            input('Hit Enter to Continue')
            break

        elif choice.lower() == 'c':
            change_menu(select_prod)
            break
        elif choice.lower() == '':
            break
        else:
            print('Enter a Valid Option')
    clr_scr()
    app()

def view_product():
    """ Console printout for viewing product. """
    attemps = 0
    clr_scr()
    while True:
        clr_scr()
        app_header()
        if attemps >= 1:
            print('No Product with Entered ID #\n')
        print('Enter Product ID -- Enter [x] to Exit')
        id_num = positive_number()
        try:
            select_prod = Product.get(Product.id == id_num)
            return select_prod
        #pylint: disable=W0702
        except:
            attemps += 1

def clr_scr():
    """
    Function to clear screen based on operating system.
    """
    user_sys = platform.system()
    if user_sys == 'Linux':
        os.system('clear')
    else:
        os.system('cls')

if __name__ == "__main__":
    db.connect()
    db.create_tables([Product], safe=True)
    db_update()
    app()
