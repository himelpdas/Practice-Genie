/**
 * Created by Himel on 3/17/2016.
 */

function modalMax() {
    // ensures modal is stretched to maximum viewport height, with proper margins
    modal_body = $(".modal-body");
    if (modal_body.length > 0) {  // modal_body.length sees if element exists http://goo.gl/aydXl
        modal_body.css({"max-height": $(window).height() - $(".modal-body")[0].getBoundingClientRect().top - $(".modal-dialog")[0] .getBoundingClientRect().top});
    }
}

function navbarPad(){
    // prevents navbar-fixed-top from blocking any container content
    $("body").css({
        "padding-top" : $(".navbar").height()
    });
}


$(function () {
    //if ($(".w2p_flash").css("display") == "block"){  // show modal when form has error (since response.flash will show)
    //    $("#object_modal").modal('show');
    //}  // keep this function BEFORE $('.modal').on('shown.bs.modal', modalMax) or else it won't resize properly on error

    $('.modal').on('shown.bs.modal', modalMax);  // run modalMax when modal is shown
    $(window).resize(modalMax);  // when window is resized

    $(window).resize(navbarPad);
    navbarPad();
});