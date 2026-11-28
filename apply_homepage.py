"""Run once from the root of the EXISTING Stellafy repository.
Updates ONLY the sample PRODUCTS list and keeps all existing routes intact.
The files templates/index.html, static/css/style.css and static/images must
already have been copied into the repository from this upgrade bundle.
"""
from pathlib import Path
root=Path.cwd()
p=root/'run.py'
if not p.exists():
    raise SystemExit('Please run this script in the Stellafy repository folder (where run.py exists).')
text=p.read_text(encoding='utf-8')
start=text.find('PRODUCTS = [')
end=text.find('\n\n# Define the social causes', start)
if start < 0 or end < 0:
    raise SystemExit('Could not find expected PRODUCTS block in run.py. No file changed.')
products='''PRODUCTS = [
    {"id": 1, "name": "Reusable Water Bottle", "price": 25.00, "type": "original", "seller": "Stellafy", "image": "bottle.svg"},
    {"id": 2, "name": "Reusable Shopping Bag", "price": 15.00, "type": "marketplace", "seller": "Good Earth Goods", "image": "bag.svg"},
    {"id": 3, "name": "Eco-Friendly Notebook", "price": 12.00, "type": "marketplace", "seller": "Paper & Pine", "image": "notebook.svg"},
    {"id": 4, "name": "Ceramic Coffee Mug", "price": 20.00, "type": "marketplace", "seller": "Riverbend Studio", "image": "mug.svg"},
    {"id": 5, "name": "Cotton Tote Bag", "price": 18.00, "type": "original", "seller": "Stellafy", "image": "tote.svg"},
    {"id": 6, "name": "Bamboo Desk Organizer", "price": 30.00, "type": "original", "seller": "Stellafy", "image": "organizer.svg"}
]'''
text=text[:start]+products+text[end:]
p.write_text(text,encoding='utf-8')
print('Updated sample PRODUCTS in run.py; routes and pricing logic are unchanged.')
