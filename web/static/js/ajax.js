function getTables(opt) {
  var xhr = new XMLHttpRequest();
  xhr.responseType = "json";
  xhr.open("post", "/get_tables", true);
  xhr.setRequestHeader(
    "content-type",
    "application/x-www-form-urlencoded; charset=utf-8"
  );
  xhr.onload = function () {
    if (this.status == 200) {
      var select = document.getElementById("select-tables");
      select.length = 0;

      for (const table in this.response) {
        let option = document.createElement("option");
        option.text = this.response[table];
        option.value = this.response[table];
        select.appendChild(option);
      }
    }
  };
  xhr.send("schema=" + opt);
}

function insertGraph(svg) {
  var svgDiv = document.getElementById("svg-container");
  svgDiv.innerHTML = svg;
  var svgObject = svgDiv.getElementsByTagName("svg")[0];
  svgPanZoom(svgObject, {
    controlIconsEnabled: true,
    zoomScaleSensitivity: 0.5,
  });
}

function loading() {
  var svgDiv = document.getElementById("svg-container");
  svgDiv.innerHTML = `
        <div class="d-flex vh-100 justify-content-center">
            <div class="spinner-border align-self-center" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>`;
  var submitButton = document.getElementById("button-submit");
  submitButton.disabled = true;
  submitButton.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Loading...`;
}

function releaseButton() {
  var submitButton = document.getElementById("button-submit");
  submitButton.disabled = false;
  submitButton.innerHTML = "Show";
}

function submitForm(form, url) {
  loading();
  var xhr = new XMLHttpRequest();
  xhr.open("post", url, true);
  xhr.onload = function () {
    if (this.status == 200) {
      insertGraph(this.response);
    } else {
      document.getElementById("svg-container").innerHTML = ""
    }
    releaseButton();
  };

  formData = new FormData(form)
  if (form.onlyrefs != null) {
    formData.set("onlyrefs", form.onlyrefs.checked ? 1 : 0)
  }
  if (form.shortest != null) {
    formData.set("shortest", form.shortest.checked ? 1 : 0)
  }

  xhr.send(formData);
}