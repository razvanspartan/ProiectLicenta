let current_service = null;
let chart = null;
document.getElementById("bookServiceButton")
    .addEventListener("click", () => onClick("bookservice"));
document.getElementById("orderServiceButton")
    .addEventListener("click", () => onClick("orderservice"));
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
    const domChart = document.getElementById('service_chart');
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
    const listContainer = document.getElementById('container-list-container');
    listContainer.innerHTML = '';
    data.containers.forEach(container => {
        const listItem = ListItem(container);
        listContainer.insertAdjacentHTML('beforeend', listItem);
    });
}
function updateServiceDetails(data, service_from_request) {
    if (service_from_request !== current_service) return;
    if(data.containers.length === 0) {
        document.getElementById('service-title').innerHTML = '<p>No containers running for this service.</p>';
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
        document.getElementById('service-title').textContent = `Service: ${service_name}`;
        if (data.containers.length === 0) {
            document.getElementById('service-title').innerHTML = '<p>No containers running for this service.</p>';
        }
        else
            updateServiceDetails(data, service_name);
    }
    catch{
        document.getElementById('service-title').innerHTML = '<p>Error fetching data for this service.</p>';
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
    const listContainer = document.getElementById('container-list-container');
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
    const loader = document.getElementById('loading-overlay');
    if (show) {
        loader.classList.remove('loader-hidden');
    } else {
        loader.classList.add('loader-hidden');
    }
}