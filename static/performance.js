const BASE_URL = "http://127.0.0.1:5000/api";



const goalId = parseInt(goal_id)


// Test Chart
const ctx = document.getElementById('myChart');


// Performance Record Charts
const chartReps = document.getElementById('goal_reps');
const chartSets = document.getElementById('goal_sets');
const chartWeightLbs = document.getElementById('goal_weight_lbs');
const chartTimeSec = document.getElementById('goal_time_sec');

// Variables

let goal;
let performance;
let performanceDates = [];

// Get the Goal from the API
async function getGoal() {
    const resp = await axios.get(`${BASE_URL}/goal/${goalId}`);
    return resp.data.goal_json
}

// Get the Performance Records from the API
async function getPerformance() {
    const resp = await axios.get(`${BASE_URL}/goal/${goalId}/performance`);
    return resp.data.performance_json
}

async function performanceDatesFill(performance) {

  for (let p of performance) {
    performanceDates.push(p.date)
    console.log(p.date)
  }

}

async function getPerformanceData(performance, variableToGet) {

  let results = [];

  for (let record of performance) {
    results.push(record[`${variableToGet}`])
    console.log(results)
  }

  return results;

}


async function start() {

  goal = await getGoal()
  performance = await getPerformance()
  performanceDatesFill(performance)

  goalReps = performanceDates.map(() => {return goal.goal_reps})
  goalSets = performanceDates.map(() => {return goal.goal_sets})
  goalWeightLbs = performanceDates.map(() => {return goal.goal_weight_lbs})
  goalTimeSec = performanceDates.map(() => {return goal.goal_time_sec})

  performanceReps = await getPerformanceData(performance, "performance_reps")
  performanceSets = await getPerformanceData(performance, "performance_sets")
  performanceWeightLbs = await getPerformanceData(performance, "performance_weight_lbs")
  performanceTimeSec = await getPerformanceData(performance, "performance_time_sec")

  if (chartReps){

    new Chart(chartReps, {
      type: 'line',
      data: {
        labels: performanceDates,
        datasets: [
          
        {
          label: 'Goal Reps',
          data: goalReps,
          borderWidth: 1
        },
        {
          label: 'Actual Reps',
          data: performanceReps,
          borderWidth: 1
        }
      ]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });

  }

  if (chartSets){

    new Chart(chartSets, {
      type: 'line',
      data: {
        labels: performanceDates,
        datasets: [
          
        {
          label: 'Goal Sets',
          data: goalSets,
          borderWidth: 1
        },
        {
          label: 'Actual Sets',
          data: performanceSets,
          borderWidth: 1
        }
      ]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });

  }

  if (chartWeightLbs) {

    new Chart(chartWeightLbs, {
      type: 'line',
      data: {
        labels: performanceDates,
        datasets: [
          
        {
          label: 'Goal Weight - (LBS.)',
          data: goalWeightLbs,
          borderWidth: 1
        },
        {
          label: 'Actual Weight - (LBS.)',
          data: performanceWeightLbs,
          borderWidth: 1
        }
      ]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });

  }

  if (chartTimeSec) {

    new Chart(chartTimeSec, {
      type: 'line',
      data: {
        labels: performanceDates,
        datasets: [
          
        {
          label: 'Goal Time - (Seconds)',
          data: goalTimeSec,
          borderWidth: 1
        },
        {
          label: 'Actual time - (Seconds)',
          data: performanceTimeSec,
          borderWidth: 1
        }
      ]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });

  }
}

start()