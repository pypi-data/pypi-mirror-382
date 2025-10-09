$(document).ready(function () {
    $('.sidenav').sidenav();
    $('.collapsible.expandable').collapsible({
        accordion: false
    });
    $(".d-search-button").click(e => {
        e.preventDefault();
        $("body").addClass("d-search-open");
    });
    $(".d-search-close-button").click(e => {
        e.preventDefault();
        $("body").removeClass("d-search-open");
    });
    if (!$(".d-cool-page-start").length) {
        $('.navbar-fixed').removeClass("d-seamless-cool-page-navbar");
    }
    $(".d-toc-wrapper").pushpin({
        top: 320,
        offset: 64
    })
    $('h1,h2,h3,.scollspy').scrollSpy();
    $('.tabs').tabs({
        swipeable: false,
        duration: 150
    });
    $('.mkdocs-ezglossary-link').addClass("tooltipped");
    $('.mkdocs-ezglossary-link').each((i, obj) => {
        obj = $(obj);
        obj.attr("data-tooltip", obj.attr("title"));
        obj.attr("title", null);
    });
    $('.tooltipped').tooltip();
    $(".d-secondary-collapsible").each((i, obj) => {
        const header = $(obj).children(".d-secondary-collapsible-header");
        const content = $(obj).children(".d-secondary-collapsible-content");
        $(header).click(() => {
            $(obj).toggleClass("d-active");
        })
    })
});

$(document).scroll(function () {
    $('.navbar-fixed').removeClass("no-transition");
    if ($(document).scrollTop() >= 180 && $(".d-cool-page-start").length) {
        $('.navbar-fixed').removeClass("d-no-text-cool-page-navbar");
    } else {
        $('.navbar-fixed').addClass("d-no-text-cool-page-navbar");
    }
    if ($(document).scrollTop() >= 240 && $(".d-cool-page-start").length) {
        $('.navbar-fixed').removeClass("d-seamless-cool-page-navbar");
    } else {
        $('.navbar-fixed').addClass("d-seamless-cool-page-navbar");
    }
});
