/**
 * Created by Himel on 3/17/2016.
 */

function modalMax() {
    // ensures modal is stretched to maximum viewport height, with proper margins
    $(".modal-body").css({"max-height": $(window).height() - $(".modal-body").offset().top - $(".modal-dialog").offset().top - 0});
}

$(function () {
    if ($(".w2p_flash").css("display") == "block"){  // show modal when form has error (since response.flash will show)
        $("#add_referral_modal").modal('show');
    }  // keep this function BEFORE $('.modal').on('shown.bs.modal', modalMax) or else it won't resize properly on error

    $('.modal').on('shown.bs.modal', modalMax);  // run modalMax when modal is shown
    $(window).resize(modalMax);  // when window is resized
});