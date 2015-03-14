/**
 * Touch api graceful degradation
 */
function setupTouch() {
    if (!("ontouchstart" in document.documentElement)){
        document.documentElement.className += " no-touch";
    } else {
        $(".oe_detect_touches").click(function() {
            $(this).toggleClass("oe_touched");
        });
    }
}

/**
 * adds custom events for optimizely and google analytics 
 */
function setupStats() {
    window.optimizely = window.optimizely || [];
    window._gaq = window._gaq || [];

    function track(event){
        optimizely.push(['trackEvent',event]);
        _gaq.push(['_trackEvent','InteractionEvents',event]);
    }

    // all elements with a ab_EVENT class will emit EVENT to g.a. and opt. when clicked
    $('[class^=ab]').on('mousedown',function(event){
        _.each(this.className.split(' '),function(klass){
            var ab = klass.indexOf('ab_');
            if(ab >= 0){ 
                track(klass.slice(ab+3));
            }
        });
    });

    // scroll events to track scroll behaviour. It tracks how far the visitor has scrolled
    // on the current page. 
    var scrolled     = false;
    var scrolled_25  = false;
    var scrolled_50  = false;
    var scrolled_75  = false;
    var scrolled_100 = false;

    $(window).scroll(function(event){
        var prog = (scrollY + innerHeight) / document.height;
        if(!scrolled){
            scrolled = true; 
            track('scroll');
        }
        if(!scrolled_25 && prog >= 0.25){
            scrolled_25 = true;
            track('scroll_25');
        }
        if(!scrolled_50 && prog >= 0.5){
            scrolled_50 = true;
            track('scroll_50');
        }
        if(!scrolled_75 && prog >= 0.75){
            scrolled_75 = true;
            track('scroll_75');
        }
        if(!scrolled_100 && prog >= 0.99){
            scrolled_100 = true;
            track('scroll_100');
        }
    });
}

/**
 * Parse query string
 */
function getQueryParams(qs) {
    var params = {}, tokens,
        qs = qs.replace('+', ' '),
        re = /[?#&]?([^=]+)=([^&]*)/g;
    while ((tokens = re.exec(qs))) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }
    return params;
}

/**
 * Set location to hash out of a dict
 */
function hashLocation(hash_dict) {
    var hash = '#' + _.map(hash_dict, function(v, k) {
        return k + '=' + encodeURIComponent(v);
    }).join('&');
    window.location.hash = hash;
}

/**
 * Script used in event page
 */
function setupEvents() {
    var user_country = 'BE';

    var hashChange = function() {
        var hash = getQueryParams(window.location.hash);
        var training = (hash.view === 'training');
        var online = (hash.category === 'online');
        if (training) {
            hash.category = 'training';
        }
        if (hash.country && hash.category == 'online') {
            hash.country = '';
            hashLocation(hash);
            return;
        }
        if (!('country' in hash)) {
            hash.country = user_country;
            hashLocation(hash);
            return;
        }
        $('.oe_filters .oe_input[name=category]').toggle(!training);
        $('.oe_filters .oe_input[name=online]')
            .prop('checked', hash.online != 'false')
            .parent().toggleClass('oe_hidden', !training);
        $('.oe_filters .oe_input[name=country]').toggle(!online);
        $('.oe_event_main_title').toggle(!training);
        $('.oe_event_trainings_title').toggle(training);

        $('.oe_event_list tr').show();
        ['organizer', 'country', 'category'].forEach(function(facet) {
            var value = hash[facet];
            if (value) {
                $('.oe_input[name=' + facet + ']').val(value);
                $('.oe_event_list tr:not([data-' + facet + '~="' + value + '"])').hide();
            } else {
                $('.oe_input[name=' + facet + ']')[0].selectedIndex = 0;
            }
        });

        if (training && $('.oe_input[name=online]').is(':checked')) {
            $('.oe_event_list tr[data-country=""][data-category~="training"]').show();
        }
    };

    $('.oe_filters .oe_input').on('change', function() {
        var hash = getQueryParams(window.location.hash);
        var name = $(this).attr('name');
        hash[name] = $(this).val();
        if (name == 'online') {
            hash[name] = '' + this.checked;
        }
        hashLocation(hash);
    });

    //$(window).on('hashchange', hashChange);
    var prevHash = window.location.hash;
    window.setInterval(function () {
        if (window.location.hash != prevHash) {
            prevHash = window.location.hash;
            hashChange();
        }
    }, 100);
    getCountryCode().then(function(country) {
        if ($('select[name=country] option[value=' + country + ']').length) {
            user_country = country;
        }
        hashChange();
    });
}

function getCountryCode() {
    return $.get("/get_country");
}

$(function() {
    setupTouch();
    setupStats();
});

// vim:fdn=1:
