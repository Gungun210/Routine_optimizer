document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('loading').style.display = 'none';
            
            if (Object.keys(data).length === 0) {
                document.getElementById('dashboard-content').innerHTML = '<p class="text-center">No data available yet. Please add entries.</p>';
                document.getElementById('dashboard-content').style.display = 'block';
                return;
            }

            document.getElementById('dashboard-content').style.display = 'block';

            // Update Stats
            document.getElementById('stat-productivity').innerText = data.stats.avg_productivity;
            document.getElementById('stat-energy').innerText = data.stats.avg_energy;
            document.getElementById('stat-hours').innerText = data.stats.total_hours_tracked;

            // Render Insights
            const insightsList = document.getElementById('insights-list');
            if (data.insights && data.insights.length > 0) {
                data.insights.forEach(insight => {
                    const li = document.createElement('li');
                    li.innerText = insight;
                    insightsList.appendChild(li);
                });
            } else {
                insightsList.innerHTML = '<li>Keep tracking your activities to generate insights!</li>';
            }

            // Common Chart Options
            Chart.defaults.color = '#94A3B8';
            Chart.defaults.font.family = "'Inter', sans-serif";

            // Category Chart (Pie)
            const ctxCategory = document.getElementById('categoryChart').getContext('2d');
            new Chart(ctxCategory, {
                type: 'pie',
                data: {
                    labels: Object.keys(data.category_data),
                    datasets: [{
                        data: Object.values(data.category_data),
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.8)', // Productive (can be any order so we should match label if possible, but let's keep it simple)
                            'rgba(245, 158, 11, 0.8)', // Neutral
                            'rgba(239, 68, 68, 0.8)'   // Waste
                        ],
                        borderWidth: 1,
                        borderColor: '#1E293B'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });

            // Activity Chart (Bar)
            const ctxActivity = document.getElementById('activityChart').getContext('2d');
            new Chart(ctxActivity, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.activity_data),
                    datasets: [{
                        label: 'Hours Spent',
                        data: Object.values(data.activity_data),
                        backgroundColor: 'rgba(129, 140, 248, 0.8)',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#334155' } },
                        x: { grid: { display: false } }
                    }
                }
            });

            // Productivity vs Time Chart (Line)
            const ctxProd = document.getElementById('productivityChart').getContext('2d');
            const sortedHours = Object.keys(data.prod_by_hour).sort((a,b) => parseInt(a) - parseInt(b));
            const prodValues = sortedHours.map(h => data.prod_by_hour[h]);
            const timeLabels = sortedHours.map(h => `${h}:00`);

            new Chart(ctxProd, {
                type: 'line',
                data: {
                    labels: timeLabels,
                    datasets: [{
                        label: 'Avg Productivity',
                        data: prodValues,
                        borderColor: '#C084FC',
                        backgroundColor: 'rgba(192, 132, 252, 0.2)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, max: 5, grid: { color: '#334155' } },
                        x: { grid: { display: false } }
                    }
                }
            });

        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('loading').innerText = 'Failed to load data.';
        });
});
