document.addEventListener('DOMContentLoaded', () => {
    const contenuaddTitles = document.querySelectorAll('.contenuadd.lowpriority > h3')
    /* Expand contenuadd with lowpriority on title click. */
    for (const contenuaddTitle of contenuaddTitles) {
        contenuaddTitle.addEventListener('click', (e) => {
            const section = e.target.closest('section')
            section.classList.toggle('expanded')
            e.preventDefault()
        })
    }

    // Expand all contenuadds and set a target class if anchor matches.
    const currentAnchor = document.location.hash ? document.location.hash.slice(1) : ''
    const contenuadds = document.querySelectorAll('.contenuadd.lowpriority')
    for (const contenuadd of contenuadds) {
        if (contenuadd.id === currentAnchor) {
            contenuadd.classList.toggle('expanded')
        }
    }
})
