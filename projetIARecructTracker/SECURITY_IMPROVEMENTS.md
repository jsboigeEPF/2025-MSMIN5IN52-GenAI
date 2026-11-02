# Améliorations de la Sécurité - Authentification par Cookie HttpOnly

## 📋 Résumé des changements

Le système d'authentification a été migré de **localStorage** vers des **cookies HttpOnly** pour améliorer considérablement la sécurité de l'application contre les attaques XSS (Cross-Site Scripting).

## 🔒 Pourquoi ce changement ?

### Avant : localStorage (❌ Vulnérable)
```javascript
// Le token était accessible depuis JavaScript
localStorage.setItem('ai_recruit_token', token);
const token = localStorage.getItem('ai_recruit_token');
```

**Problèmes :**
- ❌ Accessible par n'importe quel script JavaScript
- ❌ Vulnérable aux attaques XSS
- ❌ Un script malveillant peut voler le token
- ❌ Pas de protection CSRF intégrée

### Après : Cookie HttpOnly (✅ Sécurisé)
```python
# Côté backend - Le cookie est inaccessible depuis JavaScript
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,      # Impossible d'accéder via JavaScript
    secure=False,       # True en production avec HTTPS
    samesite="lax",     # Protection CSRF
    max_age=86400       # 24 heures
)
```

**Avantages :**
- ✅ Inaccessible depuis JavaScript (protection XSS)
- ✅ Envoyé automatiquement avec chaque requête
- ✅ Protection CSRF avec `SameSite=lax`
- ✅ Plus sécurisé selon les standards OWASP
- ✅ Configuration `secure=True` en production avec HTTPS

## 🔧 Modifications Backend

### 1. Endpoint de connexion (`/auth/login`)
```python
@router.post("/login")
def login(
    response: Response,
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    # ... validation des credentials ...
    
    # Configurer le cookie HttpOnly
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # TODO: True en production
        samesite="lax",
        max_age=86400,
        path="/"
    )
    
    return {"success": True, "user": user_data}  # Pas de token dans la réponse
```

### 2. Callback OAuth (`/oauth/gmail/callback`)
```python
@router.get("/gmail/callback")
async def gmail_oauth_callback(
    response: Response,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    # ... traitement OAuth ...
    
    # Créer la réponse de redirection
    redirect_response = RedirectResponse(url=callback_url)
    
    # Configurer le cookie HttpOnly
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400,
        path="/"
    )
    
    return redirect_response
```

### 3. Vérification de l'utilisateur actuel (`get_current_user`)
```python
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Récupère l'utilisateur depuis le cookie (prioritaire) ou le header Authorization
    """
    token = None
    
    # Essayer le cookie d'abord
    token = request.cookies.get("access_token")
    
    # Fallback sur le header Authorization si pas de cookie
    if not token and credentials:
        token = credentials.credentials
    
    # Validation du token et retour de l'utilisateur
    # ...
```

### 4. Endpoint de déconnexion (`/auth/logout`)
```python
@router.post("/logout")
def logout(
    response: Response,
    current_user = Depends(get_current_user)
):
    # Effacer le cookie
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax"
    )
    
    return {"success": True, "message": "Déconnexion réussie"}
```

## 🔧 Modifications Frontend

### 1. AuthService - Plus de localStorage pour le token
```typescript
// Avant
private setSession(authResponse: AuthResponse): void {
    localStorage.setItem(this.TOKEN_KEY, authResponse.access_token);  // ❌
    // ...
}

// Après
private setSession(authResponse: AuthResponse): void {
    // Ne plus stocker le token (il est dans un cookie HttpOnly)
    // Garder uniquement les infos utilisateur en cache
    localStorage.setItem(this.USER_KEY, JSON.stringify(authResponse.user));
    // ...
}
```

### 2. AuthService - Nouvelle méthode getCurrentUser
```typescript
/**
 * Récupère les informations de l'utilisateur actuel depuis le backend
 * Le cookie est automatiquement envoyé avec la requête
 */
getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/me`)
        .pipe(catchError(this.handleError));
}
```

### 3. AuthService - Initialisation au démarrage
```typescript
private initializeAuth(): void {
    // Tenter de récupérer l'utilisateur via le cookie
    this.getCurrentUser().subscribe({
        next: (user) => {
            this.currentUserSubject.next(user);
            this.isAuthenticatedSubject.next(true);
        },
        error: () => {
            this.clearSession(false);
        }
    });
}
```

### 4. HTTP Interceptor - withCredentials
```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const authService = inject(AuthService);
    
    // Activer l'envoi des cookies pour toutes les requêtes
    const authReq = req.clone({
        withCredentials: true  // ✅ Envoie automatiquement les cookies HttpOnly
    });
    
    return next(authReq).pipe(
        catchError((error: HttpErrorResponse) => {
            if (error.status === 401 && !isAuthRequest(req.url)) {
                authService.logout();
            }
            return throwError(() => error);
        })
    );
};
```

### 5. OAuth Callback Component
```typescript
// Avant
private authenticateUserWithToken(token: string, email: string): void {
    localStorage.setItem('ai_recruit_token', token);  // ❌
    // ...
}

