import sqlite3

conn = sqlite3.connect("my_database.db")

# Create car_parkings table
conn.execute('''CREATE TABLE car_parkings
         (car_identity   TEXT PRIMARY KEY  NOT NULL,
         arrival_time   DATETIME     NOT NULL,
         leaving_time   DATETIME     NULL,
         frequent_parking_number     INT NULL,
         is_valid_fpn        BIT DEFAULT 0 NOT NULL);''')
print("Created car_parkings table successfully...")

# Create parking_histories table
conn.execute('''CREATE TABLE parking_histories
         (id INTEGER PRIMARY KEY  AUTOINCREMENT,
         car_identity   TEXT    NOT NULL,
         arrival_time   DATETIME     NOT NULL,
         leaving_time   DATETIME     NULL,
         frequent_parking_number     INT NULL,
         is_valid_fpn        BIT DEFAULT 0 NOT NULL,
         parking_fee          DECIMAL NOT NULL);''')

print("Created parking_histories table successfully...")

# Create payment_balances table
conn.execute('''CREATE TABLE payment_balances
         (car_identity   TEXT PRIMARY KEY  NOT NULL,
          available_credit DECIMAL NOT NULL DEFAULT 0.00);''')

print("Created payment_balances table successfully...")
conn.close()