// MindTrack JavaScript Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Habit form auto-submit functionality
    const habitForms = document.querySelectorAll('.habit-form');
    habitForms.forEach(function(form) {
        const checkbox = form.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                // Add loading state
                const button = form.querySelector('button[type="submit"]');
                button.disabled = true;
                button.innerHTML = '<i data-feather="loader" class="me-1"></i>Saving...';
                
                // Submit form after short delay for better UX
                setTimeout(function() {
                    form.submit();
                }, 500);
            });
        }
    });

    // Enhanced mood slider interaction
    const moodSlider = document.getElementById('mood_score');
    if (moodSlider) {
        moodSlider.addEventListener('input', function() {
            updateMoodDisplay(this.value);
            
            // Add visual feedback
            this.style.background = `linear-gradient(to right, var(--bs-primary) 0%, var(--bs-primary) ${(this.value - 1) * 11.11}%, var(--bs-secondary) ${(this.value - 1) * 11.11}%, var(--bs-secondary) 100%)`;
        });
        
        // Initialize slider styling
        moodSlider.dispatchEvent(new Event('input'));
    }

    // Sleep quality slider enhancement
    const qualitySlider = document.getElementById('quality');
    if (qualitySlider) {
        qualitySlider.addEventListener('input', function() {
            updateQualityDisplay(this.value);
            
            // Add visual feedback
            this.style.background = `linear-gradient(to right, var(--bs-info) 0%, var(--bs-info) ${(this.value - 1) * 11.11}%, var(--bs-secondary) ${(this.value - 1) * 11.11}%, var(--bs-secondary) 100%)`;
        });
        
        // Initialize slider styling
        qualitySlider.dispatchEvent(new Event('input'));
    }

    // Journal character counter
    const journalTextarea = document.getElementById('content');
    if (journalTextarea) {
        const charCounter = document.createElement('div');
        charCounter.className = 'form-text text-end';
        charCounter.id = 'charCounter';
        journalTextarea.parentNode.appendChild(charCounter);
        
        function updateCharCounter() {
            const count = journalTextarea.value.length;
            charCounter.textContent = `${count} characters`;
            
            if (count > 5000) {
                charCounter.className = 'form-text text-end text-warning';
            } else {
                charCounter.className = 'form-text text-end';
            }
        }
        
        journalTextarea.addEventListener('input', updateCharCounter);
        updateCharCounter();
    }

    // Auto-save functionality for long forms
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    autoSaveForms.forEach(function(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('input', debounce(function() {
                saveFormData(form);
            }, 1000));
        });
        
        // Load saved data on page load
        loadFormData(form);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S to save forms
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const submitButton = document.querySelector('button[type="submit"]:focus, form button[type="submit"]');
            if (submitButton) {
                submitButton.click();
            }
        }
        
        // Ctrl/Cmd + M for mood tracking
        if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
            e.preventDefault();
            window.location.href = '/mood';
        }
        
        // Ctrl/Cmd + J for journal
        if ((e.ctrlKey || e.metaKey) && e.key === 'j') {
            e.preventDefault();
            window.location.href = '/journal';
        }
    });

    // Initialize feature icons refresh
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
});

// Utility Functions

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function saveFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`mindtrack_form_${form.id}`, JSON.stringify(data));
}

function loadFormData(form) {
    const savedData = localStorage.getItem(`mindtrack_form_${form.id}`);
    
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && input.type !== 'hidden') {
                    input.value = data[key];
                }
            });
        } catch (e) {
            console.warn('Failed to load saved form data:', e);
        }
    }
}

function clearFormData(form) {
    localStorage.removeItem(`mindtrack_form_${form.id}`);
}

// Mood tracking helpers
function getMoodEmoji(score) {
    if (score >= 9) return '😄';
    if (score >= 7) return '😊';
    if (score >= 5) return '😐';
    if (score >= 3) return '😕';
    return '😞';
}

function getMoodColor(score) {
    if (score >= 8) return 'success';
    if (score >= 6) return 'primary';
    if (score >= 4) return 'warning';
    return 'danger';
}

// Sleep tracking helpers
function getSleepQuality(quality) {
    if (quality >= 8) return 'Excellent';
    if (quality >= 6) return 'Good';
    if (quality >= 4) return 'Fair';
    return 'Poor';
}

// Analytics helpers
function calculateTrend(data) {
    if (data.length < 2) return 0;
    
    const recent = data.slice(-7).reduce((a, b) => a + b, 0) / Math.min(7, data.length);
    const previous = data.slice(-14, -7).reduce((a, b) => a + b, 0) / Math.min(7, data.slice(-14, -7).length);
    
    return recent - previous;
}

// PWA-like features
function showNotification(title, options = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            icon: '/static/images/icon.png',
            badge: '/static/images/badge.png',
            ...options
        });
    }
}

function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// Export functions for use in templates
window.MindTrack = {
    updateMoodDisplay: function(value) {
        const scoreDisplay = document.querySelector('.mood-display-score');
        const emojiDisplay = document.querySelector('.mood-display-emoji');
        
        if (scoreDisplay) scoreDisplay.textContent = value;
        if (emojiDisplay) emojiDisplay.textContent = getMoodEmoji(parseInt(value));
    },
    
    updateQualityDisplay: function(value) {
        const qualityDisplay = document.querySelector('.quality-display');
        if (qualityDisplay) qualityDisplay.textContent = value + '/10';
    },
    
    showNotification,
    requestNotificationPermission
};

// Make functions globally available for inline use
window.updateMoodDisplay = window.MindTrack.updateMoodDisplay;
window.updateQualityDisplay = window.MindTrack.updateQualityDisplay;
