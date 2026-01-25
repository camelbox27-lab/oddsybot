const admin = require('firebase-admin');
const fetch = require('node-fetch');

if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert(JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT))
  });
}

module.exports = async (req, res) => {
  try {
    const response = await fetch('https://www.sofascore.com/api/v1/sport/football/events/live');
    const data = await response.json();
    
    const matches = data.events.map(event => ({
      id: String(event.id),
      league: event.tournament.name,
      country: event.tournament.category.name,
      homeTeam: event.homeTeam.name,
      awayTeam: event.awayTeam.name,
      homeScore: event.homeScore?.current || 0,
      awayScore: event.awayScore?.current || 0,
      status: event.status.type
    }));
    
    await admin.firestore().collection('liveMatches').doc('current').set({
      matches,
      lastUpdate: admin.firestore.FieldValue.serverTimestamp()
    });
    
    res.json({ success: true, count: matches.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};