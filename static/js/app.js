// ===== Marathon 4:35 - App JavaScript =====

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered:', registration.scope);
            })
            .catch(function(error) {
                console.log('SW registration failed:', error);
            });
    });
}

// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', function() {
    var flashes = document.querySelectorAll('.flash');
    flashes.forEach(function(flash) {
        setTimeout(function() {
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-20px)';
            flash.style.transition = 'all 0.3s ease';
            setTimeout(function() { flash.remove(); }, 300);
        }, 3000);
    });
});

// Chart.js defaults for dark theme
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#8892b0';
    Chart.defaults.borderColor = '#233054';
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
}

// Create a line chart (used for pace trend, weight, etc.)
function createLineChart(canvasId, labels, data, label, color, targetLine, targetLineMax) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var datasets = [{
        label: label,
        data: data,
        borderColor: color,
        backgroundColor: color + '20',
        fill: true,
        tension: 0.3,
        pointRadius: 3,
        pointBackgroundColor: color,
        borderWidth: 2,
    }];

    if (targetLine !== undefined) {
        datasets.push({
            label: 'Target ' + targetLine,
            data: Array(labels.length).fill(targetLine),
            borderColor: '#2ecc71',
            borderDash: [5, 5],
            borderWidth: 1,
            pointRadius: 0,
            fill: false,
        });
    }

    if (targetLineMax !== undefined) {
        datasets.push({
            label: 'Target ' + targetLineMax,
            data: Array(labels.length).fill(targetLineMax),
            borderColor: '#2ecc71',
            borderDash: [3, 3],
            borderWidth: 1,
            pointRadius: 0,
            fill: '-1',
            backgroundColor: 'rgba(46, 204, 113, 0.10)',
        });
    }

    new Chart(ctx, {
        type: 'line',
        data: { labels: labels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: targetLine !== undefined, position: 'bottom', labels: { boxWidth: 12 } },
            },
            scales: {
                x: { display: true, ticks: { maxTicksLimit: 6, font: { size: 10 } } },
                y: { display: true, ticks: { font: { size: 10 } } },
            },
            interaction: { intersect: false, mode: 'index' },
        }
    });
}

// Create a bar chart (used for weekly km, etc.)
function createBarChart(canvasId, labels, data, label, color) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: color + 'cc',
                borderColor: color,
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                x: { display: true, ticks: { font: { size: 10 } } },
                y: { display: true, beginAtZero: true, ticks: { font: { size: 10 } } },
            },
        }
    });
}