// Après
private loadCurrentUser(): void {
    // Le cookie a été configuré par le backend
    // Appeler l'endpoint /me pour récupérer les infos
    this.authService.getCurrentUser().subscribe({
        next: (user) => {
            this.authService.setCurrentUser(user);
        }
    });
}
```

## 🔐 Configuration CORS

Le backend FastAPI doit être configuré avec `allow_credentials=True` :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Frontend origin
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,  # ✅ Important pour les cookies
)
```

## 📝 Flux d'authentification

### 1. Connexion normale
1. Utilisateur soumet login/password
2. Backend valide et crée un JWT
3. Backend configure un cookie HttpOnly avec le JWT
4. Backend retourne les infos utilisateur (sans token)
5. Frontend stocke les infos utilisateur en local
6. Toutes les futures requêtes envoient automatiquement le cookie

### 2. Connexion via Gmail OAuth
1. Utilisateur clique sur "Se connecter avec Gmail"
2. Redirection vers Google OAuth
3. Google redirige vers `/oauth/gmail/callback?code=...`
4. Backend échange le code contre un token Gmail
5. Backend crée/trouve l'utilisateur
6. Backend génère un JWT et configure un cookie HttpOnly
7. Backend redirige vers le frontend `/oauth/callback?success=true`
8. Frontend appelle `/auth/me` pour récupérer les infos (cookie envoyé auto)
9. Frontend redirige vers le dashboard

### 3. Déconnexion
1. Utilisateur clique sur "Déconnexion"
2. Frontend appelle `/auth/logout` (cookie envoyé auto)
3. Backend efface le cookie avec `response.delete_cookie()`
4. Frontend efface le cache local et redirige vers login

### 4. Refresh au démarrage de l'app
1. Application Angular démarre
2. `AuthService.initializeAuth()` appelé
3. Appel GET `/auth/me` (cookie envoyé automatiquement)
4. Si succès : utilisateur connecté
5. Si 401 : utilisateur déconnecté

## 🚀 Migration en Production

### Checklist avant déploiement :

1. ✅ **Activer HTTPS sur le serveur**
   ```python
   # Backend: Mettre secure=True
   response.set_cookie(
       key="access_token",
       value=access_token,
       httponly=True,
       secure=True,  # ✅ Obligatoire en production
       samesite="lax",
       max_age=86400,
       path="/"
   )
   ```

2. ✅ **Configurer le domaine dans SameSite**
   - En production, utiliser `samesite="strict"` pour plus de sécurité
   - Vérifier que frontend et backend sont sur le même domaine (ou sous-domaines)

3. ✅ **Mettre à jour CORS avec le domaine de production**
   ```python
   allow_origins=["https://votredomaine.com"]
   ```

4. ✅ **Configurer la durée de validité du cookie**
   - Actuellement : 24 heures (`max_age=86400`)
   - Adapter selon vos besoins de sécurité

## 📊 Comparaison Sécurité

| Aspect | localStorage | Cookie HttpOnly |
|--------|-------------|-----------------|
| **XSS Protection** | ❌ Non | ✅ Oui |
| **CSRF Protection** | ❌ Non | ✅ Oui (SameSite) |
| **JavaScript Access** | ✅ Oui | ❌ Non (sécurisé) |
| **Auto-envoi** | ❌ Non | ✅ Oui |
| **HTTPS requis** | ❌ Non | ✅ Oui (prod) |
| **Norme OWASP** | ❌ Non recommandé | ✅ Recommandé |

## 🔍 Tests de sécurité

### 1. Vérifier que le token n'est pas accessible
```javascript
// Dans la console du navigateur
console.log(document.cookie);  // Ne devrait PAS afficher access_token
console.log(localStorage.getItem('ai_recruit_token'));  // null
```

### 2. Vérifier l'envoi automatique du cookie
```javascript
// Le cookie est envoyé automatiquement avec chaque requête
fetch('http://localhost:8000/api/v1/auth/me', { credentials: 'include' })
```

### 3. Tester la déconnexion
- Se connecter
- Vérifier dans DevTools > Application > Cookies que `access_token` existe
- Se déconnecter
- Vérifier que le cookie a été supprimé

## 📚 Références

- [OWASP Secure Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [MDN: HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [FastAPI Cookies Documentation](https://fastapi.tiangolo.com/advanced/response-cookies/)
- [Angular HttpClient withCredentials](https://angular.io/api/common/http/HttpClient)

## ✅ Conclusion

Cette migration vers les cookies HttpOnly améliore significativement la sécurité de l'application :
- Protection contre les attaques XSS
- Protection CSRF avec SameSite
- Conformité aux standards de sécurité OWASP
- Prêt pour la production avec HTTPS

**Note importante :** En production, n'oubliez pas de configurer `secure=True` pour que le cookie ne soit envoyé que via HTTPS.
