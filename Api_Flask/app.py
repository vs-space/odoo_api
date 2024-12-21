from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Configuration Odoo
ODOO_URL = "http://localhost:8069/jsonrpc"  # URL de votre instance Odoo
ODOO_DB = "api"          # Nom de la base de données Odoo
ODOO_USERNAME = "vs101@gmail.com"  # Utilisateur Odoo
ODOO_PASSWORD = "123@456"       # Mot de passe Odoo


# Fonction pour authentifier avec Odoo
def odoo_authenticate():
    response = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0",
        "method": "call",
# La méthode call dans l'API JSON-RPC d'Odoo est utilisée pour exécuter des appels de méthode à distance.
# Elle permet de faire des demandes vers l'instance d'Odoo, en utilisant le protocole JSON-RPC.
        "params": {
            "service": "common", #Le service common est utilisé pour des tâches générales et des opérations d'administration sur la base de données Odoo.
                                 #Il ne manipule pas directement les modèles ou les données métier, mais il est nécessaire pour des opérations comme l'authentification ou la gestion de bases de données.
            "method": "authenticate",
#La méthode authenticate dans l'API d'Odoo est utilisée pour s'authentifier
#auprès de l'instance Odoo et obtenir un identifiant utilisateur (uid) valide. Cela permet à l'utilisateur d'effectuer des opérations sur les modèles de l'instance Odoo.
            "args": [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}]
        },
        "id": 1
    })
    return response.json().get("result") #retourne l'uid si l'authentification réussit.


# Route pour récupérer les produits depuis Odoo
@app.route("/products", methods=["GET"])
def get_products():
    uid = odoo_authenticate()  # Authentification avec Odoo
    if not uid:
        return jsonify({"error": "Authentication failed"}), 401
#La fonction jsonify dans Flask est utilisée pour formater des réponses en JSON
#et les envoyer au client.
    # Appel pour récupérer les données des produits
    response = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object", #Le service object est utilisé pour interagir avec les modèles et les données métier d'Odoo.
                                 #Il permet d'exécuter des actions spécifiques sur les modèles (comme res.partner, product.product, etc.) et leurs enregistrements.
            "method": "execute_kw",
#La méthode execute_kw est utilisée pour exécuter presque toutes les actions via l'API JSON-RPC ou XML-RPC d'Odoo.
#C'est une méthode générique qui permet d'appeler des fonctions spécifiques sur les modèles Odoo, que ce soit pour les opérations CRUD, les recherches, ou l'exécution de méthodes personnalisées.
            "args": [
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.product',  # Modèle Odoo pour les produits
                'search_read',      # Méthode Odoo pour lire les données
                [[('list_price','>',300)]],  # Pas de filtre pour tous les produits
                {'fields': ['id', 'name', 'list_price', 'qty_available'], 'limit': 10}  # Champs et limite
            ]
        },
        "id": 2
    })

    # Renvoyer les produits sous forme de JSON
    return jsonify(response.json().get("result"))


# Route principale (optionnelle)
@app.route("/")
def index():
    return "Bienvenue dans l'application Flask intégrée à Odoo!"


if __name__ == "__main__":
    app.run(debug=True)
