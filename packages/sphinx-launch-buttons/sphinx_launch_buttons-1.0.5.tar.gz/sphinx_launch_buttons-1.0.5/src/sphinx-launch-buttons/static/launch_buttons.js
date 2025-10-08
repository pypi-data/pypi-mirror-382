// Css to let the dropdown open on hover
const dropdownCSS = `
/* Custom CSS to make the dropdown open on hover */
.dropdown-menu {
display: none; /* Hide the dropdown menu by default */
}
.dropdown-source-buttons:hover .dropdown-menu {
display: block; /* Display the dropdown menu on hover */
}
`

// MAIN => hook into the DOM and add the buttons
document.addEventListener('DOMContentLoaded', function() {
    fetch('_static/_launch_buttons.json')
    .then((response) => response.json())
    .then((response) => {
        if(!response || !Array.isArray(response.buttons) || response.buttons.length === 0) return;
        addButtons(response.buttons)
    })
    .catch((err) => {
        // If the file is missing or malformed, do nothing — no buttons should be shown.
        console.debug('sphinx-launch-buttons: no valid launch buttons JSON found', err);
    });

});

// distribute based on the type of the buttons
let addButtons = (buttons) => {
    // Append launch buttons to the page
    buttons.forEach(function(button) {
        element = button.type == "dropdown" ? addDropdown(button) : addButton(button);
        document.getElementsByClassName('article-header-buttons')[0].prepend(element)
    });
}

/* Structure of dropdown: 
*  <div>
*       <button>
*       <ul> 
*           <li> <a> </li>
*       </ul>
*  </div>
*/
let addDropdown = (button) => {
    // Create a new container for full element
    let container = document.createElement('div');
    container.classList.add("dropdown", "dropdown-source-buttons");

    // Create a new <style> element
    var style = document.createElement('style');
    if (style.styleSheet) {
        // For IE
        style.styleSheet.cssText = dropdownCSS;
    } else {
        // For other browsers
        style.appendChild(document.createTextNode(dropdownCSS));
    }
    container.appendChild(style);

    // Create a new button element and set necessary elements
    let buttonElement = document.createElement('button');
    buttonElement.classList.add("btn", "dropdown-toggle");
    buttonElement.setAttribute("data-bs-toggle", "dropdown");

    if(button.icon != undefined) buttonElement.appendChild(setIcon(button.icon)); 
    if(button.label!= undefined) buttonElement.innerHTML += " " + button.label

    // Create dropdown list containing all links
    let dropdownList = document.createElement('ul');
    dropdownList.classList.add("dropdown-menu");

    // Add dropdown items to the list according to the given format
    // create <li> which will contain <a> with all the relevant information (b for button, running out of names...)
    button.items.forEach(function(b) {
        let listItem = document.createElement('li');
        let linkItem = document.createElement('a');
        linkItem.classList.add("btn", "btn-sm", "dropdown-item");
        linkItem.setAttribute("data-bs-placement", "left");
        linkItem.href = b.url;

        // Check if icon is present, if not add a dot (&#x2022;)
        if(b.icon != undefined){
            let icon = setSubIcon(b.icon)
            linkItem.appendChild(icon);
        } else {
            linkItem.innerHTML += "&#x2022;";
        }
        if(b.label != undefined) linkItem.innerHTML += " " + b.label;

        listItem.appendChild(linkItem);
        dropdownList.appendChild(listItem);
    })
    
    container.appendChild(buttonElement);
    container.appendChild(dropdownList);

    return container
}

// Function which will return a button element with all the relevant information
let addButton = (button) => {
    // Create a new button element
    var buttonElement = document.createElement('button');

    // Set the button's text and class
    buttonElement.classList.add("btn", "btn-sm", "navbar-btn");

    // Add an event listener to the button
    buttonElement.addEventListener('click', function() {
        // Execute the specified action when the button is clicked
        if (button.icon != undefined) buttonElement.innerHTML += button.icon;
        if (button.label != undefined) buttonElement.innerHTML += " " + button.label;
        window.location.href = button.url;
    });

    // Add the button to the page
    return buttonElement
}


// Function which sets the same classes for all svg icons
const setIcon = (icon) => {
    // Create a new DOMParser
    const parser = new DOMParser();
    const element = parser.parseFromString(icon, 'text/html').getElementsByTagName('svg')[0];
    element.classList = []
    element.classList.add("svg-inline--fa")
    return element
}

// Different function for svg icons living in different places ;) 
const setSubIcon = (icon) => {
    let span = document.createElement('span');
    span.classList.add("btn__icon-container");
    span.appendChild( setIcon(icon) );
    return span
}
