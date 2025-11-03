const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const musicRoutes = require('./routes/musicRoutes');

dotenv.config();
console.log('🔑 Clé API chargée:', process.env.SUNO_API_KEY ? 'OUI ✅' : 'NON ❌');
const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/music', musicRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Backend is running' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Une erreur est survenue', 
    message: err.message 
  });
});

app.listen(PORT, () => {
  console.log(`🎵 Serveur backend démarré sur le port ${PORT}`);
});