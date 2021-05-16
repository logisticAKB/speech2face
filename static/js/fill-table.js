function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$.ajax({
    type: "GET",
    url: "api/tasks/",
    data: null,
    dataType: "json",
    processData: false,
    contentType: false,
    success: function(data) {
        fillTable(data);
    }
});

function fillTable(data) {
    for (let i = 0; i < data.length; i++) {
        let img = ``;
        if (data[i]['result'] != null) {
            img = `<img class="image" id="img01" src=${data[i]['result']} width="64" height="64" alt="Your face">`;
        }

        $(`#task-table > tbody:last-child`).append(`<tr>\n` +
        `            <td>${data[i]['task_id']}</td>\n` +
        `            <td>${data[i]['status']}</td>\n` +
        `            <td class="centred-td-style">\n` + img +
        `            </td>\n` +
        `            <td class="centred-td-style">\n` +
        `                <svg onclick="deleteTask(this)" xmlns="http://www.w3.org/2000/svg"  viewBox="0 0 512 512" width="16px" height="16px"><path fill="#E04F5F" d="M504.1,256C504.1,119,393,7.9,256,7.9C119,7.9,7.9,119,7.9,256C7.9,393,119,504.1,256,504.1C393,504.1,504.1,393,504.1,256z"></path><path fill="#FFF" d="M285,256l72.5-84.2c7.9-9.2,6.9-23-2.3-31c-9.2-7.9-23-6.9-30.9,2.3L256,222.4l-68.2-79.2c-7.9-9.2-21.8-10.2-31-2.3c-9.2,7.9-10.2,21.8-2.3,31L227,256l-72.5,84.2c-7.9,9.2-6.9,23,2.3,31c4.1,3.6,9.2,5.3,14.3,5.3c6.2,0,12.3-2.6,16.6-7.6l68.2-79.2l68.2,79.2c4.3,5,10.5,7.6,16.6,7.6c5.1,0,10.2-1.7,14.3-5.3c9.2-7.9,10.2-21.8,2.3-31L285,256z"></path></svg>\n` +
        `            </td>\n` +
        `        </tr>`);
    }
    makeModal();
}

function makeModal() {
    let modal = document.getElementById('modal');
    let modalImg = document.getElementById("modal-img");
    let images = document.getElementsByClassName('image');
    for (let i = 0; i < images.length; i++) {
        images[i].onclick = function () {
            modal.style.display = "block";
            modalImg.src = this.src;
        }
    }

    let span = document.getElementsByClassName("close")[0];
    span.onclick = function () {
        modal.style.display = "none";
    }
}

function deleteTask(element) {
    let task_id = element.parentElement.parentElement.childNodes[1].textContent
    $(element).closest("tr").remove();
    $.ajax({
        type: "DELETE",
        url: `api/tasks/${task_id}/`,
        data: null,
        dataType: null,
        processData: false,
        contentType: false,
    });
}