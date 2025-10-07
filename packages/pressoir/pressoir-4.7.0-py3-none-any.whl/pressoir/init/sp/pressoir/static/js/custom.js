document.addEventListener('DOMContentLoaded', () => {
    const currentAnchor = document.location.hash ? document.location.hash.slice(1) : ''
    const indexes = getSetting('indexes')
    const currentAnchorMatches = indexes.some((index) =>
        currentAnchor.startsWith(index)
    )

    if (currentAnchorMatches) {
        // Expand all contenuadds and set a target class if anchor matches.
        const contenuadds = document.querySelectorAll('.contenuadd.lowpriority')
        Array.from(contenuadds).forEach((contenuadd) => {
            if (contenuadd.querySelectorAll(`#${currentAnchor}`).length) {
                contenuadd.classList.toggle('expanded')
            }
        })
        const targets = document.querySelectorAll(`span.${currentAnchor}`)
        Array.from(targets).forEach((target) => {
            target.classList.add('target')
        })
    }
})

// Open the participant infos if current target hash.
document.addEventListener('DOMContentLoaded', () => {
    const currentAnchor = document.location.hash ? document.location.hash.slice(1) : ''
    if (currentAnchor.startsWith('chercheur')) {
        const chercheur = document.querySelector(`#${currentAnchor}`)
        chercheur.classList.toggle('expanded')
    }
})

// Dealing with links to participants.
document.addEventListener('DOMContentLoaded', () => {
    const participants = document.querySelectorAll('.participant')
    Array.from(participants).forEach((participant) => {
        const description = participant.dataset.iddescription
        if (description) {
            const title = 'Accéder à la fiche du·de la participant·e'
            const balloonLength = window.screen.width < 760 ? 'medium' : 'xlarge'
            participant.outerHTML =
                participant.outerHTML +
                `&#8239;<a class="user-circle" data-balloon-length="${balloonLength}" aria-label="${title}" aria-label="${title}" href="${description}"></a>`
        }
    })
})
