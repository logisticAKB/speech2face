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
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

let seconds = 3;
let checkResultIntervalSec = 2;
let recorder = null;
let promise = navigator.mediaDevices.getUserMedia({audio: true, video: false});

promise.then(createMediaRecorder)

function createMediaRecorder(stream) {
    recorder = new MediaRecorder(stream);
    recorder.chunks = [];

    recorder.ondataavailable = function(e) {
        this.chunks.push(e.data);
    };
    // console.log(recorder);

    recorder.onstop = function(event) {
        // console.log(this.chunks)
        let blob = new Blob(this.chunks, {'type': 'audio/wav;'});
        this.chunks = [];
        let formData = new FormData();
        formData.append('audio_file', blob, "audio.wav");

        $.ajax({
        type: "POST",
        url: '/api/speech2face/',
        data: formData,
        processData: false,
        contentType: false,
        success: function(data) {
            let json = $.parseJSON(data);
            console.log(json['task_id']);
            setTimeout(checkResult, checkResultIntervalSec * 1000, json['task_id']);
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.error('jqXHR:', jqXHR);
            console.error('textStatus:', textStatus);
            console.error('errorThrown:', errorThrown);
        },
    });

    }
}

function checkResult(task_id) {
    $.ajax({
        type: "GET",
        url: '/api/speech2face/' + task_id,
        data: null,
        processData: false,
        contentType: false,
        success: function(data) {
            let json = $.parseJSON(data);
            console.log(json['status']);
            console.log(json['result']);
            if (json['status'] !== 'SUCCESS') {
                setTimeout(checkResult, checkResultIntervalSec * 1000, task_id);
            } else {
                resultSuccess(json['result'])
            }
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.error('jqXHR:', jqXHR);
            console.error('textStatus:', textStatus);
            console.error('errorThrown:', errorThrown);
        },
    });
}

function resultSuccess(result) {
    document.getElementById('loader').hidden = true;
    document.getElementById('informer').hidden = true;

    document.getElementById('image').src = result;
    document.getElementById('image').hidden = false;
    document.getElementById('image-slider').className = 'fade';
}

function onClick() {
    if (recorder != null) {
        document.getElementById('outline').className = 'outline';
        document.getElementById('delayed').className = 'outline';
        document.getElementById('informer').className = 'informer-anim';
        document.getElementById('timer').className = 'timer-anim';

        let timer = setInterval(this.onTimer, 1000);
        setTimeout(() => {clearInterval(timer); this.onTimerExpire()}, seconds * 1000);

        recorder.start();
    }
}

function onTimer() {
    seconds = seconds - 1;
    document.getElementById('timer-value').innerHTML = "0:0" + seconds;
}

function onTimerExpire() {
    recorder.stop();

    document.getElementById('outline').className = '';
    document.getElementById('delayed').className = '';


    document.getElementById('mic-button').hidden = true;

    document.getElementById('loader').hidden = false;
    document.getElementById('loader-slider').className = 'slide-up';

    document.getElementById('informer').className = "informer_2";
    document.getElementById('informer').innerHTML = "Обработка";
    document.getElementById('timer').hidden = true;
}
