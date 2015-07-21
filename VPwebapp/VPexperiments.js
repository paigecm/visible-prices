/******************************************/
/* Helper functions
/******************************************/
String.prototype.format = function () {
  // Using it as a crude templating mechanism, thus:
  // string = "<div><p class='{0}'>I want a {0} of spam eggs and ham {1}<p></div>"
  // string.format("breakfast-order", "right away")
  // -> "<div><p class='breakfast-order'>I want a breakfast-order of spam eggs and ham right away<p></div>"
  var args = arguments;
  return this.replace(/\{(\d+)\}/g, function (m, n) { return args[n]; });
};


function inContext(txtin, offsets){
    var txt = txtin.split('');
    offsets.forEach(function(i){
        var start = i[0];
        var end = i[1];
        txt[start] = "<span class=\"highlight\">" + txtin[start];
        txt[end] = txtin[end] + "</span>";
    });
    
    return txt.join('');
}

function showModalHTML(response){
    $("#modalsink").html("<div>" + response + "</div>");
    $("#modalsink").modal({
        minWidth: 800,
        maxWidth: 1000,
        maxHeight: 650,
        overlayClose:true,
        opacity:80
    });
    $("#localLoader").hide();
};

function showModal(response){
    response = response.replace(/</g, "&lt;");
    response = response.replace(/>/g, "&gt;");
    $("#modalsink").html('<pre>' + response + '</pre>');
    $("#modalsink").modal({
        minWidth: 600,
        maxWidth: 1000,
        maxHeight: 750,
        overlayClose:true,
        opacity:80
    });
    $("#localLoader").hide();
}

function showLocalLoader(obj){
    ot = obj.position().top
    $("#localLoader").css({left: "6px", top: ot + 12}).show()
}


/************************************************/
/* Add a NormalizedValue to the graph if one does
/* not exist for the specified PriceExpression
/************************************************/
function addValue(peURI){
    $.get('./addvalue.html', function(template){
        
        $.ajax({
            type: "get",
            url: "VPexperiments.py",
            data: {'priceExpression': peURI},
            dataType: 'json',
            success: function(json){
                var txt = inContext(json[peURI]['inQuote'], eval(json[peURI]['offsets']));
                showModalHTML(template.format(peURI, txt));
                $("#addValue-button").on("click", function(e){
                    e.preventDefault();
                    normalizedValue = $("#addValue-input input[name='normalizedValue']").val()
                    
                    if (!jQuery.isNumeric(normalizedValue)){
                        alert("please enter an integer or decimal: '20', or '2.5' (for ha'pennies and farthings and suchlike)")
                    
                    } else {
                        $.ajax({
                            type: "get",
                            url: "VPexperiments.py",
                            data: {"peURI": peURI, "addValue": normalizedValue},
                            dataType: 'text',
                            success: function(data){
                                showModal(data)
                            },
                            error: function(jqXHR, textStatus, errorThrown) {
                                console.log(jqXHR.response, textStatus, errorThrown);
                            }
                        });
                    }
               
                    });
                $("#localLoader").hide();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
    });
}

$(document).ready(function() {

    /******************************************/
    /* Populate namedSubjects list on page load
    /******************************************/
        $.ajax({
            type: "get",
            url: "VPexperiments.py",
            data: {'namedSubjects': true},
            dataType: 'json',
            success: function(json){
                for (i in json){
                    $("#subjects").append("<option>" + json[i] + "</option>");
                }        
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }
        });

    /*********************************************/
    /* Populate PriceExpressions list on page load.
    /* Call addValue() to handle result
    /*********************************************/
        $.ajax({
            type: "get",
            url: "VPexperiments.py",
            data: {'getPriceExpressions': true},
            dataType: 'json',
            success: function(json){
                for (q in json){
                    $("#q_pe_list").append("<li>" + q + "&nbsp;&nbsp;&nbsp;<ul></ul>");
                    for (pe in json[q]){
                        $("#q_pe_list li:last-child ul")
                            .append("<li>" + "<a name='addValue'>" + json[q][pe] + "</a>" + "</li>");
                        $("#q_pe_list").append("</li>");

                    };
                };
                
                $("a[name='addValue']").on("click", function(e){
                    showLocalLoader($($(this)));
                    addValue($(this).text());
                }).css({'color':'blue', 'cursor':'pointer'});
       
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
    
    /****************************************************/
    /* show annotation dialog and handle handle result
    /****************************************************/
    $("#NamedSubjectsForm").on("submit", function(e){
        var annotate_target = $("#NamedSubjectsForm select").val();
        $.get('./annote.html', function(template){
            // see above for String.prototype.format use here //
            showModalHTML(template.format(annotate_target));

            $("#dothis").on('click', function(e){
                var target = annotate_target;
                var username = $('#annotation-input input[name=user]').val();
                var comment = $('#annotation-input textarea').val();
                var keywords = $('#annotation-input input[name=keywords]').val();
                
                showLocalLoader($("#annotation-input")); //Fix this!
                
                $.ajax({
                    type: "get",
                    url: "VPexperiments.py",
                    data: {"target": target, "username": username, "comment": comment, "keywords": keywords},
                    dataType: 'json',
                    success: function(data){
                        showModal(data.annotationExists ? data.annotationExists : "serialized annotation triples added to the graph:\n\n" + data.serialized_annotation_triples)
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.log(jqXHR.response, textStatus, errorThrown);
                    }
                });
            });
        });  

        e.preventDefault();

    });


    /*****************************/
    /* SPARQL search
    /*****************************/
    $("#sparqlForm").on("submit", function(e){
        var query = $("#sparqlQuery").setSelection(0, 10000);
        var text = $("#sparqlQuery").getSelection().text;
        var result_format = $("#sparqlForm select").val();
    
        showLocalLoader($(this));

        $.ajax({
            type: "get",
            url: "VPexperiments.py",
            data: {'sparqlQuery': text, 'result_format': result_format},
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
    
        e.preventDefault();
    });
    
    
    /*****************************/
    /* Serialize the graph
    /*****************************/
    $("#serializeForm").on("submit", function(e){
    
        var serialize_format = $("#serializeForm select").val();
    
        showLocalLoader($(this));

        $.ajax({
            type: "get",
            url: "VPexperiments.py",
            data: {'serialize': serialize_format },
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
    
        e.preventDefault();
    });

});
