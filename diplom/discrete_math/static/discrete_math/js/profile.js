document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('id_photo');
    const preview = document.getElementById('photoPreview');

    if (!fileInput || !preview) return;

    fileInput.addEventListener('change', function () {
        const file = this.files[0];
        if (!file) return;

        // Проверка: файл должен быть изображением
        if (!file.type.startsWith('image/')) {
            alert('Пожалуйста, выберите изображение');
            this.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result; // предпросмотр
        };
        reader.readAsDataURL(file);
    });
});
