 $(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Rating input interaction
    $('.rating-input .btn-check').change(function() {
        $('.rating-input .btn').removeClass('active');
        $(this).next('.btn').addClass('active');
    });
    
    // Set initial rating button state
    $('.rating-input .btn-check:checked').next('.btn').addClass('active');
});