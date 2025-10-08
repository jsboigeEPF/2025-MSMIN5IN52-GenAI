// Dashboard JavaScript pour interactions avancées
class BiasEvaluationDashboard {
    constructor() {
        this.charts = {};
        this.data = {};
        this.filters = {
            selectedModels: [],
            selectedBiasTypes: []
        };
        this.init();
    }

    async init() {
        try {
            await this.loadData();
            this.setupFilters();
            this.renderCharts();
            this.updateSummaryStats();
            this.setupEventListeners();
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.showError('Erreur lors du chargement des données');
        }
    }

    async loadData() {
        this.showLoading(true);
        try {
            console.log('Starting to load data...');
            
            const [modelsResp, biasResp, resultsResp, summaryResp] = await Promise.all([
                axios.get('/api/models'),
                axios.get('/api/bias_dimensions'),
                axios.get('/api/results'),
                axios.get('/api/summary')
            ]);

            console.log('API responses received:', {
                models: modelsResp.data,
                bias: biasResp.data,
                results: resultsResp.data,
                summary: summaryResp.data
            });

            this.data = {
                models: modelsResp.data.models || [],
                biasDimensions: biasResp.data.dimensions || [],
                results: resultsResp.data,
                summary: summaryResp.data
            };

            console.log('Processed data:', this.data);

            // Initialiser les filtres avec tous les modèles et biais sélectionnés
            this.filters.selectedModels = [...this.data.models];
            this.filters.selectedBiasTypes = [...this.data.biasDimensions];

            console.log('Filters initialized:', this.filters);

        } catch (error) {
            console.error('Error in loadData:', error);
            throw error;
        } finally {
            this.showLoading(false);
        }
    }

    setupFilters() {
        this.renderModelFilters();
        this.renderBiasTypeFilters();
    }

    renderModelFilters() {
        const container = document.getElementById('model-filters');
        if (!container) return;

        container.innerHTML = '';
        this.data.models.forEach(model => {
            const badge = document.createElement('span');
            badge.className = 'model-badge selected';
            badge.textContent = model.toUpperCase();
            badge.dataset.model = model;
            badge.addEventListener('click', () => this.toggleModelFilter(model, badge));
            container.appendChild(badge);
        });
    }

    renderBiasTypeFilters() {
        const container = document.getElementById('bias-type-filters');
        if (!container) return;

        container.innerHTML = '';
        this.data.biasDimensions.forEach(biasType => {
            const badge = document.createElement('span');
            badge.className = 'model-badge selected';
            badge.textContent = biasType.replace('_', ' ').toUpperCase();
            badge.dataset.biasType = biasType;
            badge.addEventListener('click', () => this.toggleBiasTypeFilter(biasType, badge));
            container.appendChild(badge);
        });
    }

    toggleModelFilter(model, element) {
        const index = this.filters.selectedModels.indexOf(model);
        if (index > -1) {
            this.filters.selectedModels.splice(index, 1);
            element.classList.remove('selected');
        } else {
            this.filters.selectedModels.push(model);
            element.classList.add('selected');
        }
        this.updateCharts();
    }

    toggleBiasTypeFilter(biasType, element) {
        const index = this.filters.selectedBiasTypes.indexOf(biasType);
        if (index > -1) {
            this.filters.selectedBiasTypes.splice(index, 1);
            element.classList.remove('selected');
        } else {
            this.filters.selectedBiasTypes.push(biasType);
            element.classList.add('selected');
        }
        this.updateCharts();
    }

    renderCharts() {
        this.renderBiasComparisonChart();
        this.renderModelPerformanceChart();
        this.renderBiasDistributionChart();
        this.renderTrendChart();
    }

