document.addEventListener("DOMContentLoaded", function() {
    var recordBtn = document.getElementById("recordBtn");
    var stopBtn = document.getElementById("stopBtn");
    var timer = document.getElementById("timer");
    var timerInterval = null;
    var timerValue = 0;
    let audio = document.querySelector('audio');
    let mediaRecorder;
    let chunks = [];
    let stream;

function createUniqueFileName() {
  const timestamp = Date.now();
  const randomNumber = Math.floor(Math.random() * 1000000);
  return `audio_${timestamp}_${randomNumber}`;
}

    function start_timer() {
        if (timerInterval !== null) {
            return;
        }
       navigator.mediaDevices.getUserMedia({ audio: true })
                .then(function(localstream) {
                    stream = localstream
                    mediaRecorder = new MediaRecorder(localstream);
                     mediaRecorder.ondataavailable = function(e) {
                     console.log(e.data)
                     chunks.push(e.data);
                       };
                   mediaRecorder.onstop = function(e){
                    console.log("Stopped")
                    closeMicrophone();
                    const blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
                    chunks = [];

                    const audioUrl = URL.createObjectURL(blob)
                    audio.src =  audioUrl;
                    audio_file_name = createUniqueFileName();

                    // Create FormData
                    let formData = new FormData();
                    formData.append('file_path', blob, audio_file_name);
                    formData.append('file_name', audio_file_name);
                    formData.append('create_date', Date.now());
                    formData.append('category', 'TEST');


                 $.ajax({
                        url: '/add_audio',
                        type: 'POST',
                        data: formData,
                        processData: false, // Important, do not process data
                        contentType: false, // Important, the content type should be set to multipart/form-data
                        success: function(response) {
                            console.log(response);
                        }
                    });
                    }
                 mediaRecorder.start(1000);
                })
                .catch(function(err) {
                    console.log("Error: " + err);
                });

       timerInterval = setInterval(() => {
            timerValue += 0.1;
            updateTimerDisplay();
        }, 100);

}


    function closeMicrophone() {
      if (stream) {
        stream.getTracks().forEach(function(track) {
          track.stop();
        });
        stream = null;
      }
    }

    function stop_timer() {
        if (timerInterval !== null) {
            mediaRecorder.stop();
            clearInterval(timerInterval);
            timerInterval = null;
            timerValue = 0;
            updateTimerDisplay();
            closeMicrophone();
        }
    }

    function updateTimerDisplay() {
        timer.textContent = timerValue.toFixed(1);
    }

    recordBtn.addEventListener('click', start_timer);
    stopBtn.addEventListener('click', stop_timer);

});
