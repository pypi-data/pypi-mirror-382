document.addEventListener('DOMContentLoaded', () => {
  /* Navigation with the link from the header. */
  const mainNav = document.querySelector('header.main nav[aria-role="main"]')
  const titleLink = document.querySelector('header.main h2 a')
  window.addEventListener('click', e => {
    if (!mainNav.contains(event.target) && event.target !== titleLink) {
      mainNav.classList.remove('opened')
    }
  })
  titleLink.addEventListener('click', e => {
    e.preventDefault()
    mainNav.classList.toggle('opened')
  })

  /* Scroll on anchors to avoid being hidden by sticky header. */
  const url = new URL(window.location.href)
  if (url.hash !== "") {
    reScroll()
  }
})

window.addEventListener('hashchange', () => {
  reScroll()
})
