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
dropdownItems.forEach((item) =>{
    const dropdownButton = item.querySelector('.dropdown__button') 

    // 2. Select each button click
    dropdownButton.addEventListener('click', () =>{
        // 7. Select the current show-dropdown class
        const showDropdown = document.querySelector('.show-dropdown')
        
        // 5. Call the toggleItem function
        toggleItem(item)

        // 8. Remove the show-dropdown class from other items
        if(showDropdown && showDropdown!== item){
            toggleItem(showDropdown)
        }
    })
})

// 3. Create a function to display the dropdown
const toggleItem = (item) =>{
    // 3.1. Select each dropdown content
    const dropdownContainer = item.querySelector('.dropdown__container')

    // 6. If the same item contains the show-dropdown class, remove
    if(item.classList.contains('show-dropdown')){
        dropdownContainer.removeAttribute('style')
        item.classList.remove('show-dropdown')
    } else{
        // 4. Add the maximum height to the dropdown content and add the show-dropdown class
        dropdownContainer.style.height = dropdownContainer.scrollHeight + 'px'
        item.classList.add('show-dropdown')
    }
}

/*=============== DELETE DROPDOWN STYLES ===============*/
const mediaQuery = matchMedia('(min-width: 1118px)'),
      dropdownContainer = document.querySelectorAll('.dropdown__container')

// Function to remove dropdown styles in mobile mode when browser resizes
const removeStyle = () =>{
    // Validate if the media query reaches 1118px
    if(mediaQuery.matches){
        // Remove the dropdown container height style
        dropdownContainer.forEach((e) =>{
            e.removeAttribute('style')
        })

        // Remove the show-dropdown class from dropdown item
        dropdownItems.forEach((e) =>{
            e.classList.remove('show-dropdown')
        })
    }
}

addEventListener('resize', removeStyle)

// Counter animation for dashboard cards
document.addEventListener('DOMContentLoaded', () => {
  const counters = document.querySelectorAll('.card-value');

  const options = {
    threshold: 0.1,           // start animating when 10% of element is visible
    rootMargin: '0px 0px -100px 0px'
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const counter = entry.target;
        const target = parseFloat(counter.getAttribute('data-target'));
        const prefix = counter.textContent.includes('$') ? '$' : '';
        const suffix = counter.textContent.includes('mi') ? ' mi' :
                       counter.textContent.includes('mph') ? ' mph' : '';

        let start = 0;
        const duration = 1800; // ms
        const increment = target / (duration / 16); // ~60fps

        const updateCounter = () => {
          start += increment;
          if (start < target) {
            // Show 0 decimal places for big integers, 1 for small floats
            const displayValue = Number.isInteger(target) 
              ? Math.ceil(start) 
              : start.toFixed(1);
            
            counter.textContent = prefix + displayValue + suffix;
            requestAnimationFrame(updateCounter);
          } else {
            counter.textContent = prefix + target + suffix;
            observer.unobserve(counter);
          }
        };

        updateCounter();
      }
    });
  }, options);

  counters.forEach(counter => observer.observe(counter));
});

// Add this after DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('fareDistanceChart')?.getContext('2d');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Trips',
        data: [], // ← fill with real {x: distance, y: fare} objects
        backgroundColor: 'rgba(34, 139, 230, 0.6)',
        borderColor: 'rgba(34, 139, 230, 0.9)',
        pointRadius: 5,
        pointHoverRadius: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: 'Distance (miles)' } },
        y: { title: { display: true, text: 'Fare ($)' } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `$${ctx.parsed.y.toFixed(2)} for ${ctx.parsed.x.toFixed(1)} mi`
          }
        }
      }
    }
  });
});
