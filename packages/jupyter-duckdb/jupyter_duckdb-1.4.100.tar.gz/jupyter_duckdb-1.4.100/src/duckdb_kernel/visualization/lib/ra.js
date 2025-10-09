function animate_ra(divId, rootNodeId) {
    /*
    const {createApp, onMounted, ref} = Vue

    createApp({
        setup() {
            onMounted(() => {
                const titles = document.querySelectorAll(`#${divId} title`)
                const gs = [...titles]
                    .map(t => [t.textContent, t.parentElement])
                    .filter(g => g[1].id && g[1].id.startsWith('node'))

                console.log(gs)
            })
        }
    }).mount(`#${divId}`)
     */

    const titles = [...document.querySelectorAll(`#${divId} title`)]
        .filter(p => p.parentElement.id && p.parentElement.id.startsWith('node'))

    // update cursor
    titles.forEach(t => t.parentElement.style.cursor = 'pointer')
    titles.forEach(t => t.parentElement.style.userSelect = 'none')

    // update all polygons to handle click events
    titles.forEach(t => {
        t.parentElement.querySelectorAll('polygon')
            .forEach(p => p.style.pointerEvents = 'all')
    })

    // add click listener for each node
    titles.forEach(t => {
        t.parentElement.addEventListener('click', () => {
            titles.forEach(a => {
                document.querySelectorAll(`.${a.textContent}`)
                    .forEach(e => e.style.display = a === t ? 'block' : 'none')
                a.parentElement.querySelectorAll('polygon')
                    .forEach(e => e.setAttribute('fill', a === t ? 'rgb(200, 240, 255)' : 'none'))
            })
        })
    })

    // call listener for root node
    window.setTimeout(() => {
        titles.forEach(t => {
            if (t.textContent === rootNodeId)
                t.dispatchEvent(new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }))
        })
    }, 100)
}
