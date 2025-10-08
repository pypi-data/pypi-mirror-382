// TODO add icons 
// TODO add dropdown

document.addEventListener('DOMContentLoaded', function() {
    // Fetch json file with launch buttons
    fetch('_static/_launch_buttons.json')
    .then((response) => response.json())
    .then((response) => {
        if(!response || !Array.isArray(response.custom_launch_buttons) || response.custom_launch_buttons.length === 0) return;
        addButtons(response.custom_launch_buttons);
    })
    .catch((err) => {
        // Missing or malformed JSON — nothing to do.
        console.debug('sphinx-launch-buttons: no valid custom_launch_buttons JSON found', err);
    });

});

let addButtons = (buttons) => {
    // Append launch buttons to the page
    buttons.forEach(function(button) {

        // Create a new button element
        var buttonElement = document.createElement('button');

        // Set the button's text and class
        buttonElement.textContent = button.label;
        buttonElement.classList.add("btn", "btn-sm", "navbar-btn");

        // Add an event listener to the button
        buttonElement.addEventListener('click', function() {
            // Execute the specified action when the button is clicked
            window.location.href = button.url;
        });

        // Add the button to the page
        document.getElementsByClassName('article-header-buttons')[0].prepend(buttonElement)
    });
}
