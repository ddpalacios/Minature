document.addEventListener("DOMContentLoaded", function() {
    var recordBtn = document.getElementById("recordBtn");
    var stopBtn = document.getElementById("stopBtn");
    var warm_up_btn = document.getElementById("warm_up_btn");
    var long_tones_btn = document.getElementById("long_tones_btn");
    var harmonics_btn= document.getElementById("harmonics_btn");
    var scale_patterns_btn= document.getElementById("scale_patterns_btn");
    var repertoire_btn = document.getElementById("repertoire_btn");
    var timer = document.getElementById("timer");
    var audio_stream = document.getElementById("audio_stream_id");
        var recording_text_id = document.getElementById("recording_text_id");



    var timerInterval = null;
    var timerValue = 0;
    var audio_category = null;
    let audio = document.querySelector('audio');
    let mediaRecorder;
    let chunks = [];
    let stream;

    function createUniqueFileName() {
      const timestamp = Date.now();
      const randomNumber = Math.floor(Math.random() * 1000000);
      return `audio_${timestamp}_${randomNumber}`;
};
    function start_timer() {
        if (timerInterval !== null) {
            return;
        }

       recordBtn.hidden = true;
       timer.hidden = false;
       warm_up_btn.hidden = false;
       long_tones_btn.hidden = false;
       harmonics_btn.hidden = false;
              audio_stream.hidden = true;
       scale_patterns_btn.hidden = false;
       repertoire_btn.hidden = false;
              recording_text_id.hidden = false;


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
                    formData.append('category', audio_category);


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

};
  function stopMicrophone() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
}
    function stop_timer() {
        if (timerInterval !== null) {
            clearInterval(timerInterval);
            timerInterval = null;
            timerValue = 0;
            updateTimerDisplay();
            stopMicrophone();
        }
    };
    function updateTimerDisplay() {
        timer.textContent = timerValue.toFixed(1);
    };

    function select_category(event){
         let button_id = event.target.id
         switch(button_id){
            case "warm_up_btn":
                audio_category = "Warm-Up";
                break;
            case "long_tones_btn":
                audio_category = "Long Tones";
                break;
            case "harmonics_btn":
                audio_category = "Harmonics";
                break;
            case "scale_patterns_btn":
                audio_category = "Scale Pattern";
                break;
            case "repertoire_btn":
                audio_category = "Repertoire";
                break;
         }
          mediaRecorder.stop();
          stop_timer();
       recordBtn.hidden = false;
       timer.hidden = true;
       warm_up_btn.hidden = true;
       long_tones_btn.hidden =true;
       harmonics_btn.hidden = true;
       scale_patterns_btn.hidden = true;
       repertoire_btn.hidden = true;
       audio_stream.hidden = false;
                     recording_text_id.hidden = true;

          console.log("clicked " +audio_category);
    }

    recordBtn.addEventListener('click', start_timer);
    warm_up_btn.addEventListener('click', select_category);
    long_tones_btn.addEventListener('click', select_category);
    harmonics_btn.addEventListener('click', select_category);
    scale_patterns_btn.addEventListener('click', select_category);
    repertoire_btn.addEventListener('click', select_category);

});
