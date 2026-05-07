import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
from datetime import datetime

# 1. Initialisation de Firebase
# Assure-toi que ton fichier 'serviceAccountKey.json' est dans le même dossier
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)

# CONFIGURATION PERSONNELLE
NOM_CREATEUR = "Zacharie Pays"
ADMIN_PASSWORD = "ton_mot_de_passe_ici"  # À modifier selon tes besoins

@app.route('/admin/login', methods=['POST'])
def login_and_archive():
    data = request.json
    password = data.get('password')
    session_id = data.get('sessionId', f"auto_{int(datetime.now().timestamp())}")
    history = data.get('history', [])

    # 2. Vérification du mot de passe
    if not password or password != ADMIN_PASSWORD:
        print(f"Tentative échouée : mot de passe incorrect.")
        return jsonify({"success": False, "message": "Accès refusé"}), 401

    try:
        # 3. Connexion et Archivage automatique sur Firestore
        print(f"Connexion réussie pour : {NOM_CREATEUR}")
        
        doc_ref = db.collection('historique_conversations').document(session_id)
        
        # Envoi direct des données
        doc_ref.set({
            "createur": NOM_CREATEUR,
            "date_archivage": datetime.now(),
            "conversations": history,
            "statut": "Terminé et Archivé"
        })

        # 4. Réponse pour débloquer l'interface
        return jsonify({
            "success": True,
            "message": f"Bonjour {NOM_CREATEUR}, archive créée avec succès.",
            "redirect_url": "/dashboard"
        }), 200

    except Exception as e:
        print(f"Erreur technique : {e}")
        return jsonify({"success": False, "message": "Erreur lors de l'archivage"}), 500

if __name__ == '__main__':
    print(f"--- Système de {NOM_CREATEUR} ---")
    app.run(port=5000, debug=True)
