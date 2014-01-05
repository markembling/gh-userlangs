(function($){

    "use strict";

    // Get an appropriate loading phrase
    function chooseLoadingPhrase() {
        var phrases = [
            "stroking the octocat",
            "warming up the toaster",
            "communing with the spirit world",
            "instructing the minions",
            "hailing Starfleet Command",
            "worrying the sheep",
            "feeding the octocat"
        ];
        var rand = Math.floor(Math.random() * phrases.length);
        return phrases[rand];
    };

    // Clever little function (modified a bit) thanks to ThomasR at 
    // http://codeaid.net/javascript/convert-size-in-bytes-to-human-readable-format-(javascript)
    function bytesToSize(bytes) {
        var sizes = ['', 'KB', 'MB', 'GB', 'TB'];
        var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
    };

    // Splits the data into two sets ('main' and 'other') and adds labels.
    function splitData(rawData) {
        var main = [];
        var other = [];
        var otherValue = 0;
        var otherPercent = 0;

        $.each(rawData, function(i, v) {
            v["label"] = i;
            if (v["percent"] >= 0.5) {
                main.push(v);
            } else {
                other.push(v);
                otherValue += v["bytes"]
                otherPercent += v["percent"]
            }
        });

        main.push({ label: "Other", bytes: otherValue, percent: otherPercent });

        return { main: main, other: other };
    };

    // Loops over the data and adds a 'color' field.
    function generateColours(data, dull, finalGrey) {
        var total = Object.keys(data).length;

        var i = 300 / (total - 1);
        if (finalGrey) i = 320 / (total - 2);

        var coloured = $.map(data, function(v, idx) {
            if (finalGrey && idx == total - 1) {
                v["color"] = "#888";
            } else {
                // Generate the colour
                var h = i * idx;
                var colour = "hsl(" + h + ", 45%, 55%)";
                if (dull) colour = "hsl(" + h + ", 30%, 60%)";
                v["color"] = colour;
            }

            return v;
        });

        return coloured;
    };

    // Takes a data set and tweaks it to render a chart.
    function dataToGraphData(data) {
        return $.map(data, function(v) {
            return { value: v["bytes"], color: v["color"] };
        });
    };

    function updateSubtitle(username, repoCount) {
        var subtitle = username + " (" + repoCount;
        if (repoCount == 1) {
            subtitle += " repository)";
        } else {
            subtitle += " repositories)";
        }
        $('#subtitle').text(subtitle);
    }

    // Render the overall table containing all languages.
    function renderOverallTable(data) {
        for (var key in data) {
            var vals = data[key];


            var $tbody = $('#overall tbody');

            var $row = $("<tr></tr>");
            $row.append("<td>" + key + "</td>")
                .append("<td>" + vals["percent"].toFixed(3) + "%</td>")
                .append("<td>" + bytesToSize(vals["bytes"]) + "</td>")
                .append('<td><span class="tip" data-toggle="tooltip" title="' + vals["repos"].join(",<br>") + '">' + 
                    vals["repos"].length + (vals["repos"].length == 1 ? " repository" : " repositories") + 
                    "</span></td>")

            $tbody.append($row);

            $('.tip').tooltip({html: true});
        }
    };

    // Render a chart
    function renderGraph(data, $pie, $legend) {
        var ctx = $pie.get(0).getContext("2d");

        var opts = {
            segmentStrokeWidth: 1,
            percentageInnerCutout: 40,
            animateRotate: false
        };
        var graphData = dataToGraphData(data);
        var pie = new Chart(ctx).Doughnut(graphData, opts);

        // Legend
        $.each(data, function(i, v) {
            var $tbody = $legend.find('tbody');

            var $row = $("<tr></tr>");
            var $swatchCell = $("<td></td>");
            $swatchCell.css('background-color', v["color"])
                       .width(60)
            $row.append($swatchCell)
                .append("<td>" + v["label"] + "</td>")
                .append("<td>" + v["percent"].toFixed(3)+ "%</td>")
                .append("<td>" + bytesToSize(v["bytes"]) + "</td>")

            $tbody.append($row);
        });
    };

    function message(text) {
        var $warn = $('<div class="alert alert-warning"></div>');
        $warn.html(text);
        $warn.prepend('<a class="close" data-dismiss="alert" href="#" aria-hidden="true">&times;</a>');
        $(".page-header").after($warn);
    };

    function update() {
        $('#loading-phrase').text(chooseLoadingPhrase());
        $('#loading').show();
        $('#main-content').hide();

        $.getJSON("data")
            .done(function(d) {
                $('#main-content').show();

                updateSubtitle(d["user"], d["repo_count"]);

                renderOverallTable(d["langs"]);

                var graphData = splitData(d["langs"]);
                var mainColoured = generateColours(graphData.main, false, true);
                renderGraph(mainColoured, $('#pie'), $('#legend'));
                if (graphData.other.length > 0) {
                    var otherColoured = generateColours(graphData.other, true, false);
                    renderGraph(otherColoured, $('#pie-other'), $('#legend-other'));
                    $('#other').show();
                };
            })
            .fail(function(jqXHR) {
                var statusCode = jqXHR.status;
                if (statusCode == 500) {
                    message("The server encountered an error. Please try again later.");
                } else if (statusCode == 403) {
                    message('You do not appear to be authorized (' + 
                        jQuery.parseJSON(jqXHR.responseText).error + 
                        '). You may need to try <a href="intro">logging in and authorizing again</a>.');
                }
            })
            .always(function() {
                $('#loading').hide();
            });
    };

    // Main
    $(function() {

        update();

    });

}(jQuery));
