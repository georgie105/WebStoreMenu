import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import redirect, secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///item.db'
db = SQLAlchemy(app)

# Database model
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
    items = Item.query.order_by(Item.date_created).all()
    return render_template('index.html', items=items)


# Manage items page
@app.route('/manage')
def manage():
    items = Item.query.order_by(Item.date_created).all()
    return render_template('manage.html', items=items)

# Add items page
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        itemName = request.form['name']
        itemPrice = request.form['price']
        itemImage = request.files['image']

        # Create new Item
        new_Item = Item(name=itemName,price=itemPrice,image=secure_filename(itemImage.filename))

        try:
            itemImage.save('./static/uploads/'+secure_filename(itemImage.filename))
            db.session.add(new_Item)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        return render_template('add.html')


@app.route('/delete/<int:id>')
def delete(id):
    item_to_delete = Item.query.get_or_404(id)
    image_to_delete = './static/uploads/'+item_to_delete.image
    try:
        db.session.delete(item_to_delete)
        os.remove(image_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    item = Item.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', item=item)


if __name__ == '__name__':
    app.run(debug=True)
