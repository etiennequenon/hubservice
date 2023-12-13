document.getElementById('nextBtn').addEventListener('click', function() {
    scrollVitrine("next");
});

document.getElementById('prevBtn').addEventListener('click', function() {
    scrollVitrine("prev");
});

function scrollVitrine(direction) {
    const vitrine = document.querySelector('.vitrine');
    const itemWidth = vitrine.querySelector('.item').clientWidth;
    const scrollAmount = direction === "next" ? itemWidth : -itemWidth;

    vitrine.scrollLeft += scrollAmount;
}
