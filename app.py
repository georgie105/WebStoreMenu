import os 
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import redirect, secure_filename

app = Flask(__name__) # Initialize flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///item.db' # Connect to SQLite Database

"""
We are always faced with this warning. 

FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.

solving it will be 
"""

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app) # Initialize Database to db variable

# Create Database model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


# Index page
@app.route('/')
def index():
    items = Item.query.order_by(Item.date_created).all() # Load all items saved to database
    return render_template('index.html', items=items)  # render index page with items obtained from the database


# Manage items page
@app.route('/manage')
def manage():
    items = Item.query.order_by(Item.date_created).all() # Load all items from the Database
    return render_template('manage.html', items=items)  # render manage page with all items got from the database

'''
    This route handles both GET and POST requests
    if request is equal to POST
        run it's code
    else if request is equal to GET
        render manage page
'''
@app.route('/add', methods=['GET', 'POST']) 
def add():
    if request.method == 'POST':
        # Load form data sent from frontend
        itemName = request.form['name']
        itemPrice = request.form['price']
        itemImage = request.files['image']

        # Create new Item using Item Model
        # the secure_filename() returns a secure version of the filename
        new_Item = Item(name=itemName,price=itemPrice,image=secure_filename(itemImage.filename))

        # Try catch block to handle errors
        try:
            # Save image to specified path
            itemImage.save('./static/uploads/'+secure_filename(itemImage.filename))
            # Prepare data to be saved to database
            db.session.add(new_Item)
            # Add data to database
            db.session.commit()
            
            # Redirect to view items page
            return redirect('/')
        except:
            # If any errors occurs when saving task, return whats below
            return 'There was an issue adding your task'
    else:
        # If request is a get request, render the add page
        return render_template('add.html')


# Delete Item functionality
@app.route('/delete/<int:id>')
def delete(id):
    item_to_delete = Item.query.get_or_404(id) # Load all items from Database
    image_to_delete = item_to_delete.image # Select image name to delete
    image_to_delete_path = f'./static/uploads/{image_to_delete}' # create path for deleting image
    if os.path.isfile(image_to_delete_path): # check if the  path contains image file
        os.remove(image_to_delete_path) # delete image file
        
    # Try except block to grab errors
    try:
        # Prepare Delete item from Database
        db.session.delete(item_to_delete)
        # Implement changes to database
        db.session.commit()
        
        # Redirect to manage page
        return redirect('/manage')
    except:
        # Incase of an error, run this code
        return 'There was a problem deleting that task'


# Update item functionality
@app.route('/update/<int:id>', methods=['GET', 'POST'])
# Take in item id
def update(id):
    item = Item.query.get_or_404(id) #  select item from database from db
    
    if request.method == 'POST':
        # collect new form data and upate old data directly
        item.name = request.form['name']
        item.price = request.form['price']
        
        try:
            # Update database
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', item=item)


"""
 This is a shell context processor
 It enables you to interact with your application in a very goo manner via ` flask shell `

 It works like this,
 you have to 

 ` export FLASK_APP=app.py`

 ` flask shell`

Creating the db will be as simple as 
>>> db.create_all() 
>>> 
"""
@app.shell_context_processor
def make_shell_context():
    return {
        'app':app,
        'db':db,
        'Item':Item
    }

if __name__ == '__name__':
    app.run(debug=True)
