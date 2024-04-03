async function request(url, callback) {
  try {
    const response = await fetch(url);
    const responseText = await response.text();
    if (!response.ok) {
      throw new Error(responseText);
    }
    return callback(responseText);
  } catch (error) {
    console.error("Error fetching data:", error);
    callback(null);
  }
}

function change_ipaddress() {
  var ipaddressElement = document.getElementById("ipaddress");
  var networkElement = document.getElementById("network");
  var url = "/Change_ip";
  request(url, async function (json_data) {
    if (json_data) {
      var responseData = JSON.parse(json_data);
      var ipAddress = responseData["ipaddress"];
      var network = responseData["network"];

      console.log(ipAddress);
      ipaddressElement.innerHTML = ipAddress;
      ipaddressElement.style.display = "block";

      networkElement.innerHTML = network;
      networkElement.style.display = "block";
    } else {
      console.error("Failed to retrieve data.");
    }
  });
}

function fetch_status_info() {
  var user_count_Element = document.getElementById("user_count");
  var total_this_month_Element = document.getElementById("total_this_month");
  var total_Element = document.getElementById("total");

  var url = "/update_state";
  request(url, async function (json_data) {
    if (json_data) {
      console.log(json_data);
      var redirectURL = JSON.parse(json_data).location;

      if (redirectURL) {
        window.location.href = redirectURL;
      } else {
        var responseData = JSON.parse(json_data);
        var user_count = responseData["current_wifi_user"];
        var total_this_month = responseData["total_this_month"];
        var total = responseData["total"];

        console.log(user_count);
        user_count_Element.innerHTML = user_count;
        user_count_Element.style.display = "block";

        total_this_month_Element.innerHTML = total_this_month;
        total_this_month_Element.style.display = "block";

        total_Element.innerHTML = total;
        total_Element.style.display = "block";
      }
    } else {
      console.error("Failed to retrieve data.");
    }
  });
}

setInterval(fetch_status_info, 60000);
