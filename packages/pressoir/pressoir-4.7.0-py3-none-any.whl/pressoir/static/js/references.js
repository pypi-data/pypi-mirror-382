function zip(rows) {
    return rows[0].map((_, index) => rows.map((row) => row[index]))
}

function transformCitation(citation) {
    const cites = citation.dataset.cites
    let content = citation.textContent
    if (!content) {
        return
    }
    const hasParenthesis = content.startsWith('(') && content.endsWith(')')
    if (hasParenthesis) {
        content = content.slice(1, -1)
    }
    if (cites === '') {
        return
    }
    let citations
    if (cites.indexOf(' ') > -1) {
        if (content.indexOf(';') === -1) {
            return
        }
        const linkCitations = []
        const citesSplit = cites.split(' ')
        let innerSplit = content.split(';')
        // Handle the case when we have `(Klein and Konieczny 2015a, 2015b; 2018)`,
        // really fragile, especially when we have multiple authors like:
        // `(Faragher 2005; Griffiths 2005; Hodson 2012; Kennedy 2014; Reid, Basque, and Mancke 2004)`
        // The combination of the two cases will fail but will it really happen?
        if (citesSplit.length !== innerSplit.length) {
            innerSplit = innerSplit.flatMap((item) => item.split(','))
        }
        for (const [cite, inner] of zip([citesSplit, innerSplit])) {
            // Should not happen but at least it does not break badly.
            if (inner) {
                const linkCitation = document.createElement('a')
                linkCitation.setAttribute('href', `#ref-${cite}`)
                linkCitation.textContent = inner.trim()
                linkCitations.push(linkCitation.outerHTML)
            }
        }
        citations = linkCitations.join(', ')
    } else {
        const linkCitation = document.createElement('a')
        linkCitation.setAttribute('href', `#ref-${cites}`)
        linkCitation.textContent = content.trim()
        citations = linkCitation.outerHTML
    }
    if (hasParenthesis) {
        citations = `(${citations})`
    }
    citation.innerHTML = citations
}

function capitalize(string) {
    return string.replace(/\b\w/g, (c) => c.toUpperCase())
}

function handleReference(referenceLink, reference, fromBibliography) {
    const content = reference.textContent
        .trim()
        .replace(/(?:https?|ftp):\/\/[\n\S]+/g, '') // Remove links.
    let onelinerContent = content
        .split('\n')
        .map((fragment) => fragment.trim()) // Remove new lines.
        .join(' ')
    if (onelinerContent.startsWith('———.')) {
        const ref = document.querySelector(referenceLink.hash)
        let previousRef = ref.previousElementSibling
        let previousRefContent = previousRef.textContent.trim()
        while (previousRefContent.startsWith('———.')) {
            previousRef = previousRef.previousElementSibling
            previousRefContent = previousRef.textContent.trim()
        }
        const previousNames = previousRefContent.split('.')[0].trim()
        onelinerContent = onelinerContent.replace('———.', `${previousNames}.`)
    }
    if (fromBibliography) {
        referenceLink.href = `bibliographie.html${referenceLink.hash}`
    }
    referenceLink.setAttribute('aria-label', onelinerContent)
    const balloonLength = window.screen.width < 760 ? 'medium' : 'xlarge'
    referenceLink.dataset.balloonLength = balloonLength

    /* Open references on click. */
    referenceLink.addEventListener('click', (e) => {
        references.parentElement.setAttribute('open', 'open')
        // Waiting to reach the bottom of the page then scroll up a bit
        // to avoid the fixed header. Fragile.
        setTimeout(() => {
            window.scrollTo({
                top: window.scrollY - 130,
                behavior: 'smooth',
            })
        }, 10)
    })
}

function tooltipReference(referenceLink) {
    /* Put attributes for balloon.css to render tooltips. */
    const reference = document.querySelector(referenceLink.hash)
    if (reference) {
        handleReference(referenceLink, reference)
    } else {
        fetch('bibliographie.html')
            .then((response) => response.text())
            .then((body) => {
                const tempDiv = document.createElement('div')
                tempDiv.innerHTML = body
                return tempDiv.querySelector(referenceLink.hash)
            })
            .then((reference) => handleReference(referenceLink, reference, true))
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const references = document.querySelector('#references')
    const chapter = document.body.dataset.chapitre
    if (!chapter || !references) {
        return
    }

    /* Transform citations from contenuadd (converted as <span>s by Pandoc
     because we set `suppress-bibliography` to true). */
    Array.from(document.querySelectorAll('[data-cites]')).forEach(transformCitation)

    /* Setup balloons tooltips for references. */
    Array.from(document.querySelectorAll('[href^="#ref-"]')).forEach(tooltipReference)
})
