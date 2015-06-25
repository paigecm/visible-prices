String.prototype.format = function () {
  // Using it as a crude templating mechanism, thus:
  // string = "<div><p class='{0}'>I want a {0} of spam eggs and ham {1}<p></div>"
  // string.format("breakfast-order", "right away")
  // -> "<div><p class='breakfast-order'>I want a breakfast-order of spam eggs and ham right away<p></div>"
  var args = arguments;
  return this.replace(/\{(\d+)\}/g, function (m, n) { return args[n]; });
};

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
json = ""
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