import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { JobApplicationService } from '../../services/job-application.service';
import { JobApplication } from '../../models';

@Component({
  selector: 'app-job-applications-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="applications-container">
      <div class="page-header">
        <div class="header-content">
          <h1>📄 Candidatures</h1>
          <p>Suivi de vos candidatures avec intégration IA</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" routerLink="/dashboard">← Dashboard</button>
          <button class="btn btn-secondary" (click)="loadJobApplications()">🔄 Actualiser</button>
        </div>
      </div>

      <!-- Statistiques rapides -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ jobApplications.length }}</div>
            <div class="stat-label">Total candidatures</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ getApplicationsByStatus('APPLIED').length + getApplicationsByStatus('ACKNOWLEDGED').length }}</div>
            <div class="stat-label">En cours</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ getApplicationsByStatus('INTERVIEW').length }}</div>
            <div class="stat-label">Entretiens</div>
          </div>
          <div class="stat-item success">
            <div class="stat-number">{{ getApplicationsByStatus('ACCEPTED').length }}</div>
            <div class="stat-label">Acceptées</div>
          </div>
        </div>
      </div>

      <!-- Liste des candidatures -->
      <div class="applications-list">
        @if (loading) {
          <div class="loading-card">
            <div class="loading-spinner"></div>
            <p>Chargement des candidatures...</p>
          </div>
        } @else if (error) {
          <div class="error-card">
            <h3>❌ Erreur</h3>
            <p>{{ error }}</p>
            <button class="btn btn-primary" (click)="loadJobApplications()">Réessayer</button>
          </div>
        } @else if (jobApplications.length === 0) {
          <div class="empty-state">
            <div class="empty-icon">📄</div>
            <h3>Aucune candidature trouvée</h3>
            <p>Commencez par créer votre première candidature</p>
            <button class="btn btn-primary" routerLink="/dashboard">
              ➕ Retour au Dashboard
            </button>
          </div>
        } @else {
          @for (application of jobApplications; track application.id) {
            <div class="application-card" [class]="'status-' + application.status.toLowerCase()">
              <div class="card-header">
                <div class="card-title-section">
                  <h3 class="application-id">Candidature #{{ application.id }}</h3>
                  <div class="application-info">
                    <span class="application-details">Offre: {{ application.job_offer_id }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <div class="status-management">
                    <div class="status-inputs">
                      <span class="status-badge" [class]="'badge-' + application.status.toLowerCase()">
                        {{ getStatusLabel(application.status) }}
                      </span>
                      <select
                        class="status-select"
                        [value]="application.status"
                        (change)="onStatusChange(application, $event)"
                        [disabled]="isStatusUpdating(application.id)">
                        @for (option of statusOptions; track option) {
                          <option [value]="option">{{ getStatusLabel(option) }}</option>
                        }
                      </select>
                    </div>
                    <div class="status-feedback">
                      @if (isStatusUpdating(application.id)) {
                        <span class="status-loading">Mise à jour...</span>
                      }
                      @if (statusUpdateErrors()[application.id]) {
                        <span class="status-error">{{ statusUpdateErrors()[application.id] }}</span>
                      }
                    </div>
                  </div>
                  <div class="action-buttons">
                    <button class="btn-icon" (click)="toggleApplicationDetails(application.id)" 
                            [title]="expandedApplications().has(application.id) ? 'Réduire' : 'Développer'">
                      {{ expandedApplications().has(application.id) ? '🔼' : '🔽' }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="card-meta">
                <div class="meta-item">
                  📅 Candidature: {{ formatDate(application.applied_date) }}
                </div>
                @if (application.last_update_date) {
                  <div class="meta-item">
                    🔄 Mis à jour: {{ formatDate(application.last_update_date) }}
                  </div>
                }
                @if (application.priority) {
                  <div class="meta-item priority-{{ application.priority.toLowerCase() }}">
                    {{ getPriorityIcon(application.priority) }} {{ application.priority }}
                  </div>
                }
              </div>

              @if (expandedApplications().has(application.id)) {
                <div class="card-details">
                  @if (application.expected_salary) {
                    <div class="detail-section">
                      <strong>💰 Salaire espéré:</strong>
                      <span>{{ application.expected_salary }}€</span>
                    </div>
                  }

                  @if (application.contact_person) {
                    <div class="detail-section">
                      <strong>👤 Contact:</strong>
                      <span>{{ application.contact_person }}</span>
                      @if (application.contact_email) {
                        <span> - {{ application.contact_email }}</span>
                      }
                    </div>
                  }

                  @if (application.notes) {
                    <div class="detail-section">
                      <strong>📝 Notes:</strong>
                      <p class="notes-text">{{ application.notes }}</p>
                    </div>
                  }

                  @if (application.interview_date) {
                    <div class="detail-section">
                      <strong>📅 Date d'entretien:</strong>
                      <span>{{ formatDate(application.interview_date) }}</span>
                    </div>
                  }

                  @if (application.offer_amount) {
                    <div class="detail-section">
                      <strong>💼 Offre reçue:</strong>
                      <span>{{ application.offer_amount }}€</span>
                      @if (application.offer_deadline) {
                        <span> - Délai: {{ formatDate(application.offer_deadline) }}</span>
                      }
                    </div>
                  }

                  @if (application.rejection_reason) {
                    <div class="detail-section">
                      <strong>❌ Raison du refus:</strong>
                      <span>{{ application.rejection_reason }}</span>
                    </div>
                  }

                  <div class="detail-actions">
                    <button class="btn btn-sm btn-primary" routerLink="/emails" 
                            [queryParams]="{application_id: application.id}">
                      📧 Voir emails liés
                    </button>
                  </div>
                </div>
              }
            </div>
          }
        }
      </div>
    </div>
  `,
  styles: [`
    .applications-container {
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
    }

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 30px;
      flex-wrap: wrap;
      gap: 20px;
    }

    .header-content h1 {
      margin: 0 0 5px 0;
      color: #333;
      font-size: 2.2em;
    }

    .header-content p {
      margin: 0;
      color: #666;
      font-size: 1.1em;
    }

    .header-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .btn {
      padding: 10px 16px;
      border: none;
      border-radius: 6px;
      font-weight: 500;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .btn-primary { background: #2196F3; color: white; }
    .btn-secondary { background: #757575; color: white; }
    .btn-sm { padding: 6px 12px; font-size: 14px; }

    .btn:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }

    .stats-section {
      margin-bottom: 25px;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
    }

    .stat-item {
      background: white;
      padding: 20px;
      border-radius: 8px;
      text-align: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      border-left: 4px solid #2196F3;
    }

    .stat-item.success {
      border-left-color: #4CAF50;
    }

    .stat-number {
      font-size: 2em;
      font-weight: bold;
      color: #333;
      margin-bottom: 5px;
    }

    .stat-label {
      color: #666;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .applications-list {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .loading-card, .empty-state, .error-card {
      background: white;
      padding: 60px 20px;
      border-radius: 12px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #2196F3;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .empty-icon {
      font-size: 4em;
      margin-bottom: 20px;
    }

    .application-card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      overflow: hidden;
      transition: box-shadow 0.2s;
    }

    .application-card:hover {
      box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }

    .application-card.status-accepted {
      border-left: 4px solid #4CAF50;
    }

    .application-card.status-interview {
      border-left: 4px solid #FF9800;
    }

    .application-card.status-rejected {
      border-left: 4px solid #f44336;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 20px 25px 15px;
      gap: 20px;
      flex-wrap: wrap;
    }

    .application-id {
      margin: 0 0 8px 0;
      color: #333;
      font-size: 1.3em;
    }

    .application-details {
      color: #666;
      font-size: 14px;
    }

    .card-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .status-management {
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 220px;
    }

    .status-inputs {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .status-select {
      padding: 6px 8px;
      border-radius: 6px;
      border: 1px solid #ddd;
      font-size: 13px;
      min-width: 160px;
      background: white;
    }

    .status-select:focus {
      outline: none;
      border-color: #2196F3;
      box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.15);
    }

    .status-select:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }

    .status-feedback {
      display: flex;
      gap: 10px;
      align-items: center;
      min-height: 18px;
    }

    .status-loading {
      font-size: 12px;
      color: #555;
    }

    .status-error {
      font-size: 12px;
      color: #d32f2f;
    }

    .status-badge {
      padding: 6px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: bold;
      text-transform: uppercase;
    }

    .badge-applied { background: #e3f2fd; color: #1976d2; }
    .badge-acknowledged { background: #e8f5e8; color: #388e3c; }
    .badge-screening { background: #fff3e0; color: #f57c00; }
    .badge-interview { background: #fff3e0; color: #f57c00; }
    .badge-technical_test { background: #f3e5f5; color: #7b1fa2; }
    .badge-offer { background: #e0f2f1; color: #00796b; }
    .badge-rejected { background: #ffebee; color: #d32f2f; }
    .badge-accepted { background: #e8f5e8; color: #388e3c; }
    .badge-withdrawn { background: #f5f5f5; color: #666; }

    .action-buttons {
      display: flex;
      gap: 5px;
    }

    .btn-icon {
      width: 32px;
      height: 32px;
      border: none;
      background: #f5f5f5;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color 0.2s;
    }

    .btn-icon:hover {
      background: #e0e0e0;
    }

    .card-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      padding: 0 25px 15px;
      font-size: 14px;
      color: #666;
    }

    .meta-item.priority-high {
      color: #d32f2f;
      font-weight: 500;
    }

    .meta-item.priority-medium {
      color: #f57c00;
      font-weight: 500;
    }

    .meta-item.priority-low {
      color: #388e3c;
      font-weight: 500;
    }

    .card-details {
      padding: 20px 25px;
      border-top: 1px solid #f0f0f0;
      background: #fafafa;
    }

    .detail-section {
      margin-bottom: 15px;
      display: flex;
      align-items: flex-start;
      gap: 10px;
      flex-wrap: wrap;
    }

    .detail-section:last-child {
      margin-bottom: 0;
    }

    .detail-section strong {
      min-width: 150px;
      color: #333;
    }

    .notes-text {
      margin: 0;
      line-height: 1.5;
      white-space: pre-wrap;
      flex: 1;
    }

    .detail-actions {
      margin-top: 20px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    @media (max-width: 768px) {
      .applications-container {
        padding: 15px;
      }

      .page-header {
        flex-direction: column;
        align-items: stretch;
      }

      .stats-grid {
        grid-template-columns: repeat(2, 1fr);
      }

      .card-header {
        flex-direction: column;
        align-items: stretch;
        gap: 15px;
      }

      .card-actions {
        justify-content: space-between;
      }

      .status-management {
        width: 100%;
      }

      .status-inputs {
        justify-content: space-between;
      }

      .detail-section {
        flex-direction: column;
        align-items: stretch;
      }

      .detail-section strong {
        min-width: auto;
      }
    }
  `]
})
export class JobApplicationsListComponent implements OnInit {
  jobApplications: JobApplication[] = [];
  loading = true;
  error: string | null = null;
  expandedApplications = signal(new Set<string>());
  readonly statusOptions: JobApplication['status'][] = [
    'APPLIED',
    'ACKNOWLEDGED',
    'SCREENING',
    'INTERVIEW',
    'TECHNICAL_TEST',
    'OFFER',
    'ACCEPTED',
    'REJECTED',
    'WITHDRAWN'
  ];
  pendingStatusUpdates = signal(new Set<string>());
  statusUpdateErrors = signal<Record<string, string>>({});

  constructor(private jobApplicationService: JobApplicationService) {}

  ngOnInit() {
    this.loadJobApplications();
  }

  loadJobApplications() {
    this.loading = true;
    this.error = null;
    
    console.log('🔍 Loading job applications...');
    
    this.jobApplicationService.getJobApplications().subscribe({
      next: (applications) => {
        console.log('✅ Job applications received:', applications);
        console.log('📝 Number of applications:', applications?.length || 0);
        
        this.jobApplications = applications || [];
        this.loading = false;
      },
      error: (error) => {
        console.error('❌ Error loading job applications:', error);
        this.error = 'Erreur lors du chargement des candidatures';
        this.loading = false;
        
        // Données de démonstration en cas d'erreur
        this.loading = false;
      }
    });
  }

  onStatusChange(application: JobApplication, event: Event) {
    const selectElement = event.target as HTMLSelectElement | null;
    if (!selectElement) {
      return;
    }

    const newStatus = selectElement.value as JobApplication['status'];
    if (!newStatus || application.status === newStatus || this.isStatusUpdating(application.id)) {
      return;
    }

    const index = this.jobApplications.findIndex(app => app.id === application.id);
    if (index === -1) {
      return;
    }

    const previousApplication = { ...this.jobApplications[index] };
    const optimisticApplication = { ...previousApplication, status: newStatus };

    this.updateJobApplicationsArray(index, optimisticApplication);
    this.setStatusError(application.id, null);
    this.setPendingStatus(application.id, true);

    this.jobApplicationService.updateStatus(application.id, newStatus).subscribe({
      next: (updatedApplication) => {
        const merged = { ...optimisticApplication, ...updatedApplication };
        this.updateJobApplicationsArray(index, merged);
        this.setStatusError(application.id, null);
      },
      error: (err) => {
        console.error('Erreur lors de la mise à jour du statut:', err);
        this.updateJobApplicationsArray(index, previousApplication);
        this.setStatusError(application.id, 'Impossible de mettre à jour le statut pour le moment.');
        selectElement.value = previousApplication.status;
        this.setPendingStatus(application.id, false);
      },
      complete: () => {
        this.setPendingStatus(application.id, false);
      }
    });
  }

  isStatusUpdating(applicationId: string): boolean {
    return this.pendingStatusUpdates().has(applicationId);
  }

  deleteApplication(id: string) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette candidature ?')) {
      this.jobApplicationService.deleteJobApplication(id).subscribe({
        next: () => {
          this.jobApplications = this.jobApplications.filter(app => app.id !== id);
        },
        error: (error) => {
          console.error('Erreur lors de la suppression:', error);
          alert('Erreur lors de la suppression de la candidature');
        }
      });
    }
  }

  getApplicationsByStatus(status: string): JobApplication[] {
    return this.jobApplications.filter(app => app.status === status);
  }

  getStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'APPLIED': '📤 Envoyée',
      'ACKNOWLEDGED': '✅ Reçue',
      'SCREENING': '🔍 Sélection',
      'INTERVIEW': '💼 Entretien',
      'TECHNICAL_TEST': '🧪 Test technique',
      'OFFER': '💰 Offre',
      'REJECTED': '❌ Refusée',
      'ACCEPTED': '🎉 Acceptée',
      'WITHDRAWN': '🚫 Retirée'
    };
    return labels[status] || status;
  }

  getPriorityIcon(priority: string): string {
    const icons: { [key: string]: string } = {
      'HIGH': '🔴',
      'MEDIUM': '🟡',
      'LOW': '🟢'
    };
    return icons[priority] || '⚪';
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'Non défini';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
  }

  toggleApplicationDetails(applicationId: string) {
    const expanded = this.expandedApplications();
    if (expanded.has(applicationId)) {
      expanded.delete(applicationId);
    } else {
      expanded.add(applicationId);
    }
    this.expandedApplications.set(new Set(expanded));
  }

 

  getStatusBadgeClass(status: string): string {
    const statusClasses: { [key: string]: string } = {
      'pending': 'badge pending',
      'applied': 'badge applied',
      'interview': 'badge interview',
      'rejected': 'badge rejected',
      'accepted': 'badge accepted'
    };
    return statusClasses[status] || 'badge';
  }

  private updateJobApplicationsArray(index: number, updatedApplication: JobApplication) {
    this.jobApplications = [
      ...this.jobApplications.slice(0, index),
      updatedApplication,
      ...this.jobApplications.slice(index + 1)
    ];
  }

  private setPendingStatus(applicationId: string, updating: boolean) {
    const current = new Set(this.pendingStatusUpdates());
    if (updating) {
      current.add(applicationId);
    } else {
      current.delete(applicationId);
    }
    this.pendingStatusUpdates.set(current);
  }

  private setStatusError(applicationId: string, message: string | null) {
    const current = { ...this.statusUpdateErrors() };
    if (message) {
      current[applicationId] = message;
    } else {
      delete current[applicationId];
    }
    this.statusUpdateErrors.set(current);
  }
}
