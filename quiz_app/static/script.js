function updateProgress() {
    let total = document.querySelectorAll(".question-card").length;
    let answered = document.querySelectorAll("input[type=radio]:checked").length;
    let percent = (answered / total) * 100;
    document.getElementById("progress-bar").style.width = percent + "%";
}
