function showInfo(id) {
    document.querySelectorAll(".info").forEach(info => {
        info.computedStyleMap.display = "none";
    });
    document.getElementById(id).style.display = "block"
}
function resetInfo() {

    document.querySelectorAll(".info").forEach(info => {
        info.style.display = "none";
    });


    document.querySelector(".menu-right h2").innerText = "Маълумот навсозӣ шуд";


    setTimeout(() => {
        document.querySelector(".menu-right h2").innerText = "Маълумот";
    }, 1000);
}