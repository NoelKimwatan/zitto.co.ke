var xRevenueValues = ["January","February","March","April","May","June","July","August","September","October","November","December"];
var yRevenueValues = [7,8,8,9,9,9,10,11,14,14,15];

new Chart("myRevenueChart", {
  type: "line",
  data: {
    labels: xRevenueValues,
    datasets: [{
      fill: false,
      lineTension: 0,
      backgroundColor: "rgba(0,0,255,1.0)",
      borderColor: "rgba(0,0,255,0.1)",
      data: yRevenueValues
    }]
  },
  options: {
    legend: {display: false},
    scales: {
      yAxes: [{ticks: {min: 6, max:16}}],
    },
    title: {
        display: true,
        text: "Monthly Revenue"
      }
  }
});


var xUsersValues = ["January","February","March","April","May","June","July","August","September","October","November","December"];
var yUsersValues = [7,8,8,9,9,9,10,11,14,14,15,6];
var barColors = ["red", "green","blue","orange","brown"];

new Chart("myUsersChart", {
  type: "bar",
  data: {
    labels: xUsersValues,
    datasets: [{
      backgroundColor: barColors,
      data: yUsersValues
    }]
  },
  options: {
    legend: {display: false},
    title: {
      display: true,
      text: "Monthly New Registered Users 2021"
    }
  }
});
