import { inject } from '@angular/core';
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { throwError, catchError } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * Intercepteur HTTP pour gérer l'authentification par cookie HttpOnly
 * - Active withCredentials pour envoyer les cookies automatiquement
 * - Gère les erreurs 401 en déconnectant l'utilisateur
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // Activer l'envoi des cookies (HttpOnly) pour toutes les requêtes vers l'API
  const authReq = req.clone({
    withCredentials: true  // Important: envoie les cookies HttpOnly automatiquement
  });
  
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
    '/auth/password-reset',
    '/auth/verify-email'
  ];
  
  return authUrls.some(authUrl => url.includes(authUrl));
}
