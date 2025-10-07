document.addEventListener('DOMContentLoaded', () => {
    function extractHostname(link) {
        const url = new URL(link)
        return url.hostname.replace('www.', '')
    }

    function markdownEmphasis(value) {
        const emphasisSeparator = '*'
        if (value.indexOf(emphasisSeparator) > -1) {
            const [pre, term, post] = value.split(emphasisSeparator, 3)
            value = `${pre}<em>${term}</em>${post}`
        }
        return value
    }

    function buildTooltip(termeEnrichi, classlist) {
        const dataset = termeEnrichi.dataset

        let title = markdownEmphasis(dataset.idsp) || ''
        const firstChild = termeEnrichi.firstChild
        if (firstChild.tagName === 'A') {
            title = `<a href="${firstChild.href}">${markdownEmphasis(dataset.idsp)}</a>`
            if (firstChild.dataset.linkArchive) {
                title += `
          (<a href="${firstChild.dataset.linkArchive}">${extractHostname(
              firstChild.dataset.linkArchive
          )}</a>)
        `
            } else {
            }
        }

        let ref = ''
        const idref =
            dataset.idwiki || dataset.idbnf || dataset.idorcid || dataset.idreference

        if (idref) {
            ref = `<div class="tooltip-ref">Réf. :
        <a href="${idref}"
           title="Accéder à la référence distante"
          >${extractHostname(idref)}</a>
      </div>`
        }
        let extras = ''
        const idglossaire = dataset.idglossaire
        if (idglossaire) {
            const label = getSetting('glossaire-button-label')
            const title = getSetting('glossaire-button-title')
            extras = `<a href="${idglossaire}" title="${title}">${label}</a>`
        }
        let extraTitle = ''
        const idbibs = dataset.idbib
        if (idbibs) {
            idbibs.split(';').forEach((idbib) => {
                const refbib = idbib.trim().substring(1).split(',', 1)[0]
                extraTitle += `
                    <span class="citation" data-cites="${refbib}">
                        <a href="#ref-${refbib}" role="doc-biblioref">réf.</a>
                    </span>
                `
            })
        }

        return `
      <div class="${classlist[0]} termeenrichi">
        <div class="tooltip-title">${title}${extraTitle}</div>
        <div class="tooltip-index">
          <a href="index-np.html#${classlist[1]}"
             title="Consulter la référence dans l’index de l’ouvrage"
            >Voir dans l’index</a> ${extras}
        </div>
        ${ref}
      </div>
    `.trim()
    }

    const indexes = getSetting('indexes')
    const indexesSelector = indexes.map((index) => `span.${index}`).join(',')

    Array.from(document.querySelectorAll(indexesSelector)).forEach((termeEnrichi) => {
        const classlist = termeEnrichi.classList
        termeEnrichi.addEventListener('click', (e) => {
            e.preventDefault()
            if (classlist.contains('expanded')) {
                const tooltip = termeEnrichi.nextSibling
                termeEnrichi.parentElement.removeChild(tooltip)
                classlist.remove('expanded')
            } else {
                termeEnrichi.insertAdjacentHTML(
                    'afterend',
                    buildTooltip(termeEnrichi, classlist)
                )
                const tooltip = termeEnrichi.nextElementSibling
                Array.from(tooltip.querySelectorAll('[data-cites]')).forEach(
                    transformCitation
                )
                Array.from(tooltip.querySelectorAll('[href^="#ref-"]')).forEach(
                    tooltipReference
                )
                classlist.add('expanded')
            }
        })
    })
})
