document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const message = document.getElementById('message');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            video.srcObject = stream;
            video.onloadedmetadata = function() {
                video.play();
                setTimeout(function() {
                    capturePhoto();
                }, 1000); // Wait 1 second for camera to load
            };
        })
        .catch(function(err) {
            console.error('Error accessing camera: ', err);
            message.textContent = 'Camera access denied or not available.';
        });

    function capturePhoto() {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(function(blob) {
            const formData = new FormData();
            formData.append('photo', blob, 'photo.png');

            fetch('/upload_photo', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(data => {
                message.textContent = 'Photo captured and uploaded successfully.';
                // Stop the video stream
                video.srcObject.getTracks().forEach(track => track.stop());
            })
            .catch(error => {
                console.error('Error uploading photo:', error);
                message.textContent = 'Error uploading photo.';
            });
        }, 'image/png');
    }
});
