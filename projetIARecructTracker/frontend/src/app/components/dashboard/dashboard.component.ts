import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { JobApplicationService } from '../../services/job-application.service';
import { IntelligentTrackerService, ProcessingSummary } from '../../services/intelligent-tracker.service';

interface DashboardStats {
  totalApplications: number;
  autoCreatedApplications: number;
  manualApplications: number;
  linkedEmails: number;
  unprocessedEmails: number;
  automationRate: number;
  recentApplications: any[];
  applicationsByStatus: { [key: string]: number };
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  Object = Object; // Pour utiliser Object dans le template
  
  stats: DashboardStats = {
    totalApplications: 0,
    autoCreatedApplications: 0,
    manualApplications: 0,
    linkedEmails: 0,
    unprocessedEmails: 0,
    automationRate: 0,
    recentApplications: [],
    applicationsByStatus: {}
  };
  
  loading = true;
  error: string | null = null;

  constructor(
    private jobApplicationService: JobApplicationService,
    private intelligentTrackerService: IntelligentTrackerService
  ) {}

  ngOnInit() {
    this.loadDashboardData();
  }

  private async loadDashboardData() {
    try {
      this.loading = true;
      
      const [applications, summaryResponse] = await Promise.all([
        this.jobApplicationService.getJobApplications().toPromise(),
        this.intelligentTrackerService.getProcessingSummary().toPromise()
      ]);

      const summary = summaryResponse?.data;
      const sortedApplications = (applications || []).slice().sort((a, b) => {
        const dateA = new Date(a.created_at || a.applied_date || a.updated_at || 0).getTime();
        const dateB = new Date(b.created_at || b.applied_date || b.updated_at || 0).getTime();
        return dateB - dateA;
      });

      this.stats = {
        totalApplications: applications?.length || 0,
        autoCreatedApplications: summary?.auto_created_applications || 0,
        manualApplications: summary?.manual_applications || 0,
        linkedEmails: summary?.linked_emails || 0,
        unprocessedEmails: summary?.unprocessed_emails || 0,
        automationRate: summary?.automation_rate || 0,
        recentApplications: sortedApplications.slice(0, 5),
        applicationsByStatus: summary?.status_breakdown || this.getApplicationsByStatus(applications || [])
      };

      this.loading = false;
    } catch (error) {
      console.error('❌ Erreur lors du chargement du dashboard:', error);
      this.error = 'Erreur lors du chargement des données';
      this.loading = false;
    }
  }

  private getApplicationsByStatus(applications: any[]): { [key: string]: number } {
    return applications.reduce((acc, app) => {
      acc[app.status] = (acc[app.status] || 0) + 1;
      return acc;
    }, {});
  }

  getStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'APPLIED': 'Envoyée',
      'ACKNOWLEDGED': 'Réception confirmée',
      'SCREENING': 'En sélection',
      'INTERVIEW': 'Entretien',
      'TECHNICAL_TEST': 'Test technique',
      'OFFER': 'Offre',
      'REJECTED': 'Refusée',
      'ACCEPTED': 'Acceptée',
      'WITHDRAWN': 'Retirée',
      'ON_HOLD': 'En attente'
    };
    return labels[status] || status;
  }

  getStatusBadgeClass(status: string): string {
    const normalized = status?.toLowerCase() || '';
    const statusClasses: { [key: string]: string } = {
      'applied': 'badge applied',
      'acknowledged': 'badge acknowledged',
      'screening': 'badge screening',
      'interview': 'badge interview',
      'technical_test': 'badge test',
      'offer': 'badge offer',
      'rejected': 'badge rejected',
      'accepted': 'badge accepted',
      'withdrawn': 'badge withdrawn',
      'on_hold': 'badge on-hold'
    };
    return statusClasses[normalized] || 'badge';
  }

  formatDate(date: string): string {
    if (!date) {
      return 'N/A';
    }
    return new Date(date).toLocaleDateString('fr-FR');
  }
}
