# run.py
from app import create_app, db
from app.models import Product, Location, ProductMovement

app = create_app()

# optional shell context for flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Product': Product, 'Location': Location, 'ProductMovement': ProductMovement}

if __name__ == '__main__':
    app.run(debug=True)
