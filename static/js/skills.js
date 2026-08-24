document.addEventListener("DOMContentLoaded", () => {

    const checkboxes = document.querySelectorAll(
        '.skill-card input[type="checkbox"]'
    );

    const selectedCount =
        document.getElementById("selectedCount");


    function updateCount() {

        const count = document.querySelectorAll(
            '.skill-card input[type="checkbox"]:checked'
        ).length;

        selectedCount.textContent = count;
    }


    checkboxes.forEach((checkbox) => {

        checkbox.addEventListener(
            "change",
            updateCount
        );

    });


    updateCount();

});