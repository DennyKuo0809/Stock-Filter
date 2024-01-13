let serverPort = "8555";

function toggle_enable(element, enable_list, disable_list) {
    if (element.checked) {
        for (const [index, id_] of Object.entries(enable_list)) {
            var to_toggle = document.getElementById(id_);
            to_toggle.disabled = false;
        }
    }
    else {
        for (const [index, id_] of Object.entries(disable_list)) {
            var to_toggle = document.getElementById(id_);
            if (to_toggle.type === 'checkbox') {
                to_toggle.checked = false;
            }
            to_toggle.disabled = true;
        }
    }

}

function toggle(category) {
    console.log(category)
    /* Button */
    buttons = {
        'KDJ': document.getElementById("KDJ-toggle-btn"),
        'trend': document.getElementById("trend-toggle-btn")
    };
    // console.log(buttons)

    /* Div */
    divs = {
        'KDJ': document.getElementById("KDJ-div"),
        'trend': document.getElementById("trend-div")
    };

    /* toggle */
    for (const [key, value] of Object.entries(buttons)) {
        if (key === category) {
            if (value.classList.contains('btn-light')) {
                value.classList.remove('btn-light');
                value.classList.add('btn-secondary');
            }
        }
        else {
            if (value.classList.contains('btn-secondary')) {
                value.classList.remove('btn-secondary');
                value.classList.add('btn-light');
            }
        }
    }

    for (const [key, value] of Object.entries(divs)) {
        if (key === category) {
            if (value.style.display === 'none') {
                value.style.display = 'block';
            }
        }
        else {
            if (value.style.display === 'block') {
                value.style.display = 'none';
            }
        }
    }

}

async function refresh(aspect, button, date_id) {
    var originText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    var state = "";
    await fetch(`http://127.0.0.1:${serverPort}/refresh/${aspect}/`, {
        method: 'get'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            state = "Complete";
        })
        .catch(error => {
            console.error('There was an error!', error);
            state = "Failed";
        });

    alert(state);
    if (state === "Complete") {
        var date = new Date();
        var toChange = document.getElementById(date_id);
        console.log(toChange);
        toChange.innerHTML = `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`;
    }
    button.innerHTML = originText;
    return;
}

async function search(button) {
    var form = document.getElementById('search-form');
    var formData = new FormData(form);
    var data = {};
    for (var [key, value] of formData.entries()) {
        data[key] = value;
    }
    var originText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    var state = "";

    await fetch(`http://127.0.0.1:${serverPort}/filter/`, {
        method: 'POST',
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // console.log('Received data:', data);
            var container = document.getElementById('result');
            container.innerHTML = "";
            data.forEach(element => {
                var para = document.createElement("p");
                // const node = document.createTextNode(`${element.code} ${element.name} ${element.category}`)
                // para.appendChild(node);
                var link = document.createElement("a");
                link.appendChild(document.createTextNode(`${element.code} ${element.name} ${element.category}`));
                link.href = element.src;
                link.target = '_blank';
                para.appendChild(link);
                
                container.appendChild(para);
                console.log(element);
            });
            state = "Complete";
        })
        .catch(error => {
            console.error('There was an error!', error);
            state = "Failed";
        });
    alert(state);
    button.innerHTML = originText;
}
