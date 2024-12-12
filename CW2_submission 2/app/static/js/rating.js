$(document).ready(function() {
    // Handle star click event
    $('.star').on('click', function() {
        // Get the movie ID (you can pass it dynamically from the backend)
        var movieId = $(this).closest('.movie-details-container').data('movie-id');
        var rating = $(this).data('value');

        // Send the rating to the backend using AJAX
        $.ajax({
            url: '/rate',  // Flask endpoint for rating
            type: 'POST',
            data: JSON.stringify({ movie_id: movieId, rating: rating }),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                // Update the average rating display
                $('#average-rating').text("Average Rating: " + response.average_rating);

                // Update star appearance based on the current rating
                updateStars(rating);
            },
            error: function(error) {
                console.log("Error in AJAX request:", error);
            }
        });
    });

    // Function to update the stars to reflect the rating
    function updateStars(rating) {
        $('.star').each(function() {
            var starValue = $(this).data('value');
            if (starValue <= rating) {
                $(this).html('&#9733;'); // Filled star
            } else {
                $(this).html('&#9734;'); // Empty star
            }
        });
    }
});
