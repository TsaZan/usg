// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Auto-dismiss alerts
document.addEventListener('DOMContentLoaded', function() {
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// File input preview
document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const previewElement = document.querySelector(this.dataset.preview);
            if (previewElement && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewElement.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
});

// Password strength meter
function checkPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[!@#$%^&*(),.?":{}|<>]+/)) strength++;
    return strength;
}

document.addEventListener('DOMContentLoaded', function() {
    const passwordInputs = document.querySelectorAll('input[type="password"][data-strength-meter]');
    passwordInputs.forEach(function(input) {
        const meter = document.querySelector(input.dataset.strengthMeter);
        if (meter) {
            input.addEventListener('input', function() {
                const strength = checkPasswordStrength(this.value);
                meter.value = strength;
                meter.className = `strength-${strength}`;
            });
        }
    });
});

// Infinite scroll
class InfiniteScroll {
    constructor(container, loadMore, options = {}) {
        this.container = container;
        this.loadMore = loadMore;
        this.options = {
            threshold: 100,
            ...options
        };
        this.loading = false;
        this.init();
    }

    init() {
        window.addEventListener('scroll', () => {
            if (this.loading) return;
            
            const containerBottom = this.container.getBoundingClientRect().bottom;
            const windowHeight = window.innerHeight;
            
            if (containerBottom - windowHeight <= this.options.threshold) {
                this.loading = true;
                this.loadMore().finally(() => {
                    this.loading = false;
                });
            }
        });
    }
}

// Export functions for use in other files
window.UGC = {
    InfiniteScroll,
    checkPasswordStrength
}; 