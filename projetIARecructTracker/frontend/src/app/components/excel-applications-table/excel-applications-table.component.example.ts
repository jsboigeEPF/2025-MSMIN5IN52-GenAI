/**
 * 📊 EXEMPLE D'UTILISATION DU STYLE EXCEL
 * 
 * Ce fichier montre comment intégrer le style Excel professionnel
 * dans un composant Angular standalone
 */

import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Application {
  id: string;
  company_name: string;
  job_title: string;
  status: string;
  location?: string;
  salary_range?: string;
  contract_type?: string;
  applied_date: string;
  last_update: string;
  priority?: 'high' | 'medium' | 'low';
}

@Component({
  selector: 'app-excel-applications-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  styleUrls: ['./../../styles/excel-table.css'],
  template: `
    <div class="excel-container">
      
      <!-- 📊 Statistiques -->
      <div class="excel-stats">
        <div class="stat-card">
          <div class="stat-label">Total Candidatures</div>
          <div class="stat-value">
            {{ applications().length }}
            <span class="stat-change">+{{ newThisMonth() }} ce mois</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-label">Entretiens</div>
          <div class="stat-value">
            {{ interviewCount() }}
            <span class="stat-change">{{ pendingInterviews() }} en attente</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-label">Offres</div>
          <div class="stat-value">
            {{ offerCount() }}
            <span class="stat-change">🎉</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-label">Taux de réponse</div>
          <div class="stat-value">
            {{ responseRate() }}%
            <span class="stat-change">↑ {{ rateChange() }}%</span>
          </div>
        </div>
      </div>

      <!-- 🔧 Barre d'outils -->
      <div class="excel-toolbar">
        <div class="toolbar-left">
          <button class="excel-button primary" (click)="createApplication()">
            ➕ Nouvelle candidature
          </button>
          <button class="excel-button success" (click)="syncGmail()">
            📧 Synchroniser Gmail
          </button>
          <button class="excel-button" (click)="exportToExcel()">
            📥 Exporter Excel
          </button>
        </div>
        
        <div class="toolbar-right">
          <div class="excel-search">
            <input 
              type="text" 
              placeholder="Rechercher..." 
              [(ngModel)]="searchQuery"
              (input)="onSearchChange()">
            <span class="excel-search-icon">🔍</span>
          </div>
        </div>
      </div>

      <!-- 🔍 Filtres avancés -->
      <div class="excel-filters">
        <div class="filter-group">
          <label class="filter-label">Statut</label>
          <select 
            class="filter-select" 
            [(ngModel)]="filterStatus"
            (change)="applyFilters()">
            <option value="">Tous les statuts</option>
            <option value="APPLIED">Envoyée</option>
            <option value="ACKNOWLEDGED">Reçue</option>
            <option value="SCREENING">En cours</option>
            <option value="INTERVIEW">Entretien</option>
            <option value="OFFER">Offre</option>
            <option value="REJECTED">Refusée</option>
            <option value="ON_HOLD">En attente</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Priorité</label>
          <select 
            class="filter-select" 
            [(ngModel)]="filterPriority"
            (change)="applyFilters()">
            <option value="">Toutes</option>
            <option value="high">Haute</option>
            <option value="medium">Moyenne</option>
            <option value="low">Basse</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Type de contrat</label>
          <select 
            class="filter-select" 
            [(ngModel)]="filterContract"
            (change)="applyFilters()">
            <option value="">Tous</option>
            <option value="CDI">CDI</option>
            <option value="CDD">CDD</option>
            <option value="Stage">Stage</option>
            <option value="Alternance">Alternance</option>
            <option value="Freelance">Freelance</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Trier par</label>
          <select 
            class="filter-select" 
            [(ngModel)]="sortColumn"
            (change)="applySorting()">
            <option value="last_update">Date de mise à jour</option>
            <option value="applied_date">Date de candidature</option>
            <option value="company_name">Entreprise</option>
            <option value="job_title">Poste</option>
            <option value="status">Statut</option>
          </select>
        </div>
        
        <button class="excel-button" (click)="resetFilters()">
          🔄 Réinitialiser
        </button>
      </div>

      <!-- 📋 Tableau Excel -->
      <div class="excel-table-wrapper">
        <table class="excel-table">
          <thead>
            <tr>
              <th 
                class="sortable"
                [class.sort-asc]="sortColumn === 'company_name' && sortDirection === 'asc'"
                [class.sort-desc]="sortColumn === 'company_name' && sortDirection === 'desc'"
                (click)="sortBy('company_name')">
                Entreprise
              </th>
              <th 
                class="sortable"
                [class.sort-asc]="sortColumn === 'job_title' && sortDirection === 'asc'"
                [class.sort-desc]="sortColumn === 'job_title' && sortDirection === 'desc'"
                (click)="sortBy('job_title')">
                Poste
              </th>
              <th 
                class="sortable"
                [class.sort-asc]="sortColumn === 'status' && sortDirection === 'asc'"
                [class.sort-desc]="sortColumn === 'status' && sortDirection === 'desc'"
                (click)="sortBy('status')">
                Statut
              </th>
              <th class="sortable" (click)="sortBy('location')">
                Localisation
              </th>
              <th class="sortable" (click)="sortBy('salary_range')">
                Salaire
              </th>
              <th class="sortable" (click)="sortBy('contract_type')">
                Contrat
              </th>
              <th 
                class="sortable"
                [class.sort-asc]="sortColumn === 'applied_date' && sortDirection === 'asc'"
                [class.sort-desc]="sortColumn === 'applied_date' && sortDirection === 'desc'"
                (click)="sortBy('applied_date')">
                Date candidature
              </th>
              <th class="sortable" (click)="sortBy('last_update')">
                Dernière MAJ
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          
          <tbody>
            @if (paginatedApplications().length === 0) {
              <tr>
                <td colspan="9" class="excel-empty-state">
                  <div class="excel-empty-state-icon">📭</div>
                  <div class="excel-empty-state-title">Aucune candidature</div>
                  <div class="excel-empty-state-text">
                    Commencez par ajouter une nouvelle candidature ou synchronisez vos emails Gmail.
                  </div>
                  <button class="excel-button primary" (click)="createApplication()">
                    ➕ Créer une candidature
                  </button>
                </td>
              </tr>
            }
            
            @for (app of paginatedApplications(); track app.id) {
              <tr 
                [class.selected]="selectedId() === app.id"
                (click)="selectRow(app.id)">
                
                <td class="excel-cell-company">
                  {{ app.company_name || 'N/A' }}
                </td>
                
                <td class="excel-cell-job-title" [attr.data-tooltip]="app.job_title">
                  {{ app.job_title || 'Poste non spécifié' }}
                </td>
                
                <td>
                  <span 
                    class="excel-badge"
                    [ngClass]="'status-' + app.status.toLowerCase()">
                    {{ getStatusLabel(app.status) }}
                  </span>
                  @if (app.priority) {
                    <span 
                      class="excel-badge"
                      [ngClass]="'priority-' + app.priority"
                      style="margin-left: 4px;">
                      {{ getPriorityLabel(app.priority) }}
                    </span>
                  }
                </td>
                
                <td class="excel-cell-location">
                  @if (app.location) {
                    📍 {{ app.location }}
                  } @else {
                    <span style="color: #adb5bd;">Non spécifié</span>
                  }
                </td>
                
                <td class="excel-cell-salary">
                  {{ app.salary_range || '-' }}
                </td>
                
                <td>
                  <span class="excel-badge" *ngIf="app.contract_type">
                    {{ app.contract_type }}
                  </span>
                  <span *ngIf="!app.contract_type" style="color: #adb5bd;">-</span>
                </td>
                
                <td class="excel-cell-date">
                  {{ formatDate(app.applied_date) }}
                </td>
                
                <td class="excel-cell-date">
                  {{ formatDate(app.last_update) }}
                </td>
                
                <td class="excel-cell-actions">
                  <button 
                    class="excel-action-btn" 
                    (click)="viewDetails($event, app.id)"
                    data-tooltip="Voir les détails">
                    👁️
                  </button>
                  <button 
                    class="excel-action-btn" 
                    (click)="editApplication($event, app.id)"
                    data-tooltip="Éditer">
                    ✏️
                  </button>
                  <button 
                    class="excel-action-btn danger" 
                    (click)="deleteApplication($event, app.id)"
                    data-tooltip="Supprimer">
                    🗑️
                  </button>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>

      <!-- 📄 Pagination -->
      <div class="excel-pagination">
        <div class="pagination-info">
          Affichage {{ startIndex() }}-{{ endIndex() }} sur {{ filteredApplications().length }} candidatures
        </div>
        
        <div class="pagination-controls">
          <button 
            class="pagination-btn"
            [disabled]="currentPage() === 1"
            (click)="goToPage(currentPage() - 1)">
            ‹ Précédent
          </button>
          
          @for (page of visiblePages(); track page) {
            <button 
              class="pagination-btn"
              [class.active]="page === currentPage()"
              (click)="goToPage(page)">
              {{ page }}
            </button>
          }
          
          <button 
            class="pagination-btn"
            [disabled]="currentPage() === totalPages()"
            (click)="goToPage(currentPage() + 1)">
            Suivant ›
          </button>
        </div>
      </div>
    </div>
  `
})
export class ExcelApplicationsTableComponent implements OnInit {
  // Signals pour la réactivité
  applications = signal<Application[]>([]);
  filteredApplications = signal<Application[]>([]);
  selectedId = signal<string | null>(null);
  
