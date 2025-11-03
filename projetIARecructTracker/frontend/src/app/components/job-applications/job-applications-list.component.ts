import { Component, OnInit, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { JobApplicationService } from '../../services/job-application.service';
import { JobApplication } from '../../models';

@Component({
  selector: 'app-job-applications-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
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
        <div class="filters-toolbar">
          <div class="search-field">
            <span class="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Rechercher une candidature (poste, entreprise, notes...)"
              [ngModel]="searchTerm()"
              (ngModelChange)="onSearchChange($event)"
            />
            @if (searchTerm()) {
              <button class="clear-button" (click)="searchTerm.set('')">✕</button>
            }
          </div>
          <div class="filter-chips">
            @for (option of statusFilterOptions; track option.value) {
              <button
                class="filter-chip"
                [class.active]="activeStatusFilter() === option.value"
                (click)="setStatusFilter(option.value)">
                {{ option.label }}
                <span class="chip-count">{{ getFilterCount(option.value) }}</span>
              </button>
            }
            <button class="reset-filters" (click)="resetFilters()">Réinitialiser</button>
          </div>
        </div>

        <div class="bulk-actions" *ngIf="jobApplications.length">
          <span>{{ getFilteredApplications().length }} résultat(s)</span>
          <button 
            class="btn btn-sm btn-danger"
            (click)="confirmDeleteFiltered()"
            [disabled]="getFilteredApplications().length === 0">
            🗑️ Supprimer les {{ getFilteredApplications().length }} affichées
          </button>
          <button 
            class="btn btn-sm btn-danger outline"
            (click)="confirmDeleteAll()">
            🧹 Supprimer toutes les candidatures
          </button>
        </div>

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
          @let filtered = getFilteredApplications();
          @if (filtered.length === 0) {
            <div class="empty-state">
              <div class="empty-icon">🔎</div>
              <h3>Aucune candidature ne correspond aux filtres</h3>
              <p>Modifiez votre recherche ou réinitialisez les filtres.</p>
              <button class="btn btn-secondary" (click)="resetFilters()">Réinitialiser les filtres</button>
            </div>
          } @else {
          @let paginated = getPaginatedApplications(filtered);
          @for (application of paginated; track application.id) {
            <div class="application-card" [class]="'status-' + application.status.toLowerCase()">
              <div class="card-header">
                <div class="card-title-section">
                  <h3 class="application-id">
                    {{ getApplicationTitle(application) }}
                  </h3>
                  <div class="application-info">
                    <span class="application-details">
                      {{ application.company_name || 'Entreprise inconnue' }}
                    </span>
                    @if (application.source) {
                      <span class="application-source">• {{ application.source }}</span>
                    }
                  </div>
                </div>
                <div class="card-actions">
                  <div class="status-management">
                    <div class="status-inputs">
                      <span [ngClass]="getStatusBadgeClass(application.status)">
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
                    <button class="btn btn-sm btn-danger" (click)="deleteApplication(application.id)">
                      🗑️ Supprimer
                    </button>
                  </div>
                </div>
              }
            </div>
          }
          <div class="pagination" *ngIf="filtered.length > pageSize">
            <button class="page-btn" (click)="prevPage()" [disabled]="currentPage() === 1">←</button>
            <span class="page-info">Page {{ currentPage() }} / {{ totalPages() }}</span>
            <button class="page-btn" (click)="nextPage()" [disabled]="currentPage() === totalPages()">→</button>
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

    .filters-toolbar {
      display: flex;
      flex-direction: column;
      gap: 15px;
      background: #fff;
      padding: 16px 20px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
    }

    .bulk-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
      background: #fff;
      padding: 12px 20px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
      font-size: 14px;
      color: #4b5563;
    }

    .btn.btn-sm.btn-danger {
      background: #dc2626;
      color: #fff;
    }

    .btn.btn-sm.btn-danger.outline {
      background: #fff;
      color: #dc2626;
      border: 1px solid #fca5a5;
    }

    .search-field {
      position: relative;
      display: flex;
      align-items: center;
      background: #f9fafb;
      border-radius: 10px;
      padding: 8px 12px;
      border: 1px solid #e5e7eb;
    }

    .search-field input {
      border: none;
      background: transparent;
      flex: 1;
      padding: 4px 8px;
      font-size: 14px;
      outline: none;
      color: #1f2933;
    }

    .search-icon {
      font-size: 16px;
      color: #6b7280;
    }

    .clear-button {
      border: none;
      background: transparent;
      color: #9ca3af;
      cursor: pointer;
      font-size: 16px;
      padding: 0 4px;
    }

    .filter-chips {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .filter-chip {
      border: 1px solid #e5e7eb;
      background: #fff;
      color: #374151;
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .filter-chip.active {
      background: #1d4ed8;
      border-color: #1d4ed8;
      color: #fff;
      box-shadow: 0 4px 12px rgba(29, 78, 216, 0.25);
    }

    .chip-count {
      background: rgba(255,255,255,0.2);
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 11px;
    }

    .filter-chip.active .chip-count {
      background: rgba(255,255,255,0.25);
    }

    .reset-filters {
      border: none;
      background: transparent;
      color: #2563eb;
      font-weight: 600;
      cursor: pointer;
      padding: 6px 12px;
    }

    .loading-card, .empty-state, .error-card {
      background: white;
      padding: 60px 20px;
      border-radius: 12px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .pagination {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      margin-top: 20px;
    }

    .page-btn {
      border: none;
      background: #2563eb;
      color: #fff;
      width: 36px;
      height: 36px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s;
    }

    .page-btn:disabled {
      background: #cbd5f5;
      cursor: not-allowed;
    }

    .page-info {
      font-size: 14px;
      color: #4b5563;
      font-weight: 600;
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

    .application-info {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      color: #666;
      font-size: 14px;
    }

    .application-source {
      font-size: 12px;
      color: #999;
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
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 16px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
    }

    .status-badge.applied { background: #e3f2fd; color: #1d4ed8; }
    .status-badge.acknowledged { background: #f5f3ff; color: #5b21b6; }
    .status-badge.screening { background: #fff7ed; color: #c2410c; }
    .status-badge.interview { background: #e0f2fe; color: #0369a1; }
    .status-badge.test { background: #fce7f3; color: #be185d; }
    .status-badge.offer { background: #dcfce7; color: #15803d; }
    .status-badge.rejected { background: #fee2e2; color: #b91c1c; }
    .status-badge.accepted { background: #ecfdf5; color: #047857; }
    .status-badge.withdrawn { background: #f8fafc; color: #475569; }
    .status-badge.on-hold { background: #fef3c7; color: #b45309; }

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
  readonly statusFilterOptions: Array<{ value: JobApplication['status'] | 'ALL' | 'AUTO' | 'MANUAL', label: string }> = [
    { value: 'ALL', label: 'Toutes' },
    { value: 'AUTO', label: 'Créées par IA' },
    { value: 'MANUAL', label: 'Créées manuellement' },
    { value: 'ACKNOWLEDGED', label: 'Reçues' },
    { value: 'APPLIED', label: 'Envoyées' },
    { value: 'SCREENING', label: 'Sélection' },
    { value: 'INTERVIEW', label: 'Entretiens' },
    { value: 'OFFER', label: 'Offres' },
    { value: 'ACCEPTED', label: 'Acceptées' },
    { value: 'REJECTED', label: 'Refusées' }
  ];
  pendingStatusUpdates = signal(new Set<string>());
  statusUpdateErrors = signal<Record<string, string>>({});
  searchTerm = signal('');
  activeStatusFilter = signal<JobApplication['status'] | 'ALL' | 'AUTO' | 'MANUAL'>('ALL');
  showOnlyAuto = signal(false);
  currentPage = signal(1);
  readonly pageSize = 10;
  totalPages = computed(() => {
    const filteredLength = this.getFilteredApplications().length;
    return Math.max(1, Math.ceil(filteredLength / this.pageSize));
  });

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
        
        this.jobApplications = (applications || []).sort((a, b) => {
          const dateA = new Date(a.applied_date || a.created_at || a.updated_at || 0).getTime();
          const dateB = new Date(b.applied_date || b.created_at || b.updated_at || 0).getTime();
          return dateB - dateA;
        });
        this.currentPage.set(1);
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

  deleteApplication(id: string, skipConfirmation: boolean = false) {
    if (!skipConfirmation && !confirm('Êtes-vous sûr de vouloir supprimer cette candidature ?')) {
      return;
    }

    this.jobApplicationService.deleteJobApplication(id).subscribe({
      next: () => {
        this.jobApplications = this.jobApplications.filter(app => app.id !== id);
        this.ensureValidPage();
      },
      error: (error) => {
        console.error('Erreur lors de la suppression:', error);
        alert('Erreur lors de la suppression de la candidature');
      }
    });
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

  getFilteredApplications(): JobApplication[] {
    const term = this.normalize(this.searchTerm());
    const filter = this.activeStatusFilter();
    return this.jobApplications.filter(app => {
      const matchesSearch = !term || this.normalize(app.job_title).includes(term) ||
        this.normalize(app.company_name).includes(term) ||
        this.normalize(app.notes).includes(term);
      
      const matchesStatus = filter === 'ALL'
        ? true
        : filter === 'AUTO'
          ? this.isAutoCreated(app)
          : filter === 'MANUAL'
            ? !this.isAutoCreated(app)
            : app.status === filter;

      return matchesSearch && matchesStatus;
    });
  }

  getPaginatedApplications(filtered: JobApplication[]): JobApplication[] {
    const total = Math.max(1, Math.ceil(filtered.length / this.pageSize));
    if (this.currentPage() > total) {
      this.currentPage.set(total);
    }
    if (this.currentPage() < 1) {
      this.currentPage.set(1);
    }

    const start = (this.currentPage() - 1) * this.pageSize;
    return filtered.slice(start, start + this.pageSize);
  }

  nextPage() {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage.set(this.currentPage() + 1);
    }
  }

  prevPage() {
    if (this.currentPage() > 1) {
      this.currentPage.set(this.currentPage() - 1);
    }
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
    }
  }

  setStatusFilter(filter: JobApplication['status'] | 'ALL' | 'AUTO' | 'MANUAL') {
    this.activeStatusFilter.set(filter);
    this.currentPage.set(1);
  }

  normalize(value: string | null | undefined): string {
    return (value || '').trim().toLowerCase();
  }

  getFilterCount(filter: JobApplication['status'] | 'ALL' | 'AUTO' | 'MANUAL'): number {
    switch (filter) {
      case 'ALL':
        return this.jobApplications.length;
      case 'AUTO':
        return this.jobApplications.filter(app => this.isAutoCreated(app)).length;
      case 'MANUAL':
        return this.jobApplications.filter(app => !this.isAutoCreated(app)).length;
      default:
        return this.jobApplications.filter(app => app.status === filter).length;
    }
  }

  resetFilters() {
    this.searchTerm.set('');
    this.activeStatusFilter.set('ALL');
    this.currentPage.set(1);
  }

  onSearchChange(value: string) {
    this.searchTerm.set(value ?? '');
    this.currentPage.set(1);
  }

  confirmDeleteFiltered() {
    const filtered = this.getFilteredApplications();
    if (!filtered.length) {
      return;
    }

    if (!confirm(`Supprimer ${filtered.length} candidature(s) affichée(s) ?`)) {
      return;
    }

    const idsToDelete = new Set(filtered.map(app => app.id));
    filtered.forEach(app => this.deleteApplication(app.id, true));
    this.jobApplications = this.jobApplications.filter(app => !idsToDelete.has(app.id));
    this.ensureValidPage(true);
  }

  confirmDeleteAll() {
    if (!this.jobApplications.length) {
      return;
    }

    if (!confirm('Supprimer toutes les candidatures ? Cette action est irréversible.')) {
      return;
    }

    this.jobApplications.forEach(app => this.jobApplicationService.deleteJobApplication(app.id).subscribe());
    this.jobApplications = [];
    this.currentPage.set(1);
  }

  isAutoCreated(app: JobApplication): boolean {
    const source = this.normalize(app.source);
    const autoTokens = ['auto', 'détect', 'ia', 'automatique', 'machine'];
    return autoTokens.some(token => source.includes(token));
  }

  getPriorityIcon(priority: string): string {
    const icons: { [key: string]: string } = {
      'HIGH': '🔴',
      'MEDIUM': '🟡',
      'LOW': '🟢'
    };
    return icons[priority] || '⚪';
  }

  formatDate(dateInput: string | Date | undefined): string {
    if (!dateInput) return 'Non défini';
    const date = dateInput instanceof Date ? dateInput : new Date(dateInput);
    return date.toLocaleDateString('fr-FR');
  }

  getApplicationTitle(app: JobApplication): string {
    const rawTitle = (app.job_title || '').trim();
    if (rawTitle && !this.isPlaceholderTitle(rawTitle)) {
      return rawTitle;
    }

    if (app.notes) {
      const subjectMatch = app.notes.match(/email:\s*(.+)/i);
      if (subjectMatch && subjectMatch[1]) {
        return subjectMatch[1].trim().slice(0, 120) || 'Candidature';
      }
      const firstLine = app.notes.split('\n').find(line => line.trim());
      if (firstLine) {
        return firstLine.trim().slice(0, 120) || 'Candidature';
      }
    }

    if (app.company_name) {
      return `Candidature ${app.company_name}`.trim();
    }

    if (app.source) {
      return app.source.trim();
    }

    return 'Candidature';
  }

  private isPlaceholderTitle(title: string): boolean {
    const normalized = this.normalize(title).replace(/é/g, 'e').replace(/è/g, 'e');
    return normalized === 'poste non specifie' ||
      normalized === 'candidature' ||
      normalized === 'candidature automatique';
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
    const normalized = this.normalize(status);
    const statusClasses: { [key: string]: string } = {
      'applied': 'status-badge applied',
      'acknowledged': 'status-badge acknowledged',
      'screening': 'status-badge screening',
      'interview': 'status-badge interview',
      'technical_test': 'status-badge test',
      'offer': 'status-badge offer',
      'rejected': 'status-badge rejected',
      'accepted': 'status-badge accepted',
      'withdrawn': 'status-badge withdrawn',
      'on_hold': 'status-badge on-hold'
    };
    return statusClasses[normalized] || 'status-badge';
  }

  private updateJobApplicationsArray(index: number, updatedApplication: JobApplication) {
    this.jobApplications = [
      ...this.jobApplications.slice(0, index),
      updatedApplication,
      ...this.jobApplications.slice(index + 1)
    ];
    this.ensureValidPage();
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

  private ensureValidPage(forceFirst: boolean = false) {
    if (forceFirst) {
      this.currentPage.set(1);
      return;
    }
    const total = this.totalPages();
    if (this.currentPage() > total) {
      this.currentPage.set(total);
    }
    if (this.currentPage() < 1) {
      this.currentPage.set(1);
    }
  }
}
