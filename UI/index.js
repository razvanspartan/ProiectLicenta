let current_service = null;
let chart = null;
let settings_current_service = null;
let isInsideSettings = false;
document.getElementById("bookServiceButton")
    .addEventListener("click", () => onClick("bookservice"));
document.getElementById("orderServiceButton")
    .addEventListener("click", () => onClick("orderservice"));
document.getElementById("settingsButton").addEventListener("click", () => switchToToSettings());

document.getElementById("settingsButton").addEventListener("click", () => switchToToSettings());
function getAvgMetrics(data) {
    let total_cpu = 0;
    let total_mem = 0;
    const num_containers = data.length;

    data.forEach(container => {
        total_cpu += container.metrics.cpu;
        total_mem += container.metrics.memory;
    });
    return {
        cpu: (total_cpu / num_containers).toFixed(2),
        memory: (total_mem / num_containers).toFixed(2)
    }
}
function updateChart(data) {
    const domChart = document.getElementById('serviceChart');
    const metrics = getAvgMetrics(data.containers);
    if(!chart){
        chart = new Chart(domChart, {
        type: 'pie',
        data: {
            labels: ['Used CPU', 'Unused CPU'],
            datasets: [{
                label: ['Used CPU', 'Unused CPU'],
                data: [metrics.cpu, Math.min(100 - metrics.cpu*4)],
            }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    }
                }
        }
        });
    } else {
        chart.data.datasets[0].data = [metrics.cpu, (100 - Math.min(metrics.cpu*4, 100))];
        chart.update();
    }
}
function ListItem(container){
return `<div class="list-item">
      <h3 class='list-header'>Container ID: ${container.id}</h3>
      <div class="list-metrics-container">
      <p class='list-paragraph'>Cpu: ${container.metrics.cpu*4}%/100%</p>
      <p class='list-paragraph'>Memory: ${container.metrics.memory}MiB/200MiB</p>
      <div>
      </div>`
}
function updateList(data) {
    const listContainer = document.getElementById('containerListContainer');
    listContainer.innerHTML = '';
    data.containers.forEach(container => {
        const listItem = ListItem(container);
        listContainer.insertAdjacentHTML('beforeend', listItem);
    });
}
function updateServiceDetails(data, service_from_request) {
    if (service_from_request !== current_service) return;
    if(data.containers.length === 0) {
        document.getElementById('serviceTitle').innerHTML = '<p>No containers running for this service.</p>';
        return;
    }
    updateChart(data);
    updateList(data)
}


async function fetchContainers(service_name) {
    toggleLoader(true)
    try {
        const response = await fetch(`http://localhost:3005/api/v1/backend/metrics/${service_name}`)
        const data = await response.json();
        document.getElementById('serviceTitle').textContent = `Service: ${service_name}`;
        if (data.containers.length === 0) {
            document.getElementById('serviceTitle').innerHTML = '<p>No containers running for this service.</p>';
        }
        else
            updateServiceDetails(data, service_name);
    }
    catch{
        document.getElementById('serviceTitle').innerHTML = '<p>Error fetching data for this service.</p>';
    }
    finally { toggleLoader(false); }
}

setInterval(async() =>{
    if(!current_service) return;
    const service_at_start = current_service;
    const response = await fetch(`http://localhost:3005/api/v1/backend/metrics/${current_service}`);
    const data = await response.json();
    updateServiceDetails(data, service_at_start);
}, 5000)

function clearHTML() {
    const listContainer = document.getElementById('containerListContainer');
    if (chart) {
        chart.destroy();
        chart = null;
    }
    listContainer.innerHTML = '';
}
export function onClick(service_name) {
    current_service = service_name;
    clearHTML();
    fetchContainers(service_name);
}

function toggleLoader(show) {
    const loader = document.getElementById('loadingOverlay');
    if (show) {
        loader.classList.remove('loader-hidden');
    } else {
        loader.classList.add('loader-hidden');
    }
}

function switchToToSettings() {
    if (!current_service) {
        alert('Please select a service first (click bookService or orderService)');
        return;
    }
    settings_current_service = current_service;
    document.getElementById('settingsTitle').textContent = `Scaling Settings - ${settings_current_service}`;
    document.getElementById('settingsView').classList.remove('view-hidden');
    document.getElementById('serviceView').classList.add('view-hidden');
    loadSettingsToForm(settings_current_service);
}

function showServiceView() {
     document.getElementById('settingsView').classList.add('view-hidden');
     document.getElementById('serviceView').classList.remove('view-hidden');
 }

 function saveSettings() {
    if (!settings_current_service) {
        alert('No service selected for saving settings');
        return;
    }
    const cooldown = Number(document.getElementById('cooldownPeriod').value);
    const minInstances = Number(document.getElementById('minInstances').value);
    const maxInstances = Number(document.getElementById('maxInstances').value);
    const threshold = Number(document.getElementById('scaleThreshold').value);

    if (minInstances <= 0 || maxInstances <= 0 || cooldown <= 0) {
        alert('Values must be positive');
        return;
    }
    if (minInstances > maxInstances) {
        alert('Minimum instances cannot be greater than maximum instances');
        return;
    }

    const settings = { cooldown, minInstances, maxInstances, threshold };
    const key = `scalingSettings_${settings_current_service}`;
    try {
        localStorage.setItem(key, JSON.stringify(settings));
        const feedback = document.getElementById('settingsFeedback');
        feedback.style.display = 'block';
        setTimeout(() => feedback.style.display = 'none', 2000);
    } catch (e) {
        console.error('Failed to save settings', e);
        alert('Failed to save settings');
    }
 }

 function resetSettings() {
    const defaults = { cooldown: 5, minInstances: 1, maxInstances: 5, threshold: 75 };
    document.getElementById('cooldownPeriod').value = defaults.cooldown;
    document.getElementById('minInstances').value = defaults.minInstances;
    document.getElementById('maxInstances').value = defaults.maxInstances;
    document.getElementById('scaleThreshold').value = defaults.threshold;
    if (settings_current_service) {
        const key = `scalingSettings_${settings_current_service}`;
        localStorage.removeItem(key);
    }
    const feedback = document.getElementById('settingsFeedback');
    feedback.textContent = 'Settings reset.';
    feedback.style.display = 'block';
    setTimeout(() => { feedback.style.display = 'none'; feedback.textContent = 'Settings saved.' }, 2000);
 }

 function loadSettingsToForm() {
    try {
        if (!settings_current_service) return;
        const key = `scalingSettings_${settings_current_service}`;
        const raw = localStorage.getItem(key);
        if (!raw) return;
        const s = JSON.parse(raw);
        if (s.cooldown) document.getElementById('cooldownPeriod').value = s.cooldown;
        if (s.minInstances) document.getElementById('minInstances').value = s.minInstances;
        if (s.maxInstances) document.getElementById('maxInstances').value = s.maxInstances;
        if (s.threshold) document.getElementById('scaleThreshold').value = s.threshold;
    } catch (e) { console.warn('Could not load settings from storage', e); }
}