    renderBiasComparisonChart() {
        const ctx = document.getElementById('biasComparisonChart');
        if (!ctx) return;

        const datasets = [];
        const labels = this.filters.selectedBiasTypes;

        this.filters.selectedModels.forEach((model, index) => {
            const data = labels.map(biasType => {
                const result = this.data.results[model];
                return result && result[biasType] ? result[biasType].bias_score || 0 : 0;
            });

            datasets.push({
                label: model.toUpperCase(),
                data: data,
                backgroundColor: this.getModelColor(model, 0.7),
                borderColor: this.getModelColor(model, 1),
                borderWidth: 2,
                borderRadius: 4
            });
        });

        if (this.charts.biasComparison) {
            this.charts.biasComparison.destroy();
        }

        this.charts.biasComparison = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.map(label => label.replace('_', ' ').toUpperCase()),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Comparaison des Scores de Biais par Modèle',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        title: {
                            display: true,
                            text: 'Score de Biais (0-1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Types de Biais'
                        }
                    }
                }
            }
        });
    }

    renderModelPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        const datasets = [{
            label: 'Score de Biais Moyen',
            data: this.filters.selectedModels.map(model => {
                const result = this.data.results[model];
                if (!result) return 0;
                
                const scores = this.filters.selectedBiasTypes
                    .map(biasType => result[biasType] ? result[biasType].bias_score || 0 : 0)
                    .filter(score => score > 0);
                
                return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
            }),
            backgroundColor: this.filters.selectedModels.map(model => this.getModelColor(model, 0.7)),
            borderColor: this.filters.selectedModels.map(model => this.getModelColor(model, 1)),
            borderWidth: 2
        }];

        if (this.charts.performance) {
            this.charts.performance.destroy();
        }

        this.charts.performance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.filters.selectedModels.map(model => model.toUpperCase()),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Performance Globale des Modèles',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderBiasDistributionChart() {
        const ctx = document.getElementById('distributionChart');
        if (!ctx) return;

        // Calculer la distribution des scores de biais
        const ranges = ['0-0.1', '0.1-0.3', '0.3-0.5', '0.5-0.7', '0.7-1.0'];
        const distribution = ranges.map(() => 0);

        this.filters.selectedModels.forEach(model => {
            this.filters.selectedBiasTypes.forEach(biasType => {
                const result = this.data.results[model];
                if (result && result[biasType]) {
                    const score = result[biasType].bias_score || 0;
                    if (score < 0.1) distribution[0]++;
                    else if (score < 0.3) distribution[1]++;
                    else if (score < 0.5) distribution[2]++;
                    else if (score < 0.7) distribution[3]++;
                    else distribution[4]++;
                }
            });
        });

        if (this.charts.distribution) {
            this.charts.distribution.destroy();
        }

        this.charts.distribution = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ranges,
                datasets: [{
                    data: distribution,
                    backgroundColor: [
                        '#28a745', // Vert pour faible biais
                        '#ffc107', // Jaune pour biais modéré
                        '#fd7e14', // Orange pour biais moyen
                        '#dc3545', // Rouge pour biais élevé
                        '#6f42c1'  // Violet pour biais très élevé
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribution des Scores de Biais',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        // Simuler des données de tendance temporelle
        const months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'];
        const datasets = this.filters.selectedModels.map(model => ({
            label: model.toUpperCase(),
            data: months.map(() => Math.random() * 0.5), // Données simulées
            borderColor: this.getModelColor(model, 1),
            backgroundColor: this.getModelColor(model, 0.1),
            fill: true,
            tension: 0.4
        }));

        if (this.charts.trend) {
            this.charts.trend.destroy();
        }

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Évolution des Scores de Biais',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        title: {
                            display: true,
                            text: 'Score de Biais Moyen'
                        }
                    }
                }
            }
        });
    }

    updateCharts() {
        this.renderCharts();
        this.updateSummaryStats();
    }

    updateSummaryStats() {
        const totalModels = this.filters.selectedModels.length;
        const totalBiasTypes = this.filters.selectedBiasTypes.length;
        
        let totalScores = 0;
        let scoreCount = 0;
        let bestModel = '';
        let bestScore = Infinity;
        let lowBiasCount = 0;
        let mediumBiasCount = 0;
        let highBiasCount = 0;

        this.filters.selectedModels.forEach(model => {
            let modelScore = 0;
            let modelCount = 0;

            this.filters.selectedBiasTypes.forEach(biasType => {
                const result = this.data.results[model];
                if (result && result[biasType] && result[biasType].bias_score !== undefined) {
                    const score = result[biasType].bias_score;
                    modelScore += score;
                    modelCount++;
                    totalScores += score;
                    scoreCount++;

                    // Compter les niveaux de biais
                    if (score < 0.1) lowBiasCount++;
                    else if (score < 0.3) mediumBiasCount++;
                    else highBiasCount++;
                }
            });

            if (modelCount > 0) {
                const avgScore = modelScore / modelCount;
                if (avgScore < bestScore) {
                    bestScore = avgScore;
                    bestModel = model;
                }
            }
        });

        const avgBiasScore = scoreCount > 0 ? totalScores / scoreCount : 0;

        // Mettre à jour les éléments DOM
        this.updateStatElement('total-models', totalModels);
        this.updateStatElement('avg-bias-score', avgBiasScore.toFixed(3));
        this.updateStatElement('best-model', bestModel.toUpperCase() || 'N/A');
        this.updateStatElement('total-evaluations', scoreCount);
        this.updateStatElement('low-bias-count', lowBiasCount);
        this.updateStatElement('medium-bias-count', mediumBiasCount);
        this.updateStatElement('high-bias-count', highBiasCount);

        // Mettre à jour le tableau des détails par modèle
        this.updateModelDetailsTable();
    }

    updateModelDetailsTable() {
        const tableBody = document.getElementById('model-details-table');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        // Calculer les scores pour chaque modèle
        const modelData = this.filters.selectedModels.map(model => {
            const result = this.data.results[model] || {};
            const genderBias = result.gender_bias ? result.gender_bias.bias_score || 0 : 0;
            const racialBias = result.racial_bias ? result.racial_bias.bias_score || 0 : 0;
            const toxicity = result.toxicity ? result.toxicity.bias_score || 0 : 0;
            const sentiment = result.sentiment_analysis ? result.sentiment_analysis.bias_score || 0 : 0;
            const globalScore = (genderBias + racialBias + toxicity + sentiment) / 4;

            return {
                model,
                genderBias,
                racialBias,
                toxicity,
                sentiment,
                globalScore
            };
        });

        // Trier par score global (meilleur en premier)
        modelData.sort((a, b) => a.globalScore - b.globalScore);

        // Créer les lignes du tableau
        modelData.forEach((data, index) => {
            const row = document.createElement('tr');
            
            const getBiasClass = (score) => {
                if (score < 0.1) return 'bias-low';
                if (score < 0.3) return 'bias-medium';
                return 'bias-high';
            };

            const formatScore = (score) => score.toFixed(3);

            row.innerHTML = `
                <td><strong>${data.model.toUpperCase()}</strong></td>
                <td><span class="${getBiasClass(data.genderBias)}">${formatScore(data.genderBias)}</span></td>
                <td><span class="${getBiasClass(data.racialBias)}">${formatScore(data.racialBias)}</span></td>
                <td><span class="${getBiasClass(data.toxicity)}">${formatScore(data.toxicity)}</span></td>
                <td><span class="${getBiasClass(data.sentiment)}">${formatScore(data.sentiment)}</span></td>
                <td><strong><span class="${getBiasClass(data.globalScore)}">${formatScore(data.globalScore)}</span></strong></td>
                <td>
                    <span class="badge ${index === 0 ? 'bg-success' : index === 1 ? 'bg-warning' : 'bg-secondary'}">
                        #${index + 1}
                    </span>
                </td>
            `;

            tableBody.appendChild(row);
        });
    }

    updateStatElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            element.classList.add('fade-in');
        }
    }

    getModelColor(model, alpha = 1) {
        const colors = {
            'gpt2': `rgba(255, 107, 53, ${alpha})`,
            'distilgpt2': `rgba(0, 102, 204, ${alpha})`,
            'gpt4': `rgba(40, 167, 69, ${alpha})`,
            'claude': `rgba(111, 66, 193, ${alpha})`
        };
        return colors[model] || `rgba(108, 117, 125, ${alpha})`;
    }

    showLoading(show) {
        const spinner = document.querySelector('.loading-spinner');
        if (spinner) {
            spinner.classList.toggle('active', show);
        }
    }

    showError(message) {
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-danger alert-custom alert-dismissible fade show" role="alert">
                    <strong>Erreur:</strong> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }

    setupEventListeners() {
        // Bouton de rafraîchissement
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Bouton d'export
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }
    }

    async refreshData() {
        await this.loadData();
        this.updateCharts();
        this.showSuccess('Données mises à jour avec succès');
    }

    exportData() {
        const dataStr = JSON.stringify(this.data, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `bias-evaluation-${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }

    showSuccess(message) {
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-success alert-custom alert-dismissible fade show" role="alert">
                    <strong>Succès:</strong> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }

    showError(message) {
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-danger alert-custom alert-dismissible fade show" role="alert">
                    <strong>Erreur:</strong> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
        console.error('Dashboard Error:', message);
    }

    showLoading(show) {
        const loadingElement = document.querySelector('.loading-spinner');
        if (loadingElement) {
            loadingElement.style.display = show ? 'flex' : 'none';
        }
        
        // Désactiver/activer les boutons pendant le chargement
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.disabled = show;
        });
    }
}

// Fonction pour vérifier si Chart.js est chargé
function waitForChart() {
    return new Promise((resolve) => {
        if (typeof Chart !== 'undefined') {
            resolve();
        } else {
            setTimeout(() => {
                waitForChart().then(resolve);
            }, 50);
        }
    });
}

// Initialiser le dashboard quand le DOM et Chart.js sont prêts
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, waiting for Chart.js...');
    await waitForChart();
    console.log('Chart.js loaded, initializing dashboard...');
    window.dashboard = new BiasEvaluationDashboard();
});