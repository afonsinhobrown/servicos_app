// ServiçosPro - Main JavaScript File
class ServicosProApp {
    constructor() {
        this.init();
    }

    init() {
        this.initTheme();
        this.initNotifications();
        this.initForms();
        this.initScrollEffects();
        this.initBackToTop();
        this.initAutoDismissAlerts();
        this.initTooltips();
        this.initModals();
        this.initPasswordToggles();
        this.initImageLoaders();
        this.initAjaxHandlers();
    }

    // Theme Management
    initTheme() {
        const themeToggle = document.getElementById('themeToggle');
        const savedTheme = localStorage.getItem('theme') || 'light';

        // Apply saved theme
        document.documentElement.setAttribute('data-bs-theme', savedTheme);

        if (themeToggle) {
            themeToggle.checked = savedTheme === 'dark';
            themeToggle.addEventListener('change', (e) => {
                const theme = e.target.checked ? 'dark' : 'light';
                this.setTheme(theme);
            });
        }

        // System theme detection
        if (!localStorage.getItem('theme')) {
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.setTheme('dark');
            }
        }
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);

        // Dispatch event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }

    // Notifications System
    initNotifications() {
        // Check for new notifications periodically
        setInterval(() => {
            this.checkNotifications();
        }, 30000); // Every 30 seconds

        // Initial check
        this.checkNotifications();
    }

    async checkNotifications() {
        try {
            const response = await fetch('/api/notifications/count');
            const data = await response.json();

            if (data.success) {
                this.updateNotificationBadge(data.count);
            }
        } catch (error) {
            console.error('Error checking notifications:', error);
        }
    }

    updateNotificationBadge(count) {
        const badges = document.querySelectorAll('.badge-notification, .notification-count');
        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        });
    }

    // Form Enhancements
    initForms() {
        // Auto-dismiss alerts
        this.initAutoDismissAlerts();

        // Bootstrap form validation
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });

        // Real-time form validation
        this.initRealTimeValidation();
    }

    initRealTimeValidation() {
        const inputs = document.querySelectorAll('input[required], textarea[required], select[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });

            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    this.validateField(input);
                }
            });
        });
    }

    validateField(field) {
        if (field.checkValidity()) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }
    }

    // Scroll Effects
    initScrollEffects() {
        let lastScrollTop = 0;
        const navbar = document.querySelector('.navbar');

        if (navbar) {
            window.addEventListener('scroll', () => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    // Scrolling down
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    // Scrolling up
                    navbar.style.transform = 'translateY(0)';
                }

                lastScrollTop = scrollTop;
            });
        }

        // Scroll reveal animations
        this.initScrollReveal();
    }

    initScrollReveal() {
        const srElements = document.querySelectorAll('.sr-item');
        srElements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(50px)';
            el.style.transition = 'all 0.6s ease';

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        setTimeout(() => {
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0)';
                        }, index * 100);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });

            observer.observe(el);
        });
    }

    // Back to Top Button
    initBackToTop() {
        const backToTop = document.createElement('a');
        backToTop.href = '#';
        backToTop.className = 'back-to-top';
        backToTop.innerHTML = '<i class="bi bi-chevron-up"></i>';
        backToTop.setAttribute('aria-label', 'Voltar ao topo');
        document.body.appendChild(backToTop);

        // Show/hide back to top button
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        });

        // Smooth scroll to top
        backToTop.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Auto Dismiss Alerts
    initAutoDismissAlerts() {
        const alerts = document.querySelectorAll('.alert-dismissible');

        alerts.forEach(alert => {
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                if (alert && alert.isConnected) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);

            // Pause auto-dismiss on hover
            alert.addEventListener('mouseenter', function() {
                this.style.transition = 'all 0.3s ease';
            });

            alert.addEventListener('mouseleave', function() {
                this.style.transition = 'all 0.5s ease';
            });
        });
    }

    // Tooltips
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Modal Enhancements
    initModals() {
        // Auto-focus on first input in modals
        document.addEventListener('shown.bs.modal', function (event) {
            const modal = event.target;
            const input = modal.querySelector('input:not([type="hidden"]), textarea, select');
            if (input) {
                setTimeout(() => input.focus(), 100);
            }
        });

        // Close modal on successful form submission
        document.addEventListener('DOMContentLoaded', function() {
            const forms = document.querySelectorAll('.modal-form');
            forms.forEach(form => {
                form.addEventListener('submit', function(e) {
                    const modal = this.closest('.modal');
                    if (modal) {
                        setTimeout(() => {
                            const bsModal = bootstrap.Modal.getInstance(modal);
                            if (bsModal) {
                                bsModal.hide();
                            }
                        }, 1000);
                    }
                });
            });
        });
    }

    // Password Toggle Visibility
    initPasswordToggles() {
        document.querySelectorAll('.password-toggle').forEach(toggle => {
            toggle.addEventListener('click', function() {
                const input = this.previousElementSibling;
                const icon = this.querySelector('i');

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('bi-eye');
                    icon.classList.add('bi-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('bi-eye-slash');
                    icon.classList.add('bi-eye');
                }
            });
        });
    }

    // Image Loading and Error Handling
    initImageLoaders() {
        document.querySelectorAll('img').forEach(img => {
            // Add loading state
            img.addEventListener('load', function() {
                this.classList.add('loaded');
            });

            // Handle broken images
            img.addEventListener('error', function() {
                this.classList.add('image-error');
                this.alt = 'Imagem não disponível';
            });
        });
    }

    // AJAX and API Handlers
    initAjaxHandlers() {
        // Global AJAX error handler
        $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
            console.error('AJAX Error:', thrownError);
            ServicosProApp.showToast('Erro de conexão. Tente novamente.', 'danger');
        });
    }

    // Utility Functions
    static showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        // Create toast
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast after hide
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    static formatCurrency(amount) {
        return new Intl.NumberFormat('pt-MZ', {
            style: 'currency',
            currency: 'MZN'
        }).format(amount);
    }

    static formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('pt-MZ', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    static formatDateTime(dateString) {
        return new Date(dateString).toLocaleDateString('pt-MZ', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static debounce(func, wait) {
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

    // Loading States
    showLoading(selector = 'body') {
        const element = document.querySelector(selector);
        if (element) {
            element.classList.add('loading');
        }
    }

    hideLoading(selector = 'body') {
        const element = document.querySelector(selector);
        if (element) {
            element.classList.remove('loading');
        }
    }

    // API Helper
    async apiCall(url, options = {}) {
        this.showLoading();

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API call failed:', error);
            ServicosProApp.showToast('Erro de conexão. Tente novamente.', 'danger');
            throw error;
        } finally {
            this.hideLoading();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.servicosProApp = new ServicosProApp();

    // Initialize AOS
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            once: true,
            offset: 100
        });
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// Online/Offline detection
window.addEventListener('online', function() {
    ServicosProApp.showToast('Conexão restaurada', 'success');
});

window.addEventListener('offline', function() {
    ServicosProApp.showToast('Sem conexão com a internet', 'warning');
});