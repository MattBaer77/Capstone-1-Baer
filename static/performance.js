const BASE_URL = "http://127.0.0.1:5000/api";

// Parse Integer of Goal ID
const goalId = parseInt(goal_id);

// Performance Record Charts
const chartReps = document.getElementById('goal_reps');
const chartSets = document.getElementById('goal_sets');
const chartWeightLbs = document.getElementById('goal_weight_lbs');
const chartTimeSec = document.getElementById('goal_time_sec');

// Get the Goal from the API
async function getGoal() {

  const resp = await axios.get(`${BASE_URL}/goal/${goalId}`);
  return resp.data.goal_json;

}

// Get the Performance Records from the API
async function getPerformance() {

  const resp = await axios.get(`${BASE_URL}/goal/${goalId}/performance`);
  return resp.data.performance_json;

}

async function getPerformanceData(performance, variableToGet) {

  let result = [];

  for (let record of performance) {
    result.push(record[`${variableToGet}`])
  }

  return result;

}

async function start() {

  const goal = await getGoal();
  const performance = await getPerformance();
  const performanceDates = await getPerformanceData(performance, "date");

  const goalReps = performanceDates.map(() => {return goal.goal_reps});
  const goalSets = performanceDates.map(() => {return goal.goal_sets});
  const goalWeightLbs = performanceDates.map(() => {return goal.goal_weight_lbs});
  const goalTimeSec = performanceDates.map(() => {return goal.goal_time_sec});

  const performanceReps = await getPerformanceData(performance, "performance_reps");
  const performanceSets = await getPerformanceData(performance, "performance_sets");
  const performanceWeightLbs = await getPerformanceData(performance, "performance_weight_lbs");
  const performanceTimeSec = await getPerformanceData(performance, "performance_time_sec");

  if (chartReps){

    new Chart(chartReps, {
      type: 'line',
      data: {
        labels: performanceDates,
        datasets: [

        {
          label: 'Actual Reps',
          data: performanceReps,
          borderWidth: 1
        },
          
        {
          label: 'Goal Reps',
          data: goalReps,
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
          label: 'Actual Sets',
          data: performanceSets,
          borderWidth: 1
        },
          
        {
          label: 'Goal Sets',
          data: goalSets,
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
          label: 'Actual Weight - (LBS.)',
          data: performanceWeightLbs,
          borderWidth: 1
        },
          
        {
          label: 'Goal Weight - (LBS.)',
          data: goalWeightLbs,
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
          label: 'Actual time - (Seconds)',
          data: performanceTimeSec,
          borderWidth: 1
        },
          
        {
          label: 'Goal Time - (Seconds)',
          data: goalTimeSec,
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