const HEADING_SELECTORS = 'h1, h2, summary'

function generateHeadingsIds() {
  const content = document.querySelector('article')
  const headings = content.querySelectorAll(HEADING_SELECTORS)
  const headingMap = {}

  Array.from(headings).forEach((heading) => {
    const id = heading.id
      ? heading.id
      : heading.textContent
          // Replace all accents with non-accentuated versions.
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .trim()
          .toLowerCase()
          .replace('\n', '')
          .split(' ')
          .filter((s) => s)
          .join('-')
          // Replace special chars, order matters: keep space at the end.
          .replace(/[\?\!\@\#\$\%\^\&\*\(\)‘’“”«»,.…;:\s]/gi, '')
    headingMap[id] = !isNaN(headingMap[id]) ? ++headingMap[id] : 0
    if (headingMap[id]) {
      heading.id = id + '-' + headingMap[id]
    } else {
      heading.id = id
    }
  })
}

function openReferencesOnClick() {
  const referencesLink = document.querySelector('.toc a[href="#references"]')
  const references = document.querySelector('#references')
  if (!referencesLink || !references) return
  referencesLink.addEventListener('click', (e) => {
    const anchor = e.target.getAttribute('href')
    const target = document.querySelector(anchor)
    target.parentElement.setAttribute('open', 'open')
    reScroll()
  })
  // In case we already have the references target in the URL on load,
  // simulate a click in order to expand the details/summary content.
  const url = new URL(window.location.href)
  if (url.hash === '#references') {
    referencesLink.click()
    reScroll()
  } else if (url.hash.startsWith('#ref-')) {
    reScroll()
  } else {
    references.parentElement.removeAttribute('open')
  }
}

document.addEventListener('DOMContentLoaded', () => {
  generateHeadingsIds() // Useful to tocbot.
  tocbot.init({
    tocSelector: '.toc',
    contentSelector: 'article',
    headingSelector: HEADING_SELECTORS,
    // Useful to determine when to highlight the element in the toc given
    // the position of the scroll, with a higher value than just under the
    // sticky header, it gives room for small sections at the bottom of
    // the page. And we do not have to reScroll.
    headingsOffset: 200,
    // Shorten the items of the menu and add ellipsis.
    headingLabelCallback: (text) => {
      text = text.trim()
      const max = 60
      return text.substr(0, max - 1) + (text.length + 1 > max ? '…' : '')
    },
    // Expand contenuadd on click and scroll a bit up in this case,
    // otherwise the target is hidden by the fixed topbar.
    onClick: (e) => {
      const target = document.querySelector(e.target.hash)
      const parent = target.parentElement
      if (parent.classList.contains('contenuadd')) {
        parent.classList.add('expanded')
      }
    },
  })
  openReferencesOnClick()
})
