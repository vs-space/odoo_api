from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Configuration Odoo
ODOO_URL = "http://localhost:8069/jsonrpc"  # URL de votre instance Odoo
ODOO_DB = "api"  # Nom de la base de données Odoo
ODOO_USERNAME = "vs101@gmail.com"  # Utilisateur Odoo
ODOO_PASSWORD = "123@456"  # Mot de passe Odoo


# Fonction pour authentifier avec Odoo
def odoo_authenticate():
    response = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "authenticate",
            "args": [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}]
        },
        "id": 1
    })
    return response.json().get("result")


# Route pour ajouter un produit
@app.route("/add_product", methods=["POST"])
def add_product():
    uid = odoo_authenticate()  # Authentification avec Odoo
    if not uid:
        return jsonify({"error": "Authentication failed"}), 401

    # Récupérer les données du produit depuis la requête POST
    product_data = request.json
    if not product_data:
        return jsonify({"error": "No product data provided"}), 400

    # Vérifier les champs obligatoires
    name = product_data.get("name")
    list_price = product_data.get("list_price", 0.0)
    qty_available = product_data.get("qty_available", 0.0)

    if not name:
        return jsonify({"error": "Product name is required"}), 400

    # Appel pour créer un produit dans Odoo
    response = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.product',  # Modèle Odoo
                'create',           # Méthode pour créer un enregistrement
                [{
                    'name': name,               # Nom du produit
                    'list_price': list_price,   # Prix de vente
                    'qty_available': qty_available  # Quantité disponible (facultatif)
                }]
            ]
        },
        "id": 2
    })

    # Vérifier la réponse
    result = response.json()
    if "result" in result:
        return jsonify({"message": "Product created successfully", "product_id": result["result"]})
    else:
        return jsonify({"error": "Failed to create product", "details": result.get("error")}), 500


# Route principale (optionnelle)
@app.route("/")
def index():
    return "Bienvenue dans l'application Flask intégrée à Odoo!"


if __name__ == "__main__":
    app.run(debug=True)

'''
exemple de teste 
{
  "name": "Produit 2",
  "list_price": 400.0,
  "qty_available": 12
}

'''