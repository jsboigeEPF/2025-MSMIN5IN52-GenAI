# Guide de Test - Authentification par Cookie HttpOnly

## 🔄 Étapes pour tester le système complet

### 1. Redémarrer les serveurs

**Backend:**
```bash
cd backend
python run_server.py
```

**Frontend:**
```bash
cd frontend
ng serve
```

### 2. Tester l'authentification Gmail OAuth

#### Option A: Nouvel utilisateur
1. Ouvrir http://localhost:4200
2. Cliquer sur "Se connecter avec Gmail"
3. Autoriser l'accès Gmail
4. Vérifier la redirection vers le dashboard
5. Ouvrir DevTools > Application > Cookies
6. Vérifier que le cookie `access_token` existe avec `HttpOnly = ✓`

#### Option B: Utilisateur existant
1. Se connecter avec email/password
2. Le cookie `access_token` doit être créé
3. Naviguer vers Dashboard > Paramètres Gmail
4. Cliquer sur "Connecter Gmail"
5. Autoriser l'accès Gmail

### 3. Vérifier le statut Gmail

Dans le Dashboard NLP, section "Statut Gmail" devrait afficher:
- ✅ Gmail connecté
- Email de l'utilisateur
- Date de dernière synchronisation

Si "null" ou non connecté:
1. Ouvrir la console du navigateur
2. Vérifier les logs : `Statut Gmail récupéré: { connected: true, ... }`
3. Si 403 ou 401, vérifier que le cookie est bien envoyé

### 4. Synchroniser les emails

1. Dans le Dashboard NLP
2. Section "Ingestion des Emails"
3. Sélectionner l'intervalle (ex: 7 jours)
4. Cliquer "Démarrer la synchronisation"
5. Vérifier les logs backend pour voir les emails récupérés

### 5. Analyser les emails

1. Section "Analyse NLP"
2. Sélectionner l'intervalle
3. Cliquer "Lancer l'analyse"
4. Vérifier les résultats

## 🐛 Problèmes courants et solutions

### Problème 1: "Statut Gmail: null"

**Cause:** Le cookie n'est pas envoyé ou l'utilisateur n'est pas authentifié

**Solution:**
1. Vérifier que l'intercepteur HTTP a `withCredentials: true`
2. Vérifier que le cookie existe dans DevTools > Application > Cookies
3. Se reconnecter si nécessaire

### Problème 2: "403 Forbidden sur /auth/me"

**Cause:** `security = HTTPBearer()` sans `auto_error=False`

**Solution:** ✅ Déjà corrigé dans `auth.py`
```python
security = HTTPBearer(auto_error=False)
```

### Problème 3: "Aucun email à traiter"

**Causes possibles:**
1. Gmail non connecté
2. Pas d'emails dans l'intervalle sélectionné
3. Emails déjà synchronisés

**Solutions:**
1. Vérifier le statut Gmail d'abord
2. Augmenter l'intervalle de synchronisation
3. Vérifier les logs backend pour voir les emails récupérés

### Problème 4: Cookie non défini après login

**Cause:** Le backend ne configure pas le cookie

**Solution:** ✅ Déjà corrigé
- `/auth/login` configure le cookie
- `/oauth/gmail/callback` configure le cookie

### Problème 5: Cookie non envoyé avec les requêtes

**Cause:** `withCredentials` manquant

**Solution:** ✅ Déjà corrigé dans `auth.interceptor.ts`
```typescript
const authReq = req.clone({
    withCredentials: true
});
```

## 🔍 Vérifications de sécurité

### 1. Token non accessible depuis JavaScript
Ouvrir la console du navigateur:
```javascript
console.log(localStorage.getItem('ai_recruit_token'));  // null
console.log(document.cookie);  // Ne devrait PAS contenir access_token
```

✅ Si null ou absent = Sécurisé

### 2. Cookie HttpOnly configuré
DevTools > Application > Cookies > http://localhost:4200

Vérifier:
- Name: `access_token`
- HttpOnly: ✓
- SameSite: `Lax`
- Secure: (vide en dev, ✓ en prod)

### 3. Cookie envoyé automatiquement
DevTools > Network > Sélectionner une requête API > Headers

Vérifier:
```
Cookie: access_token=eyJ0eXAiOiJKV1QiLC...
```

## 📝 Logs à surveiller

### Backend (console)
```
INFO: Redirection OAuth pour l'utilisateur X
INFO: OAuth callback réussi: user@gmail.com
INFO: GET /api/v1/auth/me HTTP/1.1" 200 OK
INFO: GET /api/v1/oauth/gmail/status HTTP/1.1" 200 OK
INFO: POST /api/v1/oauth/gmail/sync-emails HTTP/1.1" 200 OK
```

### Frontend (console navigateur)
```
Statut Gmail récupéré: {connected: true, email: "...", ...}
Résultat synchronisation Gmail: {success: true, synced_emails: 15, ...}
Résultats de l'analyse: {processed_count: 15, ...}
```

## 🚀 Checklist finale

- [ ] Backend redémarré
- [ ] Frontend redémarré
- [ ] Cookie `access_token` présent avec HttpOnly
- [ ] Connexion Gmail réussie
- [ ] Statut Gmail = connecté
- [ ] Synchronisation emails fonctionne
- [ ] Analyse NLP fonctionne
- [ ] Token non accessible en JavaScript
- [ ] Déconnexion efface le cookie

## 📚 Endpoints modifiés

### Backend
- ✅ `/auth/login` - Configure cookie HttpOnly
- ✅ `/auth/logout` - Efface le cookie
- ✅ `/auth/me` - Lit depuis le cookie
- ✅ `get_current_user` - Lit le cookie en priorité
- ✅ `/oauth/gmail/callback` - Configure le cookie
- ✅ `/oauth/gmail/authorize` - Utilise get_current_user

### Frontend
- ✅ `auth.interceptor.ts` - withCredentials: true
- ✅ `auth.service.ts` - Ne stocke plus le token
- ✅ `gmail-oauth.service.ts` - Ne cherche plus le token en local
- ✅ `oauth-callback.component.ts` - Appelle /auth/me

## 🎯 Flux complet attendu

1. **Inscription via Gmail:**
   - Clic "Se connecter avec Gmail"
   - Redirection Google OAuth
   - Callback → Backend crée user + cookie
   - Redirection frontend → Appel /auth/me
   - Dashboard affiché

2. **Statut Gmail:**
   - Au chargement du dashboard
   - Service appelle /oauth/gmail/status
   - Backend lit cookie → retourne statut
   - Frontend affiche "Gmail connecté"

3. **Synchronisation:**
   - Clic "Démarrer synchronisation"
   - POST /oauth/gmail/sync-emails (cookie auto)
   - Backend récupère emails Gmail
   - Retour: nombre d'emails synchronisés

4. **Analyse:**
   - Clic "Lancer analyse"
   - POST /emails/batch-process (cookie auto)
   - Backend analyse avec NLP
   - Retour: résultats analyse

5. **Déconnexion:**
   - Clic "Déconnexion"
   - POST /auth/logout
   - Backend efface le cookie
   - Redirection vers login
