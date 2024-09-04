// Dodavanje event listenera kada je DOM potpuno učitan
document.addEventListener('DOMContentLoaded', function() { //DOM (Document Object Model) 
    // JavaScript za hamburger meni
    const menuButton = document.querySelector('.menu-button');
    const menu = document.querySelector('.menu');

    if (menuButton && menu) {
        menuButton.addEventListener('click', function() {
            menu.classList.toggle('active');
        });
    }

    // Klikabilni gradovi samo za logovane korisnike koji nisu admini
    const cityWeatherElements = document.querySelectorAll('.clickable-city:not(.non-clickable)');
    cityWeatherElements.forEach(cityElement => {
        cityElement.addEventListener('click', function() {
            const city = this.querySelector('h4').textContent;
            window.location.href = `/result?city=${encodeURIComponent(city)}`;
        });
    });

    // Obrada promene u dropdown meniju za odabir države
    const countrySelect = document.getElementById('country');
    if (countrySelect) {
        countrySelect.addEventListener('change', function() {
            document.querySelector('form').submit();
        });
    }

    // Prikazivanje pop-up prozora za povratne informacije
    const feedbackButton = document.getElementById('feedbackButton');
    const feedbackPopup = document.getElementById('feedbackPopup');
    const popupFeedbackForm = document.getElementById('popupFeedbackForm');

    if (feedbackButton && feedbackPopup && popupFeedbackForm) {
        feedbackButton.addEventListener('click', function() {
            feedbackPopup.classList.toggle('hidden');
            document.getElementById('feedback_temperature').value = feedbackButton.getAttribute('data-temperature'); // Postavi temperaturu iz sesije
        });

        popupFeedbackForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const feedbackData = {
                recommendation_id: document.getElementById('recommendation_id').value,
                feedback: JSON.stringify({
                    upper_wear: capitalizeWords(document.getElementById('popup_feedback_upper_wear').value),
                    lower_wear: capitalizeWords(document.getElementById('popup_feedback_lower_wear').value),
                    footwear: capitalizeWords(document.getElementById('popup_feedback_footwear').value),
                    temperature: document.getElementById('feedback_temperature').value  // Dodavanje temperature
                }),
                min_temp: document.getElementById('popup_feedback_min_temp').value,
                max_temp: document.getElementById('popup_feedback_max_temp').value
            };

            fetch('/save_feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(feedbackData)
            })
            .then(response => {
                if (response.ok) {
                    alert('Povratna informacija uspješno poslana!');
                    feedbackPopup.classList.add('hidden');
                } else {
                    alert('Došlo je do greške prilikom slanja povratne informacije.');
                }
            })
            .catch(error => {
                console.error('Greška:', error);
                alert('Došlo je do greške prilikom slanja povratne informacije.');
            });
        });
    }
});

// Funkcija za kapitalizaciju reči u stringu
function capitalizeWords(str) {
    return str.replace(/\b\w+/g, function(txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}
