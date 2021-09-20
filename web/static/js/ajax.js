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

function submitform_relatedtables(form) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/render_relatedtables", true);
    xhr.setRequestHeader(
        "content-type",
        "application/x-www-form-urlencoded;charset=UTF-8"
    );
    xhr.onload = function () {
        if (this.status == 200) {
            insert_graph(this.response);
        }
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
