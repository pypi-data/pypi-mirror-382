let alias = jQuery.noConflict();

var site_theme = (localStorage.getItem('theme') != null)
    ? localStorage.getItem('theme')
    : 'light';

var site_font = (localStorage.getItem('font') != null)
    ? localStorage.getItem('font')
    : 'normal';

function toggle_theme(_theme) {
    if (_theme === "dark") {
        alias('body').attr("data-bs-theme", "dark")
        alias('#btn-theme').html("<i class=\"bi bi-sun-fill\"></i>")
        alias('#btn-theme').attr("onclick", "toggle_theme('light')")
        alias('#source-code-css').attr("href", "https://github.coventry.ac.uk/pages/ab6459/CUEH_Slides/js/custom/styles/atom-one-dark.css")

        alias('.slide-background .title-slide .slide-background-content').each(function() {
            let bgImage = alias(this).css("background-image");
            if (bgImage) {
                let newBgImage = bgImage.replace("light", "dark");
                alias(this).css("background-image", newBgImage);
            }
        })

    } else {
        alias('body').attr("data-bs-theme", "light")
        alias('#btn-theme').html("<i class=\"bi bi-moon-stars-fill\"></i>")
        alias('#btn-theme').attr("onclick", "toggle_theme('dark')")
        alias('#source-code-css').attr("href", "https://github.coventry.ac.uk/pages/ab6459/CUEH_Slides/js/custom/styles/atom-one-light.css")

        alias('.slide-background .title-slide .slide-background-content').each(function() {
            let bgImage = alias(this).css("background-image");
            if (bgImage) {
                let newBgImage = bgImage.replace("dark", "light");
                alias(this).css("background-image", newBgImage);
            }
        })


    }
    localStorage.setItem('theme', _theme);
}

function toggle_font(_font) {
    if (_font === "comic-sans") {
        alias('#btn-font').attr("onclick", "toggle_font('normal')")
        alias('#chosen-font').attr("href", "https://fonts.googleapis.com/css2?family=Comic+Neue:ital,wght@0,300;0,400;0,700;1,300;1,400;1,700&display=swap")
        alias('body').addClass('comic-sans')
        alias('body').removeClass('ubuntu')
        console.log("comic-sans")
    } else {

        alias('#btn-font').attr("onclick", "toggle_font('comic-sans')")
        alias('#chosen-font').attr("href", "https://fonts.googleapis.com/css2?family=Ubuntu+Sans:ital,wght@0,100..800;1,100..800&display=swap")
        alias('body').addClass('ubuntu')
        alias('body').removeClass('comic-sans')
        console.log("normal")
    }
    localStorage.setItem('font', _font);
}

alias(document).ready(function () {
    toggle_theme(site_theme)
    toggle_font(site_font)
})
