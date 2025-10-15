import { inject } from '@angular/core';
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { throwError, catchError } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * Intercepteur HTTP pour gérer l'authentification Bearer Token
 * Simple, robuste, et fonctionne partout (dev et prod)
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // Récupérer le token depuis sessionStorage
  const token = authService.getToken();
  
  // Ajouter le header Authorization si token disponible
  let authReq = req;
  if (token) {
    authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }
  
  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si erreur 401 (non authentifié ou token expiré), déconnecter l'utilisateur
      if (error.status === 401 && !isAuthRequest(req.url)) {
        authService.logout();
      }
      
      return throwError(() => error);
    })
  );
};

function isAuthRequest(url: string): boolean {
  // URLs d'authentification qui ne nécessitent pas de déconnexion en cas de 401
  const authUrls = [
    '/auth/login',
    '/auth/register',
    '/auth/me',
    '/auth/logout',  // ⚠️ IMPORTANT: éviter la boucle infinie
    '/auth/password-reset',
    '/auth/verify-email'
  ];
  
  return authUrls.some(authUrl => url.includes(authUrl));
}
