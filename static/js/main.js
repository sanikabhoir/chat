// Enable tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Auto-scroll message container to bottom
    const messageContainers = document.querySelectorAll('.messages-container');
    messageContainers.forEach(container => {
        container.scrollTop = container.scrollHeight;
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
    
    // Character counter for post content
    const postContent = document.querySelector('#content');
    const charCounter = document.querySelector('#char-counter');
    
    if (postContent && charCounter) {
        postContent.addEventListener('input', function() {
            const remaining = 500 - this.value.length;
            charCounter.textContent = remaining + ' characters remaining';
            
            if (remaining < 50) {
                charCounter.classList.add('text-danger');
            } else {
                charCounter.classList.remove('text-danger');
            }
        });
    }
    
    // Real-time message preview
    const messageInput = document.querySelector('#content');
    const messagePreview = document.querySelector('#message-preview');
    
    if (messageInput && messagePreview) {
        messageInput.addEventListener('input', function() {
            messagePreview.textContent = this.value || 'Your message preview...';
        });
    }
});