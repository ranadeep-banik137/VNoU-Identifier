document.getElementById('registrationForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the form from submitting normally
    if (confirm('Are you all the inputs are correct?')) {
        const formData = new FormData(event.target);
    try {
        const response = await fetch('http://localhost:1100/register', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            alert('File not uploaded');
            throw new Error('Server response not ok');
        }
        alert('File uploaded and moved!');
        event.target.reset();
    } catch (error) {
        console.error('Error:', error);
    }
    }
});
