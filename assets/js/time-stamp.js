document.addEventListener('DOMContentLoaded', function() {

    var video = document.getElementById('video')
    var buttons = document.querySelectorAll('#buttons a')

    Array.from(buttons).forEach(function (button) {
        button.addEventListener('click', function () {
            video.currentTime = button.dataset.timestamp
            video.play()
        })
    })
});