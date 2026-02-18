/*=============== SHOW MENU ===============*/
const showMenu = (toggleId, navId) =>{
   const toggle = document.getElementById(toggleId),
         nav = document.getElementById(navId)

   toggle.addEventListener('click', () =>{
       // Add show-menu class to nav menu
       nav.classList.toggle('show-menu')
       // Add show-icon to show and hide menu icon
       toggle.classList.toggle('show-icon')
   })
}

showMenu('nav-toggle','nav-menu')

/*=============== SHOW DROPDOWN MENU ===============*/
const dropdownItems = document.querySelectorAll('.dropdown__item')

// 1. Select each dropdown item
const dropdownItem = document.querySelector('.dropdown__item');
const dropdownButton = document.querySelector('.dropdown__button');
const dropdownContainer = document.querySelector('.dropdown__container');

// open when button clicked
dropdownButton.addEventListener('click', function (e) {
    e.stopPropagation(); // prevent bubbling
    dropdownItem.classList.toggle('show-dropdown');
});

// close when clicking outside
document.addEventListener('click', function (e) {
    if (!dropdownItem.contains(e.target)) {
        dropdownItem.classList.remove('show-dropdown');
    }
});

const mediaQuery = window.matchMedia('(min-width: 1118px)');

const removeStyle = () => {
  if (mediaQuery.matches) {
    // remove inline height if any
    dropdownContainer.removeAttribute('style');

    // close dropdown
    dropdownItem.classList.remove('show-dropdown');
  }
};

window.addEventListener('resize', removeStyle);


// Counter animation for dashboard cards
function counterAnimation(){
  const cards = document.querySelectorAll('.card-value');

  // Loop through each card and animate the count up to the actual value
  cards.forEach(card => {
        const target = Number(card.textContent);
        let count = 0;
        const increment = target / 100;

        const update = () => {
            count += increment;
            if (count < target) {
                card.textContent = Math.floor(count);
                requestAnimationFrame(update);
            } else {
                card.textContent = target.toLocaleString(); // Format with commas

                // adding units to specific cards
                if (card.id === 'avgFare') {
                    card.textContent = '$' + card.textContent;
                } else if (card.id === 'avgDistance') {
                    card.textContent += ' miles';
                } else if (card.id === 'avgSpeed') {
                    card.textContent += ' mph';
                } else if (card.id === 'totalRevenue') {
                    card.textContent = '$' + card.textContent;
                }
            }
        };

        card.textContent = 0;
        update();
    });
}

// Dropdown for search filters in the search page
const searchMethod = document.getElementById("searchMethod");

const sections = {
  payment: document.getElementById("paymentSearch"),
  date: document.getElementById("dateSearch"),
  fare: document.getElementById("fareSearch"),
  distance: document.getElementById("distanceSearch")
};

searchMethod.addEventListener("change", function () {

  // hide everything first
  Object.values(sections).forEach(section => {
    section.classList.add("hidden");
  });

  // show only selected one
  if (sections[this.value]) {
    sections[this.value].classList.remove("hidden");
  }
});

