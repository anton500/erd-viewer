function gettables(opt) {
    var xhr = new XMLHttpRequest();
    xhr.responseType = "json";
    xhr.open("POST", "/get_tables", true);
    xhr.setRequestHeader(
        "content-type",
        "application/x-www-form-urlencoded;charset=UTF-8"
    );
    xhr.onload = function () {
        if (this.status == 200) {
            select = document.getElementById("tablesSelect");
            select.length = 0;

            for (table in this.response) {
                option = document.createElement("option");
                option.text = this.response[table];
                option.value = this.response[table];
                select.appendChild(option);
            }
        }
    };
    xhr.send("schema=" + opt);
}

function insert_graph(svg) {
    var div = document.getElementById("svgcontainer");
    div.innerHTML = svg;
    var svgObject = div.getElementsByTagName("svg")[0];
    svgPanZoom(svgObject, {
        controlIconsEnabled: true,
        zoomScaleSensitivity: 0.5,
    });
}

function loading() {
    var svgdiv = document.getElementById("svgcontainer");
    svgdiv.innerHTML = `
        <div class="d-flex vh-100 justify-content-center">
            <div class="spinner-border align-self-center" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>`;

    var submitbutton = document.getElementById("btnSubmit");
    submitbutton.disabled = true;
    submitbutton.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Loading...`;
}

function releasebtn() {
    var submitbutton = document.getElementById("btnSubmit");
    submitbutton.disabled = false;
    submitbutton.innerHTML = "Show";
}

function submitform_relatedtables(form) {
    loading();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/render_relatedtables", true);
    xhr.setRequestHeader(
        "content-type",
        "application/x-www-form-urlencoded;charset=UTF-8"
    );
    xhr.onload = function () {
        if (this.status == 200) {
            insert_graph(this.response);
        } else {
            document.getElementById("svgcontainer").innerHTML = ""
        }
        releasebtn();
    };

    var schema = form.schemas.value;
    var table = form.tables.value;
    var depth = form.depth.value;
    var onlykeys = form.onlykeys.checked ? 1 : 0;

    xhr.send(
        "schema=" +
            schema +
            "&" +
            "table=" +
            table +
            "&" +
            "depth=" +
            depth +
            "&" +
            "onlykeys=" +
            onlykeys
    );
}
