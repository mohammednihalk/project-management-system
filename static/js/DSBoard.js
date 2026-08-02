// 🔥 GLOBAL FUNCTION (KEEP OUTSIDE)
function handleInsightClick(type, projectUrl, calendarUrl){

    if (type === "danger") {
        window.location.href = projectUrl + "?status=overdue";
    }
    else if (type === "progress") {
        window.location.href = projectUrl + "?status=in_progress";
    }
    else if (type === "success") {
        window.location.href = projectUrl + "?status=completed";
    }
    else if (type === "warning") {
        window.location.href = calendarUrl;
    }
}


// ✅ MAIN SCRIPT
document.addEventListener("DOMContentLoaded", function () {

    // ===== CHARTS =====
    const ctx = document.getElementById('statusChart');

    if (ctx && typeof chartData !== 'undefined') {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'In Progress', 'Completed', 'Overdue'],
                datasets: [{
                    data: [
                        chartData.active,
                        chartData.in_progress,
                        chartData.completed,
                        chartData.overdue
                    ],
                    backgroundColor: [
                        '#10b981',
                        '#f59e0b',
                        '#3b82f6',
                        '#ef4444'
                    ]
                }]
            }
        });
    }

    const ctx2 = document.getElementById('typeChart');

    if (ctx2 && typeof barData !== 'undefined') {
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: barData.labels,
                datasets: [{
                    label: 'Projects',
                    data: barData.counts,
                    backgroundColor: function(context) {
                        const chart = context.chart;
                        const {ctx, chartArea} = chart;
                        if (!chartArea) return;

                        const gradient = ctx.createLinearGradient(0, 0, 0, chartArea.bottom);
                        gradient.addColorStop(0, "#4f46e5");
                        gradient.addColorStop(1, "#22c55e");

                        return gradient;
                    },
                    borderRadius: 10,
                    barThickness: 40
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    }

    // ===== TOAST FUNCTION =====
    function showToast(message) {
        const toast = document.getElementById('aiToast');
        if (!toast) return;

        toast.innerText = "🤖 " + message;
        toast.style.display = "block";

        setTimeout(() => {
            toast.style.display = "none";
        }, 4000);
    }

    // ===== INITIAL TOAST =====
    const initialInsights = document.querySelectorAll('.insight-item');

    if (initialInsights.length > 0) {
        showToast(initialInsights[0].innerText);
    }

    // ===== LIVE UPDATE =====
    setInterval(() => {

        fetch('/api/insights/')
            .then(res => res.json())
            .then(data => {

                const list = document.querySelector('.insight-list');
                if (!list) return;

                list.innerHTML = "";

                data.insights.forEach((item, index) => {

                    const li = document.createElement('li');

                    li.className = `insight-item ${item[0]} ${index === 0 ? 'top-insight' : ''}`;
                    li.onclick = () => handleInsightClick(item[0],"/Project/","/calendar/");

                    let icon = "💡";

                    if (item[0] === "danger") icon = "⚠️";
                    else if (item[0] === "progress") icon = "🔄";
                    else if (item[0] === "success") icon = "✅";
                    else if (item[0] === "warning") icon = "🔥";

                    li.innerHTML = `
                        <div class="icon">${icon}</div>
                        <div class="text">${item[1]}</div>
                    `;

                    list.appendChild(li);
                });

                // 🔥 UPDATE TOAST WITH NEW TOP INSIGHT
                if (data.insights.length > 0) {
                    showToast(data.insights[0][1]);
                }

            })
            .catch(err => {
                console.error("Insight fetch error:", err);
            });

    }, 5000);

});