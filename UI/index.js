let current_service = null;
let chart = null;
let isInsideSettings = false;
document.getElementById("bookserviceButton")
    .addEventListener("click", () => onClick("bookservice"));
document.getElementById("orderserviceButton")
    .addEventListener("click", () => onClick("orderservice"));
document.getElementById("settingsButton").addEventListener("click", () => switchToToSettings());
document.getElementById("settingsSaveButton").addEventListener("click", () => saveSettings());
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
function setServiceButtonAsSelected(service_name) {
    document.getElementById('settingsButton').classList.remove('hidden');
    document.getElementById('bookserviceButton').classList.remove('selected');
    document.getElementById('orderserviceButton').classList.remove('selected');
    document.getElementById(`${service_name}Button`).classList.add('selected');
}
export function onClick(service_name) {
    current_service = service_name;
    clearHTML();
    setServiceButtonAsSelected(service_name)
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
    if (isInsideSettings) {
        showServiceView();
        document.getElementById('settingsButton').textContent = 'Scaling Settings';
    } else {
        document.getElementById('serviceView').classList.add('view-hidden');
        document.getElementById('settingsView').classList.remove('view-hidden');
        document.getElementById('settingsButton').textContent = 'Back to Service';
    }
    isInsideSettings = !isInsideSettings;
}

function showServiceView() {
     document.getElementById('settingsView').classList.add('view-hidden');
     document.getElementById('serviceView').classList.remove('view-hidden');
 }

function showSettingsFeedback(message, isError = false) {
    const el = document.getElementById('settingsFeedback');
    el.style.display = 'block';
    el.textContent = message;
    if (isError) el.classList.add('error'); else el.classList.remove('error');
}

function saveSettings() {
    const fields = [
        { id: 'cooldownPeriod', name: 'Cooldown Period' },
        { id: 'minInstances', name: 'Min Instances' },
        { id: 'maxInstances', name: 'Max Instances' },
        { id: 'scaleUpThreshold', name: 'Scale Up Threshold' },
        {id: 'scaleDownThreshold', name: 'Scale Down Threshold' },
    ];

    for (const f of fields) {
        const el = document.getElementById(f.id);
        const val = Number(el.value);
        const min = Number(el.min);
        const max = Number(el.max);
        if (el.value === '' || !Number.isFinite(val)) {
            showSettingsFeedback(`Enter a valid number for ${f.name}.`, true);
            return;
        }
        if (val < min || val > max) {
            showSettingsFeedback(`${f.name} must be between ${min} and ${max}.`, true);
            return;
        }
    }

    const minInstances = Number(document.getElementById('minInstances').value);
    const maxInstances = Number(document.getElementById('maxInstances').value);
    const scaleDownThreshold = Number(document.getElementById('scaleDownThreshold').value);
    const scaleUpThreshold = Number(document.getElementById('scaleUpThreshold').value);
    if (minInstances > maxInstances) {
        showSettingsFeedback('Min Instances must be less than or equal to Max Instances.', true);
        return;
    }
    if(scaleDownThreshold >= scaleUpThreshold) {
        showSettingsFeedback('Scale Down Threshold must be less than Scale Up Threshold.', true);
        return;
    }

    showSettingsFeedback('Settings saved.', false);

}