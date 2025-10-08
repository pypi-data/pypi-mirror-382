jQuery(document).ready(function ($) {
    $(".collapse").on("shown.bs.collapse", function () {
        localStorage.setItem("coll_" + this.id, true);
    });

    $(".collapse").on("hidden.bs.collapse", function () {
        localStorage.removeItem("coll_" + this.id);
    });

    $(".collapse").each(function () {
        if (localStorage.getItem("coll_" + this.id) === "true") {
            $(this).collapse("show");
        } else {
            $(this).collapse("hide");
        }
    });

    var urlSplit = $(location).attr('href').split('/');
    let regex = /[A-Za-z0-9]+_/i;
    let page = null;
    for (var index in urlSplit) {
        if (regex.test(urlSplit[index])) {
            page = urlSplit[index].split('_')[0];
        }
    }

    $('[id*="task"]').on('click', function () {
        if (this.open) {
            localStorage.removeItem(page + "activity_coll_" + this.id);
        } else {
            localStorage.setItem(page + "activity_coll_" + this.id, true);
        }
    })

    $('[id*="task"]').each(function () {
        if (localStorage.getItem(page + "activity_coll_" + this.id) === "true") {
            $(this).attr('open', true);
        } else {
            $(this).attr('open', false);
        }
    })

});