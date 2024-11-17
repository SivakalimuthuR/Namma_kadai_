# Flask Inventory Management System

This is a Flask-based Inventory Management System where users can manage their company's items, purchases, and sales. The application allows for basic operations such as adding and editing items, making purchases and sales, and viewing reports of recent transactions.

## Features

- **Home Dashboard**: Displays the current cash balance and a list of items in the inventory.
- **Item Management**: Allows users to add new items, edit existing items, and delete items from the inventory.
- **Purchase Management**: Allows users to record purchases, update inventory, and deduct from the company's cash balance.
- **Sale Management**: Allows users to record sales, update inventory, and add to the company's cash balance.
- **Report Viewing**: Provides paginated views of purchase and sale transactions.
  
## Tech Stack

- **Flask**: Web framework for building the app.
- **Flask-SQLAlchemy**: ORM for managing the database and models.
- **Flask-WTF**: Form handling and CSRF protection.
- **SQLAlchemy**: ORM for database management.
- **Bootstrap**: CSS framework for responsive design (for front-end styling).
  
## Setup and Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.x
- pip (Python's package installer)

### Steps to Set Up

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/inventory-management-system.git
   cd inventory-management-system
Create and activate a virtual environment:

bash
Copy code
python3 -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Set up your environment variables (optional but recommended for production):

Create a .env file in the root of the project and add the following:

makefile
Copy code
FLASK_APP=app.py
FLASK_ENV=development
Initialize the database:

bash
Copy code
flask shell
Inside the shell, run the following to create the database tables:

python
Copy code
from app import db
db.create_all()
Run the application:

bash
Copy code
flask run
The application should now be running at http://127.0.0.1:5000/.

Endpoints
Home
GET / - Displays the home dashboard with the current balance and item list.
Item Management
GET /add_item - Displays a form to add a new item and a list of existing items.
POST /add_item - Handles form submission to add a new item to the inventory.
POST /delete_item/<int:item_id> - Deletes the specified item from the inventory.
POST /edit_item/<int:item_id> - Edits the details of the specified item.
Purchase Management
GET /purchase/add - Displays the form to add new purchases.
POST /purchase/add - Handles form submission for making purchases, updating the stock, and deducting from the balance.
Sale Management
GET /add_sale - Displays the form to add new sales.
POST /add_sale - Handles form submission for making sales, updating the stock, and adding to the balance.
Reports
GET /view_reports - Displays the paginated list of purchases and sales for the company.
Database Models
Company
Stores information about the company:

id: Primary Key
name: Name of the company (Unique)
cash_balance: Cash balance of the company (default: 1000.0)
Item
Stores information about items in the inventory:

id: Primary Key
name: Name of the item (Unique)
price: Price per unit of the item
qty: Quantity of the item in stock
Purchase
Stores purchase transactions:

id: Primary Key
timestamp: Timestamp of the purchase
item_id: ForeignKey to the Item table
qty: Quantity purchased
rate: Price per unit at the time of purchase
amount: Total purchase amount (calculated as qty * rate)
Sale
Stores sale transactions:

id: Primary Key
timestamp: Timestamp of the sale
item_id: ForeignKey to the Item table
qty: Quantity sold
rate: Price per unit at the time of sale
amount: Total sale amount (calculated as qty * rate)
Forms
ItemForm
Fields: name, qty, price
Validates if an item already exists before adding.
PurchaseForm
Fields: item_id, qty, rate
Allows the user to select items, specify quantity, and rate for the purchase.
SaleForm
Fields: item_id, qty, rate
Allows the user to specify sales details including item, quantity, and rate.
Flash Messages
The application uses flash messages to notify the user about the status of their actions. Common messages include:

"Item added successfully!"
"Insufficient balance for purchase!"
"Sales successfully added!"
"Item already exists."
Styling
The project uses custom CSS in style.css to style various components:

General Styling: Sets up fonts, colors, and background for the page.
Table Styling: Adds shadows, hover effects, and customizations to tables.
Navbar: Adds an attractive navbar with hover effects.
Buttons: Custom buttons with hover and focus effects.