  // Filtres
  searchQuery = '';
  filterStatus = '';
  filterPriority = '';
  filterContract = '';
  
  // Tri
  sortColumn = 'last_update';
  sortDirection: 'asc' | 'desc' = 'desc';
  
  // Pagination
  currentPage = signal(1);
  pageSize = 10;
  
  // Computed values
  totalPages = computed(() => 
    Math.ceil(this.filteredApplications().length / this.pageSize)
  );
  
  paginatedApplications = computed(() => {
    const start = (this.currentPage() - 1) * this.pageSize;
    const end = start + this.pageSize;
    return this.filteredApplications().slice(start, end);
  });
  
  startIndex = computed(() => 
    (this.currentPage() - 1) * this.pageSize + 1
  );
  
  endIndex = computed(() => 
    Math.min(this.currentPage() * this.pageSize, this.filteredApplications().length)
  );
  
  visiblePages = computed(() => {
    const total = this.totalPages();
    const current = this.currentPage();
    const pages: number[] = [];
    
    // Toujours afficher la première page
    pages.push(1);
    
    // Pages autour de la page courante
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
      if (!pages.includes(i)) pages.push(i);
    }
    
    // Toujours afficher la dernière page
    if (total > 1 && !pages.includes(total)) {
      pages.push(total);
    }
    
    return pages;
  });
  
  // Stats
  newThisMonth = computed(() => {
    const now = new Date();
    const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    return this.applications().filter(app => 
      new Date(app.applied_date) >= firstDayOfMonth
    ).length;
  });
  
  interviewCount = computed(() =>
    this.applications().filter(app => app.status === 'INTERVIEW').length
  );
  
  pendingInterviews = computed(() =>
    this.applications().filter(app => 
      app.status === 'INTERVIEW' && new Date(app.last_update) > new Date()
    ).length
  );
  
  offerCount = computed(() =>
    this.applications().filter(app => app.status === 'OFFER').length
  );
  
  responseRate = computed(() => {
    const total = this.applications().length;
    const responded = this.applications().filter(app => 
      app.status !== 'APPLIED'
    ).length;
    return total > 0 ? Math.round((responded / total) * 100) : 0;
  });
  
  rateChange = computed(() => {
    // Calcul simplifié du changement de taux
    return Math.floor(Math.random() * 20) - 10; // Mock
  });

  ngOnInit() {
    this.loadApplications();
  }

  loadApplications() {
    // TODO: Appeler le service pour récupérer les candidatures
    // this.jobApplicationService.getJobApplications().subscribe(apps => {
    //   this.applications.set(apps);
    //   this.applyFilters();
    // });
  }

  onSearchChange() {
    this.applyFilters();
  }

  applyFilters() {
    let filtered = [...this.applications()];
    
    // Recherche textuelle
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(app =>
        app.company_name?.toLowerCase().includes(query) ||
        app.job_title?.toLowerCase().includes(query) ||
        app.location?.toLowerCase().includes(query)
      );
    }
    
    // Filtre statut
    if (this.filterStatus) {
      filtered = filtered.filter(app => app.status === this.filterStatus);
    }
    
    // Filtre priorité
    if (this.filterPriority) {
      filtered = filtered.filter(app => app.priority === this.filterPriority);
    }
    
    // Filtre contrat
    if (this.filterContract) {
      filtered = filtered.filter(app => app.contract_type === this.filterContract);
    }
    
    this.filteredApplications.set(filtered);
    this.applySorting();
    this.currentPage.set(1); // Reset à la page 1
  }

  sortBy(column: string) {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.applySorting();
  }

  applySorting() {
    const sorted = [...this.filteredApplications()].sort((a, b) => {
      const aVal = a[this.sortColumn as keyof Application] || '';
      const bVal = b[this.sortColumn as keyof Application] || '';
      
      const comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
      return this.sortDirection === 'asc' ? comparison : -comparison;
    });
    
    this.filteredApplications.set(sorted);
  }

  resetFilters() {
    this.searchQuery = '';
    this.filterStatus = '';
    this.filterPriority = '';
    this.filterContract = '';
    this.applyFilters();
  }

  selectRow(id: string) {
    this.selectedId.set(id);
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
    }
  }

  // Actions
  createApplication() {
    console.log('Créer nouvelle candidature');
    // TODO: Implémenter
  }

  syncGmail() {
    console.log('Synchroniser Gmail');
    // TODO: Implémenter
  }

  exportToExcel() {
    console.log('Exporter vers Excel');
    // TODO: Implémenter export CSV/Excel
  }

  viewDetails(event: Event, id: string) {
    event.stopPropagation();
    console.log('Voir détails:', id);
    // TODO: Naviguer vers page détails
  }

  editApplication(event: Event, id: string) {
    event.stopPropagation();
    console.log('Éditer:', id);
    // TODO: Ouvrir modal/page édition
  }

  deleteApplication(event: Event, id: string) {
    event.stopPropagation();
    if (confirm('Êtes-vous sûr de vouloir supprimer cette candidature ?')) {
      console.log('Supprimer:', id);
      // TODO: Appeler service de suppression
    }
  }

  // Helpers
  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      'APPLIED': 'Envoyée',
      'ACKNOWLEDGED': 'Reçue',
      'SCREENING': 'En cours',
      'INTERVIEW': 'Entretien',
      'OFFER': 'Offre',
      'REJECTED': 'Refusée',
      'ON_HOLD': 'En attente'
    };
    return labels[status] || status;
  }

  getPriorityLabel(priority: string): string {
    const labels: Record<string, string> = {
      'high': '🔥 Haute',
      'medium': '⚡ Moyenne',
      'low': '💤 Basse'
    };
    return labels[priority] || priority;
  }

  formatDate(date: string): string {
    if (!date) return '-';
    const d = new Date(date);
    return d.toLocaleDateString('fr-FR', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric' 
    });
  }
}
