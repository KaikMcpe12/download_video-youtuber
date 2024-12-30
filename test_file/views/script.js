document.getElementById('download-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const url = document.getElementById('url').value;
    const messageDiv = document.getElementById('message');

    try {
        const response = await fetch('http://localhost:5000/download/mp3', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            const errorText = await response.text();
            messageDiv.textContent = `Erro1: ${errorText}`;
            messageDiv.style.color = 'red';
            return;
        }

        console.log(response)
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = 'audio.mp3';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);

        messageDiv.textContent = 'Download concluído com sucesso!';
        messageDiv.style.color = 'green';
    } catch (error) {
        messageDiv.textContent = `Erro2: ${error}`;
        messageDiv.style.color = 'red';
    }
});
