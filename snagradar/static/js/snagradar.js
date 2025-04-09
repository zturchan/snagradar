var loadFile = function (event) {
  var output = document.getElementById('preview');
  output.src = URL.createObjectURL(event.target.files[0]);
  output.onload = function () {
    URL.revokeObjectURL(output.src) // free memory
  }
}

$(document).ready(function () {
  
  $(document).on("click", ".clear-button", function(){
    $("form#form input, select").each(function(){
      $(this).val("");
    });
    $("#preview").attr("src", "");
  });

  $("form#form").submit(function (e) {
    e.preventDefault();
    $('#snag-error').hide();
    $('#snag-info').hide();
    $('#snag-warning').hide();
    var formData = new FormData(this);
    $('.scan-spinner').addClass("active");

    // When using the FormData constructor, selects are not picked up so we need to add them
    $("form#form select").each(function(){
        var $select = $(this);
        formData.append($select.attr('name'), $select.val());
    });


    $.ajax({
      url: $(this).attr("action"),
      type: 'POST',
      data: formData,
      error: function(error){
        if (error.responseJSON){
          $('#error-text').text(error.responseJSON.description);
          $('#snag-error').show();
        } else {
          $('#error-text').text("An undefined server error occurred.");
          $('#snag-error').show();
        }
        $('.scan-spinner').removeClass("active");
      },
      success: function (pokemon) {
        $('.scan-spinner').removeClass("active");
        $("#hp-stat").val(pokemon['hp']);
        $("#atk-stat").val(pokemon['atk']);
        $("#defense-stat").val(pokemon['defense']);
        $("#spatk-stat").val(pokemon['spatk']);
        $("#spdef-stat").val(pokemon['spdef']);
        $("#speed-stat").val(pokemon['speed']);
        $("#evs_total").text(pokemon.evs_total);
        $("#evs_hp").text(pokemon.evs_hp);
        $("#evs_atk").text(pokemon.evs_atk);
        $("#evs_defense").text(pokemon.evs_defense);
        $("#evs_spatk").text(pokemon.evs_spatk);
        $("#evs_spdef").text(pokemon.evs_spdef);
        $("#evs_speed").text(pokemon.evs_speed);        
        $("#pokemon-select").val(pokemon.name).change();
        $("#nature").val(pokemon.nature).change();
        $("#lvl").val(pokemon.lvl).change();
        if (pokemon.msg != null && pokemon.msg.length > 0){
          $('#warning-text').text(pokemon.msg);
          $('#snag-warning').show();
        }
        $('#info-text').text(pokemon.msg);
        $('#snag-info').show();
        setTimeout(() => {
          $('#snag-info').hide();
        }, 5000);
      },
      cache: false,
      contentType: false,
      processData: false
  });
  });
});
