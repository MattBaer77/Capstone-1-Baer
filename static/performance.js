const BASE_URL = "http://127.0.0.1:5000/api";

const defaultGridStyle = {

  scales: {
    y: {
      beginAtZero: true,
      grid: {color: "hsl(0, 0%, 50%)"}
    },
    x: {
      grid: {color: "hsl(0, 0%, 25%)"}
    }
  }

}

// Parse Integer of Goal ID
const goalId = parseInt(goal_id);

// Performance Record Charts
const chartReps = document.getElementById('goal_reps');
const chartSets = document.getElementById('goal_sets');
const chartWeightLbs = document.getElementById('goal_weight_lbs');
const chartTimeSec = document.getElementById('goal_time_sec');
const chartDistanceMiles = document.getElementById('goal_distance_miles');

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
  const goalDistanceMiles = performanceDates.map(() => {return goal.goal_distance_miles});

  const performanceReps = await getPerformanceData(performance, "performance_reps");
  const performanceSets = await getPerformanceData(performance, "performance_sets");
  const performanceWeightLbs = await getPerformanceData(performance, "performance_weight_lbs");
  const performanceTimeSec = await getPerformanceData(performance, "performance_time_sec");
  const performanceDistanceMiles = await getPerformanceData(performance, "performance_distance_miles");

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
      options: defaultGridStyle
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
      options: defaultGridStyle
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
      options: defaultGridStyle
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
      options: defaultGridStyle
    });

  }

  if (chartDistanceMiles) {

    new Chart(chartDistanceMiles, {
      type: 'line',
      data: {
        labels: performanceDates,
        datasets: [
        
        {
          label: 'Actual time - (Seconds)',
          data: performanceDistanceMiles,
          borderWidth: 1
        },
          
        {
          label: 'Goal Time - (Seconds)',
          data: goalDistanceMiles,
          borderWidth: 1
        }

      ]
      },
      options: defaultGridStyle
    });

  }

}

start()