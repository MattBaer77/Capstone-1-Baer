const BASE_URL = "http://127.0.0.1:5000/api";

const goalId = parseInt(goal_id)

const ctx = document.getElementById('myChart');

// Get the Goal from the API
async function getGoal() {
    const resp = await axios.get(`${BASE_URL}/goal/${goalId}`);
    goal = await resp.data.goal_json
}

// Get the Performance Records from the API
async function getPerformance() {
    const resp = await axios.get(`${BASE_URL}/goal/${goalId}/performance`);
    performance = await resp.data.performance_json
}

let goal;
getGoal()
let performance;
getPerformance()




// SAMPLE  
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
    datasets: [{
      label: '# of Votes',
      data: [12, 19, 3, 5, 2, 3],
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});