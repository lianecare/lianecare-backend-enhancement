/* Toast */
$.toastDefaults = {
    position: 'top-right',
    /** top-left/top-right/top-center/bottom-left/bottom-right/bottom-center - Where the toast will show up **/
    dismissible: true,
    /** true/false - If you want to show the button to dismiss the toast manually **/
    stackable: true,
    /** true/false - If you want the toasts to be stackable **/
    pauseDelayOnHover: true,
    /** true/false - If you want to pause the delay of toast when hovering over the toast **/
    style: {
        toast: '', /** Classes you want to apply separated my a space to each created toast element (.toast) **/
        info: '', /** Classes you want to apply separated my a space to modify the "info" type style  **/
        success: '', /** Classes you want to apply separated my a space to modify the "success" type style  **/
        warning: '', /** Classes you want to apply separated my a space to modify the "warning" type style  **/
        error: '', /** Classes you want to apply separated my a space to modify the "error" type style  **/
    }
};

function fixFooter() {
    var footerHeight = $("footer").outerHeight(true);
    var headerHeight = $("#site-header").outerHeight(true);
    var windowHeight = $(window).outerHeight(true);
    var minHeight = windowHeight - footerHeight - headerHeight;
    $("#main").css("minHeight", minHeight);
}

const wait = document.querySelector('#wait');
function startLoading() {
    wait.classList.add("display");
    setTimeout(()=>{
        wait.classList.remove("display");
    }, 5000);
}

function hideLoading() {
    wait.classList.remove("display");
}

function initAutocomplete(id_address, id_lat, id_lng, id_house_no, id_postcode, id_city, id_region, id_country){
    if(!GMAPS_INIT_DONE || !google){
        //Wait SDK download
        setTimeout(
            ()=>initAutocomplete(id_address, id_lat, id_lng, id_house_no, id_postcode, id_city, id_region, id_country),
            60
        );
        return;
    }

    let address1Field = document.querySelector(id_address);

    // Create the autocomplete object, restricting the search predictions to
    // addresses in the US and Canada.
    let autocomplete = new google.maps.places.Autocomplete(address1Field, {
        componentRestrictions: { country: ["it"] },
        fields: ["address_components", "geometry"],
        types: ["address"],
    });
    // When the user selects an address from the drop-down, populate the
    // address fields in the form.
    autocomplete.addListener("place_changed", function() {
        let address = "";
        let house_no = "";
        let postal_code = "";
        let city = "";
        let region = "";
        let country = "";

        // Get the place details from the autocomplete object.
        const place = autocomplete.getPlace();

        // Get each component of the address from the place details,
        // and then fill-in the corresponding field on the form.
        // place.address_components are google.maps.GeocoderAddressComponent objects
        // which are documented at http://goo.gle/3l5i5Mr
        for (const component of place.address_components) {
            const componentType = component.types[0];

            switch (componentType) {
                case "route":
                    address = component.long_name || ''
                    break;

                case "street_number":
                    house_no = component.long_name || '';
                    break;


                case "postal_code":
                    postal_code = component.long_name || '';
                    break;


                case "locality":
                    city = component.long_name || '';
                    break;

                case "administrative_area_level_1": {
                    region = component.short_name || '';
                    break;
                }

                case "country":
                    country = component.long_name || '';
                    break;
            }
        }

        document.querySelector(id_lat).value = place.geometry.location.lat();
        document.querySelector(id_lng).value = place.geometry.location.lng();
        document.querySelector(id_house_no).value = house_no;
        if (postal_code == ""){
            document.querySelector(id_postcode).value = 'na';
        }
        else{
            document.querySelector(id_postcode).value = postal_code;
        }

        document.querySelector(id_city).value = city;
        document.querySelector(id_region).value = region;
        document.querySelector(id_country).value = country;

        document.querySelector(id_address).value = `${address} ${house_no}, ${postal_code} ${city}, ${region}, ${country}`;
        $(id_address).valid();

    });
}

/* Project specific Javascript goes here. */
$(document).ready(function () {
    fixFooter();

    $('[data-toggle="tooltip"]').tooltip(); // Tooltip inizialize

    // Check the age of majority
    jQuery.validator.addMethod("minAge", function (value, element, min) {
        var today = new Date();

        var dateParts = value.split("/");
        var birthDate = new Date(+dateParts[2], dateParts[1] - 1, +dateParts[0]);

        /*var dateParts = value.split("-");
        var birthDate = new Date(+dateParts[0], dateParts[1] - 1, +dateParts[2]);*/

        var age = today.getFullYear() - birthDate.getFullYear();
        if (age > min + 1) {
            return true;
        }
        var m = today.getMonth() - birthDate.getMonth();

        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age >= min;
    }, "Non sei maturo abbastanza!");

    // Check address
    jQuery.validator.addMethod("check_address", function (value, element) {
        return this.optional(element) || $('#id_postcode').val() !== '' || $('#id_city').val() !== '';
    }, "Inserisci un indirizzo valido");


    // Password
    jQuery.validator.addMethod("check_password", function (value, element) {
        return this.optional(element) || /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,16}$/i.test(value);
    }, "Tra gli 8 e i 16 caratteri con almeno una lettera maiuscola, minuscola ed un carattere numerico.");
});

