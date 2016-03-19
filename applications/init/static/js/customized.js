/**
 * Created by Himel on 3/17/2016.
 */

function modalMax() {
    // ensures modal is stretched to maximum viewport height, with proper margins
    $(".modal-body").css({"max-height": $(window).height() - $(".modal-body").offset().top - $(".modal-dialog").offset().top - 7});
}

$(function () {
    $('.modal').on('shown.bs.modal', modalMax);  // run modalMax when modal is shown
    $(window).resize(modalMax);  // when window is resized
});