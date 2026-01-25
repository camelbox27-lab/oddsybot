const functions = require('firebase-functions');
const admin = require('firebase-admin');
const fetch = require('node-fetch');

admin.initializeApp();

exports.updateLiveScores = functions.pubsub
  .schedule('every 30 seconds')
  .onRun(async (context) => {
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
        matches: matches,
        lastUpdate: admin.firestore.FieldValue.serverTimestamp()
      });
      
      console.log(`${matches.length} maç güncellendi`);
    } catch (error) {
      console.error('Hata:', error);
    }
  });