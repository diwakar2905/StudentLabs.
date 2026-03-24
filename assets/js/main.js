document.addEventListener('DOMContentLoaded', () => {
    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Waitlist Form Interactivity
    const forms = document.querySelectorAll('.waitlist-form');
    
    forms.forEach(form => {
        const emailInput = form.querySelector('.email-input');
        const btn = form.querySelector('.btn-primary');
        const span = form.querySelector('.btn-text');
        const btnGlow = form.querySelector('.btn-glow');

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = emailInput.value.trim();
            
            if (email) {
                span.textContent = 'Joining...';
                btn.style.opacity = '0.9';
                btn.disabled = true;
                
                setTimeout(() => {
                    span.textContent = 'Welcome aboard! 🚀';
                    btn.style.background = 'linear-gradient(135deg, #059669, #10b981)'; // Green success
                    btn.style.boxShadow = '0 8px 25px rgba(16, 185, 129, 0.4)';
                    if (btnGlow) btnGlow.style.background = '#10b981';
                    emailInput.value = '';
                    
                    setTimeout(() => {
                        span.textContent = 'Join the Waitlist';
                        btn.style.background = '';
                        btn.style.boxShadow = '';
                        if (btnGlow) btnGlow.style.background = 'var(--accent-1)';
                        btn.disabled = false;
                    }, 4000);
                }, 1000);
            }
        });
    });

    // Scroll Reveal Animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal').forEach((element, index) => {
        // Add staggered delays for grid items
        if(element.classList.contains('step-card') || element.classList.contains('feature-card')) {
            element.style.transitionDelay = `${(index % 3) * 0.15}s`;
        }
        observer.observe(element);
    });

    // FAQ Accordion with smooth height transitions
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            
            // Close all
            faqItems.forEach(faq => {
                faq.classList.remove('active');
                faq.querySelector('.faq-icon').style.transform = 'rotate(0deg)';
            });
            
            // Open clicked
            if (!isActive) {
                item.classList.add('active');
                item.querySelector('.faq-icon').style.transform = 'rotate(45deg)';
            }
        });
    });
    
    // Demo video loop sequence simulation
    const demoLoading = document.querySelector('.demo-loading');
    const demoResult = document.querySelector('.demo-result');
    const mockTyping = document.querySelector('.mock-typing');
    
    if (demoLoading && demoResult && mockTyping) {
        setInterval(() => {
            // Reset animations
            mockTyping.style.animation = 'none';
            demoLoading.style.animation = 'none';
            demoResult.style.animation = 'none';
            
            // Force reflow
            void mockTyping.offsetWidth;
            
            setTimeout(() => {
                mockTyping.style.animation = 'typing 3s steps(40) forwards, blink 0.5s step-end infinite alternate';
                demoLoading.style.animation = 'revealLoading 0s 3.5s forwards';
                demoResult.style.animation = 'revealResult 0s 6s forwards';
            }, 50);
        }, 12000);
    }
});
