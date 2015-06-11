function showModal(response){
    response = response.replace(/</g, "&lt;");
    response = response.replace(/>/g, "&gt;");
    $("#modalsink").html('<pre>' + response + '</pre>');
    $("#modalsink").modal({
        minWidth: 600,
        maxWidth: 1000,
        maxHeight: 450,
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

    /*****************************/
    /* SPARQL search
    /*****************************/
    $("#sparqlForm").on("submit", function(e){
        var query = $("#sparqlQuery").setSelection(0, 10000);
        var text = $("#sparqlQuery").getSelection().text;
        var result_format = $("#sparqlForm select").val();
    
        console.log(text, query, result_format);
    
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
    
        return false;
    });
    
    
    /*****************************/
    /* serialize the graph
    /*****************************/
    $("#serializeForm").on("submit", function(e){
    
        var serialize_format = $("#serializeForm select").val();
    
        showLocalLoader($(this));

        $.ajax({
            type: "get",
            url: "VPexperiments.py",
            data: {'serialize': true, 'serialize_format': serialize_format },
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
    
        return false;
    });

});