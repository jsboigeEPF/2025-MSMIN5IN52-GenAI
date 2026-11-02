import { Injectable } from '@angular/core';
import { CanActivate, CanActivateChild, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable, of } from 'rxjs';
import { map, take, filter, switchMap, catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate, CanActivateChild {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.checkAuth(state.url);
  }

  canActivateChild(
    childRoute: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.checkAuth(state.url);
  }

  private checkAuth(url: string): Observable<boolean> {
    return this.authService.authInitialized$.pipe(
      filter(initialized => initialized),
      take(1),
      switchMap(() => this.authService.isAuthenticated$.pipe(take(1))),
      switchMap(isAuthenticated => {
        if (isAuthenticated) {
          return of(true);
        }

        const token = this.authService.getToken();
        if (token) {
          return this.authService.reloadAuthState().pipe(
            map(() => true),
            catchError(() => {
              this.redirectToLogin(url);
              return of(false);
            })
          );
        }

        this.redirectToLogin(url);
        return of(false);
      })
    );
  }

  private redirectToLogin(url: string): void {
    this.router.navigate(['/auth/login'], { 
      queryParams: { returnUrl: url }
    });
  }
}

@Injectable({
  providedIn: 'root'
})
export class GuestGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.authService.authInitialized$.pipe(
      filter(initialized => initialized),
      take(1),
      switchMap(() => this.authService.isAuthenticated$.pipe(take(1))),
      map(isAuthenticated => {
        if (!isAuthenticated) {
          return true;
        } else {
          // Utilisateur déjà connecté, rediriger vers le dashboard
          this.router.navigate(['/dashboard']);
          return false;
        }
      })
    );
  }
}

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.authService.authInitialized$.pipe(
      filter(initialized => initialized),
      take(1),
      switchMap(() => this.authService.isAuthenticated$.pipe(take(1))),
      map(isAuthenticated => {
        if (isAuthenticated && this.authService.hasRole('admin')) {
          return true;
        } else if (isAuthenticated) {
          // Utilisateur connecté mais pas admin
          this.router.navigate(['/dashboard']);
          return false;
        } else {
          // Utilisateur non connecté
          this.router.navigate(['/auth/login'], { 
            queryParams: { returnUrl: state.url }
          });
          return false;
        }
      })
    );
  }
}
