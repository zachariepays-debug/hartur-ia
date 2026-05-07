const express = require('express');
const admin = require('firebase-admin');
const bodyParser = require('body-parser');

// 1. Initialisation de Firebase
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();
const app = express();
app.use(bodyParser.json());

// Configuration du Créateur
const CREATOR_NAME = "Zacharie Pays";

/**
 * Endpoint pour envoyer un message
 */
app.post('/chat/send', async (req, res) => {
    const { sessionId, message, role } = req.body;
    
    try {
        // Enregistrement du message dans une collection temporaire ou active
        await db.collection('active_sessions').doc(sessionId).collection('messages').add({
            text: message,
            role: role,
            timestamp: admin.firestore.FieldValue.serverTimestamp()
        });

        res.status(200).send({ status: "Message envoyé" });
    } catch (error) {
        res.status(500).send({ error: error.message });
    }
});

/**
 * Endpoint pour TERMINER et ARCHIVER la conversation
 * C'est ici que l'historique devient visible dans "conversations"
 */
app.post('/chat/finish', async (req, res) => {
    const { sessionId } = req.body;

    try {
        // 1. Récupérer tous les messages de la session
        const messagesSnapshot = await db.collection('active_sessions')
                                         .doc(sessionId)
                                         .collection('messages')
                                         .orderBy('timestamp')
                                         .get();

        let fullHistory = [];
        messagesSnapshot.forEach(doc => fullHistory.push(doc.data()));

        // 2. Créer l'entrée finale dans l'historique Firestore
        const historyRef = db.collection('conversations').doc(sessionId);
        
        await historyRef.set({
            creator: CREATOR_NAME, // Votre nom : Zacharie Pays
            endedAt: admin.firestore.FieldValue.serverTimestamp(),
            transcript: fullHistory,
            status: "Terminée"
        });

        // 3. Nettoyage de la session active (optionnel)
        await db.collection('active_sessions').doc(sessionId).delete();

        res.status(200).send({ 
            message: "Conversation archivée avec succès",
            creator: CREATOR_NAME,
            path: `conversations/${sessionId}`
        });

    } catch (error) {
        res.status(500).send({ error: "Erreur lors de l'archivage : " + error.message });
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Serveur actif sur le port ${PORT}`);
    console.log(`Créateur configuré : ${CREATOR_NAME}`);
});
